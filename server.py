import argparse
import json

from bulbs.rexster import Graph, Config
from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime
from flask import Flask, render_template_string
from flaskext.htmlbuilder import html as H
from flask_debugtoolbar import DebugToolbarExtension


class LabeledNode(Node):
    def __unicode__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.label)


class RootPart(LabeledNode):
    element_type = 'root_part'

class Part(LabeledNode):
    element_type = "part"
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
    note = String(nullable=True)


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
    """ Part => AttrType """
    label = "has_attr_type"


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

    g.add_proxy("is_a", IsA)
    g.add_proxy("has_connection", HasConnection)
    g.add_proxy("has_part", HasPart)
    g.add_proxy("belongs_to", BelongsTo)
    g.add_proxy("implements", Implements)
    g.add_proxy("produces", Produces)
    g.add_proxy("is_unit", IsUnit)
    g.add_proxy("has_attr_type", HasAttrType)
    return g


def load_units():
    units = json.load(open('units.json'))['units']
    for unit in units:
        name = unit.pop('name')
        unit['name'] = unit['label']
        unit['label'] = name

        g.units.create(**unit)


def load_attr_types():
    attr_types = json.load(open('attr_types.json'))['attr_types']

    for attr_type in attr_types:
        (unit,) = list(g.units.index.lookup(label=attr_type.pop('unit')))
        attr_type['label'] = attr_type.pop('name')
        attr_type_obj = g.attr_types.create(**attr_type)
        g.is_unit.create(attr_type_obj, unit)


def load_parts():
    def _add_child(part_dict, parent_part):
        assert 'attr_types' not in part_dict
        part = g.parts.create(label=part_dict['name'])
        g.is_a.create(part, parent_part)

        for child_part_dict in part_dict.get('children', []):
            _add_child(child_part_dict, part)

    parts = json.load(open('parts.json'))['parts']

    for part_dict in parts:
        part = g.parts.create(label=part_dict['name'])
        g.is_a.create(part, g.root_parts.get_all().next())

        for attr_type_name in part_dict.get('attr_types', []):
            (attr_type,) = g.attr_types.index.lookup(label=attr_type_name)
            g.has_attr_type.create(part, attr_type)

        for child_part_dict in part_dict.get('children', []):
            _add_child(child_part_dict, part)


base_template = '''
<body>
  <div class="container">
    <h1>{{heading}}</h1>
    {{content}}
  </div>
</body>
'''


app = Flask(__name__)

@app.route('/units')
def units_view():
    unit_html = []
    for unit in g.units.get_all():
        unit_html.append(H.li(unit.name, ' [%s]'%unit.label))

    doc = H.div(H.h1('Units'), H.ul(unit_html))
    return render_template_string(base_template, content=doc)


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
    doc = _get_part_li(g.root_parts.get_all().next())
    return render_template_string(base_template, content=doc)



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
    load_parts()
    print 'Finished importing'


def export_xml(args):
    outf = open('export.graphml', 'w')
    outf.write(g.get_graphml())


def run_ui(args):
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
