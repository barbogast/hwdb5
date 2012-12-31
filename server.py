#!/usr/bin/env python

import argparse
import json
from collections import OrderedDict

from bulbs.rexster import Graph, Config
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from flask import Flask, render_template_string
from flaskext.htmlbuilder import html as H
from flask_debugtoolbar import DebugToolbarExtension

import treetools

class LabeledNode(Node):
    note = String(nullable=True)

    def __unicode__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.label)


class RootPart(LabeledNode):
    element_type = 'root_part'

class Part(LabeledNode):
    element_type = "part"
    label = String(nullable=False)

class Connector(LabeledNode):
    element_type = "connector"
    label = String(nullable=False)

class Connection(Node):
    element_type = "part_connection"

class Standard(LabeledNode):
    element_type = "standard"
    label = String(nullable=False)

class AttrType(LabeledNode):
    element_type = "attr_type"
    label = String(nullable=False)

class Company(LabeledNode):
    element_type = "company"
    label = String(nullable=False)

class Unit(LabeledNode):
    element_type = "unit"
    name = String(nullable=False)
    label = String(nullable=False)
    format = String(nullable=False)

class Attribute(Node):
    element_type = "attribute"
    value = String(nullable=False)


class IsA(Relationship):
    """ Standard => Standard
        Part => Part
        Part => Root Part """
    label = "is_a"

class HasConnection(Relationship):
    """ Part => Connection """
    label = "has_connection"

class HasPart(Relationship):
    """ Connection => Part """
    label = "has_part"

class BelongsTo(Relationship):
    """ Connection => Part """
    label = "belongs_to"

class Implements(Relationship):
    """ Part => Standard """
    label = "implements"

class Produces(Relationship):
    """ Company => Part """
    label = "produces"

class IsUnit(Relationship):
    """ Company => Part """
    label = "is_unit"

class HasAttrType(Relationship):
    """ Part => AttrType
        Attribute => AttrType """
    label = "has_attr_type"

class HasAttribute(Relationship):
    """ Part => Attribute """
    label = "has_attribute"


g = None
def init_graph():
    config = Config('http://localhost:8182/graphs/hwdbgraph')
    g = Graph(config)
    g.add_proxy("root_parts", RootPart)
    g.add_proxy("parts", Part)
    g.add_proxy("standards", Standard)
    g.add_proxy("connections", Connection)
    g.add_proxy("attr_types", AttrType)
    g.add_proxy("companies", Company)
    g.add_proxy("units", Unit)
    g.add_proxy("attributes", Attribute)
    g.add_proxy("connectors", Connector)

    g.add_proxy("is_a", IsA)
    g.add_proxy("has_connection", HasConnection)
    g.add_proxy("has_part", HasPart)
    g.add_proxy("belongs_to", BelongsTo)
    g.add_proxy("implements", Implements)
    g.add_proxy("produces", Produces)
    g.add_proxy("is_unit", IsUnit)
    g.add_proxy("has_attr_type", HasAttrType)
    g.add_proxy("has_attribute", HasAttribute)
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


def load_root_parts():
    import data
    parts = treetools.inflate_tree(data.parts)

    for part_dict in parts:
        d = {
            'label': part_dict.pop('<name>'),
            'note': part_dict.pop('<note>', None),
        }

        part = g.parts.create(**d)
        g.is_a.create(part, g.root_parts.get_all().next())

        for attr_type_name in part_dict.pop('<attr_types>', []):
            (attr_type,) = g.attr_types.index.lookup(label=attr_type_name)
            g.has_attr_type.create(part, attr_type)

        assert not part_dict


def _add_element(el_dict, parent_el, element_type):
    assert 'attr_types' not in el_dict, 'attr_types should be on the first level elements of the part tree (or should they?)'
    d = {
        'label': el_dict.pop('<name>'),
        'note': el_dict.pop('<note>', None),
    }
    el = element_type.create(**d)

    if parent_el is not None:
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
        _add_element(child_el_dict, el, element_type)

    assert not el_dict, el_dict


def load_standard():
    import data
    standards = treetools.inflate_tree(data.standards)
    for standard_dict in standards:
        _add_element(standard_dict, None, g.standards)

def load_connectors():
    import data
    connectors = treetools.inflate_tree(data.connectors)
    for connector_dict in connectors:
        _add_element(connector_dict, None, g.connectors)

def load_sub_parts():
    import data
    parts = treetools.inflate_tree(data.subparts)

    for part_dict in parts:
        (part,) = g.parts.index.lookup(label=part_dict.pop('<name>'))
        for child_part_dict in part_dict.pop('<children>'):
            _add_element(child_part_dict, part, g.parts)

        assert not part_dict, part_dict


base_template = '''
{% extends "base.html" %}
{% block body %}
  <div class="container">
    <h1>{{heading}}</h1>
    {{content}}
  </div>
{% endblock %}'''

menu_items = OrderedDict([
    ('/parts', 'Parts'),
    ('/attr_types', 'Attribute Types'),
    ('/attributes', 'Attributes'),
    ('/units', 'Units'),
    ('/combinations', 'Combinations'),
    ('/standards', 'Standards'),
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

    doc = H.div(H.h1('Units'), H.ul(unit_html))
    return _render_string(base_template, content=doc)


@app.route('/parts')
def parts_view():
    def _get_part_li(parent_part):
        parts_html = []
        edges_iter = parent_part.inE('is_a')
        if edges_iter:
            for edge in edges_iter:
                part = edge.outV()
                parts_html.append(H.li(part.label, _get_part_li(part)))
        return H.ul(parts_html)
    doc = H.div(id='tree')(_get_part_li(g.root_parts.get_all().next()))
    return _render_string(base_template, heading='Parts', content=doc)



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

    load_units()
    load_attr_types()
    load_root_parts()
    load_standard()
    load_connectors()
    load_sub_parts()
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
