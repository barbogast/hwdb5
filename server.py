#!/usr/bin/env python

import argparse
import json
from collections import OrderedDict
from operator import itemgetter, methodcaller

from flask import Flask, render_template_string, jsonify, request
from flaskext.htmlbuilder import html as H
from flask_debugtoolbar import DebugToolbarExtension

from model import *
from db import reset_db, init_graph


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
