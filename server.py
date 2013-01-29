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
from utils import ntl


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
                    url: "json?type={{datatype}}",
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

menu_items = OrderedDict([
    ('/parts', 'Parts'),
    ('/attr_types', 'Attribute Types'),
    ('/attributes', 'Attributes'),
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
    rows = []
    for unit in g.units.get_all():
        attr_types = []
        for attr_type in ntl(unit.inV('is_unit')):
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
    return _render_string(base_template, heading='Attribute Types', content=content)

@app.route('/attr_types')
def attr_types():
    rows = []
    attr_types = sorted(g.attr_types.get_all(), key=attrgetter('label'))
    for attr_type in attr_types:
        (unit,) = attr_type.outV('is_unit')

        parts = []
        for part in ntl(attr_type.inV('can_have_attr_type')):
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
    return _render_string(base_template, heading='Units', content=content)

@app.route('/attributes')
def attributes_view():
    attributes_li = []
    for attribute in g.attributes.get_all():
        parts_li = []
        for part in attribute.inV('has_attribute'):
            parts_li.append(H.li(part.label))

        if len(parts_li) > 1:
            (attr_type,) = attribute.outV('has_attr_type')
            (unit,) = attr_type.outV('is_unit')

            attributes_li.append(
                H.ul(
                    attr_type.label, ': ',
                    H.strong(attribute.value, ' ', Markup(unit.name)),
                    H.ul( sorted(parts_li, key=str))
                )
            )
    return _render_string(base_template, heading='Attributes', content=H.ul(sorted(attributes_li, key=str)))

@app.route('/parts')
def parts_view():
     return _render_string(tree_template,
                           heading='Parts',
                           content=H.div(id='tree')(),
                           datatype='parts')


@app.route('/standards')
def standards_view():
    return _render_string(tree_template,
                          heading='Standards',
                          content=H.div(id='tree')(),
                          datatype='standards')


@app.route('/connectors')
def connectors_view():
    return _render_string(tree_template,
                          heading='Standards',
                          content=H.div(id='tree')(),
                          datatype='connectors')


@app.route('/connections')
def connections_view():
    return _render_string(tree_template,
                          heading='connections',
                          content=H.div(id='tree')(),
                          datatype='connections')


def _get_connections_json():
    def _get_connections_for_part(part):
        # key=connecor.eid, value=list_of_connector_dicts
        connectors = {}

        # list of dicts
        without_connectors = []

        # get all connectors that his part has
        for has_connector in ntl(part.outE('has_connector')):
            connector = has_connector.inV()
            connectors[connector.eid] = []
            for i in xrange(has_connector.quantity):
                connector_dict = {'title': connector.label, 'isFolder': True, 'children': []}
                connectors[connector.eid].append(connector_dict)

        # get connected parts
        for connection in ntl(part.outV('connected_from')):

            # check if the connection has a connector
            connected_via_list = connection.outE('connected_via')
            if connected_via_list:
                (connected_via,) = connected_via_list
                connector_eid = connected_via.inV().eid
            else:
                connector_eid = None

            # get the connected part
            (childpart,) = connection.outV('connected_to')
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
    for part in ntl(root.inV('is_a')):
        connected_parts = []
        l.append({'title': part.label,
                  'children': _get_connections_for_part(part)
        })
    l.sort(key=itemgetter('title'))
    return l


def _get_element_json(parent_el):
    l = []
    for element in ntl(parent_el.inV('is_a')):
        l.append({'title': element.label,
                  'key': element.eid,
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


@app.route('/details')
def details():
    data_type = request.args['type']
    eid = request.args['eid']
    element = g.vertices.get(eid)
    dl = []
    for attribute in ntl(element.outV('has_attribute')):
        (attr_type,) = attribute.outV('has_attr_type')
        (unit,) = attr_type.outV('is_unit')
        dl.append(H.dt(attr_type.label))
        dl.append(H.dd(Markup(unit.format % {'unit': attribute.value}))) #TODO: the use of Markup is unsafe here.

    if dl:
        content = H.dl(dl)
    else:
        content = 'No attributes'
    return str(H.div(id='tree_details')(content))

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
