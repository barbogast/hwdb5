#!/usr/bin/env python

import argparse
import json
from collections import OrderedDict
from operator import itemgetter, methodcaller

from bulbs.rexster import Graph, Config
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from flask import Flask, render_template_string, jsonify, request
from flaskext.htmlbuilder import html as H
from flask_debugtoolbar import DebugToolbarExtension

import treetools


class BaseNode(Node):
    __mode__ = 'STRICT'

class LabeledNode(BaseNode):
    note = String(nullable=True)
    label = String(nullable=False)

    def __unicode__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.label)


class RootPart(BaseNode):
    element_type = 'root_part'

class Part(LabeledNode):
    element_type = "part"

class Connector(LabeledNode):
    element_type = "connector"

class RootConnector(BaseNode):
    element_type = 'root_connector'

class Connection(BaseNode):
    element_type = "part_connection"
    quantity = Integer()

class ConnectionRoot(BaseNode):
    element_type = "connection_root"

class RootStandard(BaseNode):
    element_type = 'root_standard'

class Standard(LabeledNode):
    element_type = "standard"

class AttrType(LabeledNode):
    element_type = "attr_type"

class Company(LabeledNode):
    element_type = "company"

class Unit(LabeledNode):
    element_type = "unit"
    name = String(nullable=False)
    format = String(nullable=False)

class Attribute(BaseNode):
    element_type = "attribute"
    value = String(nullable=False)


class IsA(Relationship): label = "is_a"
class BelongsTo(Relationship): label = "belongs_to"
class ConnectedVia(Relationship): label = "connected_via"
class ConnectedFrom(Relationship): label = "connected_from"
class ConnectedTo(Relationship): label = "connected_to"
class Implements(Relationship): label = "implements"
class IsUnit(Relationship): label = "is_unit"
class HasAttrType(Relationship): label = "has_attr_type"
class HasAttribute(Relationship): label = "has_attribute"
class HasConnector(Relationship):
    label = 'has_connector'
    quantity = Integer(nullable=False)


relationships = (
    (Standard,      IsA,            Standard),
    (Standard,      IsA,            RootStandard),
    (Connector,     IsA,            Connector),
    (Connector,     IsA,            RootConnector),
    (Part,          IsA,            Part),
    (Part,          IsA,            RootPart),
    (Part,          IsA,            ConnectionRoot),
    (Part,          HasConnector,   Connector),
    (Part,          Implements,     Standard),
    (Part,          HasAttribute,   Attribute),
    (Part,          HasAttrType,    AttrType,),
    (Connection,    BelongsTo,      Part),
    (Connection,    ConnectedVia,   Connector),
    (Connection,    ConnectedFrom,  Part),
    (Connection,    ConnectedTo,    Part),
    (AttrType,      HasAttrType,    AttrType),
    (AttrType,      IsUnit,         Unit),
)


g = None
def init_graph():
    config = Config('http://localhost:8182/graphs/hwdbgraph')
    g = Graph(config)
    g.add_proxy("root_parts", RootPart)
    g.add_proxy("parts", Part)
    g.add_proxy("root_standards", RootStandard)
    g.add_proxy("standards", Standard)
    g.add_proxy("connections", Connection)
    g.add_proxy("attr_types", AttrType)
    g.add_proxy("companies", Company)
    g.add_proxy("units", Unit)
    g.add_proxy("attributes", Attribute)
    g.add_proxy("root_connectors", RootConnector)
    g.add_proxy("connectors", Connector)
    g.add_proxy("connections", Connection)
    g.add_proxy("connection_roots", ConnectionRoot)


    for node_from, rel, node_to in relationships:
        g.add_proxy(rel.label, rel)
    return g


def load_units():
    import data
    for unit in data.units:
        d = {
            'name': unit.pop('label'),
            'label': unit.pop('name'),
            'format': unit.pop('format', '%(unit)s'),
            'note': unit.pop('note', None),
        }
        assert not unit
        g.units.create(**d)


def load_attr_types():
    import data
    for attr_type in data.attr_types:
        (unit,) = list(g.units.index.lookup(label=attr_type.pop('unit')))
        attr_type['label'] = attr_type.pop('name')
        attr_type_obj = g.attr_types.create(**attr_type)
        g.is_unit.create(attr_type_obj, unit)


def _add_element(el_dict, parent_el, element_type, root_element_node):
    assert 'attr_types' not in el_dict, 'attr_types should be on the first level elements of the part tree (or should they?)'
    d = {
        'label': el_dict.pop('<name>'),
        'note': el_dict.pop('<note>', None),
    }
    el = element_type.create(**d)

    if parent_el is None:
        g.is_a.create(el, root_element_node)
    else:
        g.is_a.create(el, parent_el)

    for attr_type_name in el_dict.pop('<attr_types>', []):
        (attr_type,) = g.attr_types.index.lookup(label=attr_type_name)
        g.has_attr_type.create(el, attr_type)

    for attr_type_name, attr_value in el_dict.pop('<attrs>', {}).iteritems():
        attribute = g.attributes.create(value=attr_value)
        (attr_type,) = g.attr_types.index.lookup(label=attr_type_name)
        g.has_attr_type.create(attribute, attr_type)
        g.has_attribute.create(el, attribute)

    for standard_name in el_dict.pop('<standards>', []):
        (standard,) = g.standards.index.lookup(label=standard_name)
        g.implements.create(el, standard)

    for child_el_dict in el_dict.pop('<children>', []):
        _add_element(child_el_dict, el, element_type, root_element_node)

    assert not el_dict, el_dict


def load_root_parts():
    import data
    (root_part,) = g.root_parts.get_all()
    parts = treetools.inflate_tree(data.parts)
    for part_dict in parts:
        _add_element(part_dict, None, g.parts, root_part)


def load_standard():
    import data
    (root_standard,) = g.root_standards.get_all()
    standards = treetools.inflate_tree(data.standards)
    for standard_dict in standards:
        _add_element(standard_dict, None, g.standards, root_standard)


def load_connectors():
    import data
    (root_connector,) = g.root_connectors.get_all()
    connectors = treetools.inflate_tree(data.connectors)
    for connector_dict in connectors:
        _add_element(connector_dict, None, g.connectors, root_connector)


def load_sub_parts():
    import data
    parts = treetools.inflate_tree(data.subparts)

    for part_dict in parts:
        (part,) = g.parts.index.lookup(label=part_dict.pop('<name>'))
        for child_part_dict in part_dict.pop('<children>'):
            _add_element(child_part_dict, part, g.parts, None)

        assert not part_dict, part_dict


def load_connections():
    def _create_connection(system_part, parent_part, child_dict, connector):
        (child_part,) = g.parts.index.lookup(label=child_dict.pop('<name>'))
        connection = g.connections.create(quantity=child_dict.pop('<quantity>', 1))
        g.belongs_to.create(connection, system_part)
        g.connected_from.create(parent_part, connection)
        g.connected_to.create(connection, child_part)
        if connector:
            g.connected_via.create(connection, connector)

        _add_connection(system_part, child_part, child_dict)
        assert not child_dict, child_dict


    def _add_connection(system_part, parent_part, part_dict):
        for child_dict in part_dict.pop('<no_connector>', []):
            _create_connection(system_part, parent_part, child_dict, None)

        for conn_dict in part_dict.pop('<connectors>', []):
            (connector,) = g.connectors.index.lookup(label=conn_dict.pop('<name>'))
            g.has_connector.create(parent_part, connector, quantity=conn_dict.pop('<quantity>', 1))
            for child_dict in conn_dict.pop('<children>', []):
                _create_connection(system_part, parent_part, child_dict, connector)

        assert not part_dict, part_dict


    import data
    systems = treetools.inflate_tree(data.systems)
    (connection_root,) = g.connection_roots.get_all()
    for system_dict in systems:
        (system_part,) = g.parts.index.lookup(label=system_dict.pop('<name>'))
        g.is_a.create(system_part, connection_root)
        _add_connection(system_part, system_part, system_dict)
        assert not system_dict, system_dict



base_template = '''
{% extends "base.html" %}
{% block body %}
    <script type="text/javascript">
        $(function(){
            $("#tree").dynatree({
                persist: true,
                initAjax: {
                    url: "{{json_url}}",
                    postProcess: function(data, dataType){
                        // flask.jsonify denies sending json with an array as root
                        // for security reasons. so we unwrap it here
                        return data.children
                    },
                },
            });
        });
    </script>

  <div class="container">
    <h1>{{heading}}</h1>
    {{content}}
  </div>
{% endblock %}'''

menu_items = OrderedDict([
    ('/parts', 'Parts'),
    #('/attr_types', 'Attribute Types'),
    #('/attributes', 'Attributes'),
    ('/units', 'Units'),
    ('/connections', 'Connections'),
    ('/standards', 'Standards'),
    ('/connectors', 'Connectors'),
])

def _render_string(tmpl_str, **kwargs):
    """ Adds common template arguments """
    return render_template_string(tmpl_str, menu_items=menu_items, **kwargs)


app = Flask(__name__)

@app.route('/units')
def units_view():
    unit_html = []
    for unit in g.units.get_all():
        unit_html.append(H.li(unit.name, ' [%s]'%unit.label))
    return _render_string(base_template, heading='Units', content=H.ul(unit_html))


@app.route('/parts')
def parts_view():
     return _render_string(base_template,
                           heading='Parts',
                           content=H.div(id='tree'),
                           json_url='json?type=parts')


@app.route('/standards')
def standards_view():
    return _render_string(base_template,
                          heading='Standards',
                          content=H.div(id='tree'),
                          json_url='json?type=standards')


@app.route('/connectors')
def connectors_view():
    return _render_string(base_template,
                          heading='Standards',
                          content=H.div(id='tree'),
                          json_url='json?type=connectors')


@app.route('/connections')
def connections_view():
    return _render_string(base_template,
                          heading='connections',
                          content=H.div(id='tree'),
                          json_url='json?type=connections')

def _NTL(v):
    """ NoneToList: Convert None into [] """
    return [] if v is None else v


def _get_connections_json():
    def _get_connections_for_part(part):
        # key=connecor.eid, value=list_of_connector_dicts
        connectors = {}

        # list of dicts
        without_connectors = []

        # get all connectors that his part has
        for has_connector in _NTL(part.outE('has_connector')):
            connector = has_connector.inV()
            connectors[connector.eid] = []
            for i in xrange(has_connector.quantity):
                connector_dict = {'title': connector.label, 'isFolder': True, 'children': []}
                connectors[connector.eid].append(connector_dict)

        # get connected parts
        for connected_from in _NTL(part.outE('connected_from')):
            connection = connected_from.inV()

            # check if the connection has a connector
            connected_vias = connection.outE('connected_via')
            if connected_vias:
                (connected_via,) = connected_vias
                connector_eid = connected_via.inV().eid
            else:
                connector_eid = None

            # get the connected part
            (connected_to,) = connection.outE('connected_to')
            childpart = connected_to.inV()
            child_dict = {'title': childpart.label,
                          'children': _get_connections_for_part(childpart)}

            if connector_eid is None:
                without_connectors.append(child_dict)
            else:
                # associate each connected part with one connector
                for i in xrange(connection.quantity):
                    for connector in connectors[connector_eid]:
                        if not connector['children']:
                            connector['children'].append(child_dict)
                            break
                    else:
                        raise Exception('Too few connectors')

        flattened_connectors = []
        for connectorList in connectors.values():
            flattened_connectors.extend(connectorList)
        result = flattened_connectors + without_connectors
        return sorted(result, key=methodcaller('get', 'title'))


    l = []
    (root,) = g.connection_roots.get_all()
    for edge in _NTL(root.inE('is_a')):
        connected_parts = []

        part = edge.outV()
        l.append({'title': part.label,
                  'children': _get_connections_for_part(part)
        })
    l.sort(key=itemgetter('title'))
    return l


def _get_element_json(parent_el):
    l = []
    for edge in _NTL(parent_el.inE('is_a')):
        element = edge.outV()

        children = []
        for edge in _NTL(element.inE('belongs_to')):
            connection = edge.outV()
            (connected_part,) = connection.inE('connected_from')

        l.append({'title': element.label,
                  'children': _get_element_json(element)})
    l.sort(key=itemgetter('title'))
    return l


@app.route('/json')
def parts_json():
    data_type = request.args['type']
    if data_type == 'parts':
        (root,) = g.root_parts.get_all()
    elif data_type == 'standards':
        (root,) = g.root_standards.get_all()
    elif data_type == 'connectors':
        (root,) = g.root_connectors.get_all()
    elif data_type == 'connections':
        return jsonify({'children': _get_connections_json()})
    else:
        raise ValueError()
    return jsonify({'children': _get_element_json(root)})


def reset_db(args):
    if not args.force:
        answer = raw_input('Really import data (y,N)? ')
        if answer != 'y':
            print 'Abort'
            return

    global g
    g = init_graph()
    g.clear()
    g = init_graph()
    root_part = g.root_parts.create()
    root_standard = g.root_standards.create()
    root_connector = g.root_connectors.create()
    connection_root = g.connection_roots.create()

    load_units()
    load_attr_types()
    load_root_parts()
    load_standard()
    load_connectors()
    load_sub_parts()
    load_connections()
    print 'Finished importing'


def export_xml(args):
    outf = open('export.graphml', 'w')
    outf.write(g.get_graphml())


def run_ui(args):
    global g
    g = init_graph()

    app.debug = True
    app.secret_key = 'Todo'
    if True:
        toolbar = DebugToolbarExtension(app)
    app.run(port=5001)


COMMANDS = {
    'ui': run_ui,
    'reset_db': reset_db,
}


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('command', choices=COMMANDS.keys(), help='Run one of the commands')
parser.add_argument('--force', action="store_true", help='Force yes on user input for the given command')

args = parser.parse_args()

COMMANDS[args.command](args)
