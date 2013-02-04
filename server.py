#!/usr/bin/env python

import argparse
import json
from collections import OrderedDict
from operator import itemgetter, methodcaller, attrgetter
from logging import DEBUG

from flask import Flask, render_template_string, jsonify, request, Markup
from flaskext.htmlbuilder import html as H
from flask_debugtoolbar import DebugToolbarExtension

from model import *
from db import reset_db, init_graph


base_template = '''
{% extends "base.html" %}
{% block body %}
  <div class="container">
    <h1>{{heading}}</h1>
        {{content}}
  </div>
{% endblock %}'''


tree_template = '''
{% extends "base.html" %}
{% block body %}
    <script type="text/javascript">
        $(function(){
            $("#tree").dynatree({
                persist: true,
                onActivate: function(node){
                    var url = '/details?type={{datatype}}&eid='+node.data.key
                    $.ajax(url, {
                        'success': function(data, textStatus, jqXHR){
                            $('#tree_details').replaceWith(data);
                        }
                    })
                },
                initAjax: {
                    url: "/json?type={{datatype}}",
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
    <div class="row">
        <div class="span4">
            {{content}}
        </div>
        <div class="span5">
            <div id="tree_details">Select an element to show the details</div>
        </div>
    </div>
  </div>
{% endblock %}'''


app = Flask(__name__)


@app.route('/')
def index_view():
    return render_template_string(base_template, heading='Index', content='')


@app.route('/schema/units')
def units_view():
    rows = []
    for unit in g.units.get_all():
        attr_types = []
        for attr_type in unit.inV('is_unit') or []:
            attr_types.append(attr_type.label)

        rows.append(H.tr(
            H.td(unit.name),
            H.td(unit.label),
            H.td(unit.format),
            H.td(unit.note),
            H.td(', '.join(attr_types)),
        ))
    content = H.table(class_="table table-condensed table-bordered")(
        H.thead(
            H.tr(
                H.th('Name'), H.th('Unit'), H.th('Format'), H.th('Note'), H.th('Attribute types')
            )
        ),
        H.tbody(rows)
    )
    return render_template_string(base_template, heading='Attribute Types', content=content)

@app.route('/schema/attr_types')
def attr_types():
    rows = []
    attr_types = sorted(g.attr_types.get_all(), key=attrgetter('label'))
    for attr_type in attr_types:
        (unit,) = attr_type.outV('is_unit')

        parts = []
        for part in attr_type.inV('can_have_attr_type') or []:
            parts.append(part.label)

        rows.append(H.tr(
            H.td(Markup(attr_type.label)), #TODO: using Markup is unsafe
            H.td(unit.name),
            H.td(', '.join(parts)),
            H.td(attr_type.note)
        ))

    content = H.table(class_="table table-condensed table-bordered")(
        H.thead(
            H.tr(
                H.th('Name'), H.th('unit'), H.th('Part'), H.th('Note')
            )
        ),
        H.tbody(rows)
    )
    return render_template_string(base_template, heading='Units', content=content)


@app.route('/schema/parts')
def part_schema_view():
     return render_template_string(tree_template,
                                   heading='Part Schema',
                                   content=H.div(id='tree')(),
                                   datatype='part_schema')


@app.route('/schema/standards')
def standards_view():
    return render_template_string(tree_template,
                                  heading='Standards',
                                  content=H.div(id='tree')(),
                                  datatype='standards')


@app.route('/schema/connectors')
def connectors_view():
    return render_template_string(tree_template,
                                  heading='Standards',
                                  content=H.div(id='tree')(),
                                  datatype='connectors')


@app.route('/data/parts')
def parts_view():
     return render_template_string(tree_template,
                                   heading='Parts',
                                   content=H.div(id='tree')(),
                                   datatype='parts')


@app.route('/data/connections')
def connections_view():
    return render_template_string(tree_template,
                                  heading='connections',
                                  content=H.div(id='tree')(),
                                  datatype='connections')


@app.route('/data/attributes')
def attributes_view():
    return render_template_string(tree_template,
                                  heading='Attributes',
                                  content=H.div(id='tree')(),
                                  datatype='attributes')


def _get_connections_json():
    def _get_connections_for_part(connection_root_part, part):
        # key=connecor.eid, value=list_of_connector_dicts
        connectors = {}

        # list of dicts
        without_connectors = []

        # get all connectors that his part has
        for has_connector in part.outE('has_connector') or []:
            connector = has_connector.inV()
            connectors[connector.eid] = []
            for i in xrange(has_connector.quantity):
                connector_dict = {'title': connector.label,
                                  'key': connector.eid,
                                  'isFolder': True,
                                  'children': []}
                connectors[connector.eid].append(connector_dict)

        # get connected parts
        for connection in part.outV('connected_from') or []:
            # only follow connections which belong to this connection parent
            (this_connection_root_part,) = connection.outV('belongs_to')
            if not this_connection_root_part == connection_root_part:
                continue

            # check if the connection has a connector
            connected_via_list = connection.outE('connected_via')
            if connected_via_list:
                (connected_via,) = connected_via_list
                connector_eid = connected_via.inV().eid
            else:
                connector_eid = None

            # get the connected part
            (childpart,) = connection.outV('connected_to')

            child_dict = {'title': childpart.label, 'key': childpart.eid,}

            if childpart.outV('has_connection'):
                # part is a connection root
                child_dict['children'] = _get_connections_for_part(childpart, childpart)
            else:
                child_dict['children'] = _get_connections_for_part(connection_root_part, childpart)

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
    for part in root.inV('has_connection') or []:
        connected_parts = []
        l.append({'title': part.label,
                  'key': part.eid,
                  'children': _get_connections_for_part(part, part),
        })
    l.sort(key=itemgetter('title'))
    return l


def _get_attributes_json():
    attr_types = {}
    for attribute in g.attributes.get_all():
        parts = []
        for part in attribute.inV('has_attribute'):
            parts.append(part.label)
        parts.sort()

        if len(parts) > 1:
            (attr_type,) = attribute.outV('has_attr_type')
            (unit,) = attr_type.outV('is_unit')

            title = unit.format % {'unit': attribute.value} + ' [%s]' % len(parts)
            attr_type_dict = attr_types.setdefault(attr_type.label, {'title': attr_type.label, 'children': []})
            attr_type_dict['children'].append({'title': title, 'children': parts})

    l = []
    for key in sorted(attr_types):
        attribute_dict = attr_types[key]
        attribute_dict['children'].sort(key=itemgetter('title'))
        attribute_dict['title'] += ' [%s]' % len(attribute_dict['children'])
        l.append(attribute_dict)

    #return _render_string(base_template, heading='Attributes', content=H.ul(sorted(attributes_li, key=str)))
    return l


def _get_element_json(parent_el):
    l = []
    for element in parent_el.inV('is_a') or []:
        l.append({'title': element.label,
                  'key': element.eid,
                  'isFolder': hasattr(element, 'is_schema') and element.is_schema,
                  'children': _get_element_json(element)})
    l.sort(key=itemgetter('title'))
    return l


def _get_part_schema_json(parent_el):
    l = []
    for element in parent_el.inV('is_a') or []:
        d = {'title': element.label, 'key': element.eid }
        print element.label, element.is_schema
        if element.is_schema:
            d['children'] = _get_part_schema_json(element)
        l.append(d)
    l.sort(key=itemgetter('title'))
    return l


@app.route('/json')
def json():
    data_type = request.args['type']

    if data_type == 'parts':
        (root,) = g.root_parts.get_all()
        result = _get_element_json(root)

    elif data_type == 'standards':
        (root,) = g.root_standards.get_all()
        result = _get_element_json(root)

    elif data_type == 'connectors':
        (root,) = g.root_connectors.get_all()
        result = _get_element_json(root)

    elif data_type == 'part_schema':
        (root,) = g.root_parts.get_all()
        result = _get_part_schema_json(root)

    elif data_type == 'connections':
        result = _get_connections_json()

    elif data_type == 'attributes':
        result = _get_attributes_json()

    else:
        raise ValueError()

    return jsonify({'children': result})


@app.route('/details')
def details():
    def _get_parents(element):
        (parent,) = element.outV('is_a')
        # Hacky hacky hacky patteng
        if isinstance(parent, (RootConnector, RootPart, RootStandard)):
            return []
        else:
            l = _get_parents(parent)
            l.append(element.label)
            return l

    data_type = request.args['type']
    eid = request.args['eid']
    element = g.vertices.get(eid)

    ul = []
    for el in _get_parents(element):
        li = []
        if ul:
            li.append(H.span(class_='divider')(H.i(class_='icon-chevron-right')))
        li.append(el)
        ul.append(li)

    breadcrumb = H.ul(class_='breadcrumb')(ul)

    dl_dict = {}
    for attribute in element.outV('has_attribute') or []:
        (attr_type,) = attribute.outV('has_attr_type')
        (unit,) = attr_type.outV('is_unit')
        dl_dict[attr_type.label] = unit.format % {'unit': attribute.value}

    dl = []
    for name in sorted(dl_dict):
        dl.append(H.dt(name))
        dl.append(H.dd(Markup(dl_dict[name]))) #TODO: the use of Markup is unsafe here.

    if dl:
        content = H.dl(dl)
    else:
        content = 'No attributes'
    return str(H.div(id='tree_details')(breadcrumb, content))

def export_xml(args):
    outf = open('export.graphml', 'w')
    outf.write(g.get_graphml())


def run_ui(args):
    global g
    g = init_graph()
    #g.config.set_logger(DEBUG)
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
