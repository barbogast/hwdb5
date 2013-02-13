import json
from operator import itemgetter, methodcaller

from flask import Flask, render_template, jsonify, request, Markup, redirect
from flaskext.htmlbuilder import html as H

from model import N


app = Flask(__name__)


@app.route('/')
def index_view():
    return render_template('normal.html', heading='Index', content='')


@app.route('/schema/units')
def units_view():
    units = []
    for unit in N.Unit.get_all():
        units.append(unit)
    units.sort(key=lambda u: u.P.label.lower())

    rows = []
    for unit in units:
        attr_types = []
        for attr_type in unit._bulbs_node.inV('IsUnit') or []:
            attr_types.append(attr_type.label)

        rows.append(H.tr(
            H.td(unit.P.name),
            H.td(unit.P.label),
            H.td(unit.P.format),
            H.td(unit.P.note),
            H.td(', '.join(attr_types)),
            H.td(H.button(type='submit', name='edit_form', value=str(unit.eid))('Edit')),
            H.td(H.button(type='submit', name='delete_form', value=str(unit.eid))('Delete')),
        ))

    table = H.table(class_="table table-condensed table-bordered")(
        H.thead(
            H.tr(
                H.th('Name'), H.th('Unit'), H.th('Format'), H.th('Note'), H.th('Attribute types')
            )
        ),
        H.tbody(rows)
    )
    content = H.form(method='POST', action='/schema/edit_units')(
        table,
        H.td(H.button(type='submit', name='new_form', value='new')('New')),
    )
    return render_template('normal.html', heading='Units', content=content)


def _render_input(values, label, name, id=None, type=''):
    if id is None:
        id = name

    return H.div(class_='control-group')(
        H.label(class_='control-label', for_=id)(label),
        H.div(class_='controls')(
            H.input(name=name, value=values.get(name), id=id, type=type)
        )
    )


def _mk_form(unit, action, eid, msg=''):
    return H.form(method='POST')(class_="form-horizontal", method='POST')(
        msg,
        _render_input(unit, 'Name', name='name'),
        _render_input(unit, 'Unit', name='label'),
        _render_input(unit, 'Format', name='format'),
        _render_input(unit, 'Note', name='note'),
        H.button(type='submit', name='action', value=action)('Save'),
        H.input(type='hidden', name='eid', value=str(eid)),
    )


@app.route('/schema/edit_units', methods=('GET', 'POST',))
def edit_units():
    if 'delete_form' in request.form:
        eid = request.form['delete_form']
        unit = N.Unit.from_eid(eid)
        attr_types = unit.get_attr_types()

        if attr_types:
            content = H.div(
                'Cannot delete unit, its used for %s' % ', '.join((a.label for a in attr_types)),
                H.br, H.a(href='/schema/units')('Back'),
            )
        else:
            form_els = [
                'Really delete "%s"?' % unit.P.name, H.br,
                H.button(type='submit', name='action', value='delete')('Yes'), H.br,
                H.a(href='/schema/units')('Back'),
            ]
            if eid is not None:
                form_els.append(H.input(type='hidden', name='eid', value=eid))

            content = H.form(method='POST')(form_els)
        return render_template('normal.html', heading='Really delete?', content=content)

    elif 'edit_form' in request.form:
        unit = N.Unit.from_eid(request.form['edit_form'])
        content = _mk_form(unit, 'edit', unit.eid)
        return render_template('normal.html', heading='Edit unit', content=content)

    elif 'new_form' in request.form:
        content = _mk_form({}, 'new', None)
        return render_template('normal.html', heading='Add unit', content=content)


    elif request.form.get('action') == 'delete':
        unit = N.Unit.from_eid(request.form['eid'])
        if unit:
            unit.delete()
        return redirect('/schema/units')

    elif request.form.get('action') == 'edit':
        unit = N.Unit.from_eid(request.form['eid'])
        if request.form['label'] != unit.P.label and N.Unit.get_all(label=request.form['label']):
            content = _mk_form(request.form, 'edit', unit.eid, 'Unit name already taken')
            return render_template('normal.html', heading='Edit unit', content=content)
        unit.update(request.form)
        unit.save()
        return redirect('/schema/units')

    elif request.form.get('action') == 'new':
        if N.Unit.get_all(label=request.form['label']):
            content = _mk_form(request.form, 'new', None, 'Unit with this unit already present')
            return render_template('normal.html', heading='Add unit', content=content)

        N.Unit.create(**dict(request.form.iteritems()))
        return redirect('/schema/units')

    else:
        raise Exception('Invalid action')


@app.route('/schema/attr_types')
def attr_types():
    rows = []
    attr_types = sorted(N.AttrType.get_all(), key=lambda el: el.P.label)
    for attr_type in attr_types:
        (unit,) = attr_type._bulbs_node.outV('IsUnit')

        parts = []
        for part in attr_type._bulbs_node.inV('CanHaveAttrType') or []:
            parts.append(part.label)

        rows.append(H.tr(
            H.td(Markup(attr_type.P.label)), #TODO: using Markup is unsafe
            H.td(unit.name),
            H.td(', '.join(parts)),
            H.td(attr_type.P.note)
        ))

    content = H.table(class_="table table-condensed table-bordered")(
        H.thead(
            H.tr(
                H.th('Name'), H.th('unit'), H.th('Part'), H.th('Note')
            )
        ),
        H.tbody(rows)
    )
    return render_template('normal.html', heading='Attribute Types', content=content)


def _create_render_tree_func(url, heading, datatype):
    def func():
        return render_template('tree.html', heading=heading, datatype=datatype)
    app.add_url_rule(url, url.replace('/', '_'), func)

_create_render_tree_func('/schema/parts', 'Part Schema', 'part_schema')
_create_render_tree_func('/schema/standards', 'Standards', 'standards')
_create_render_tree_func('/schema/connectors', 'Connectors', 'connectors')
_create_render_tree_func('/schema/connections', 'Connection schema', 'connection_schema')
_create_render_tree_func('/data/parts', 'Parts', 'parts')
_create_render_tree_func('/data/connections', 'Connections', 'connections')
_create_render_tree_func('/data/attributes', 'Attributes', 'attributes')
_create_render_tree_func('/schema/os', 'Operating Systems', 'os')


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
        for connection in part.outV('ConnectedFrom') or []:
            # only follow connections which belong to this connection parent
            (this_connection_root_part,) = connection.outV('BelongsTo')
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
            (childpart,) = connection.outV('ConnectedTo')

            child_dict = {'title': childpart.label, 'key': childpart.eid,}

            if childpart.outV('HasConnection'):
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
    root = N.ConnectionRoot.get_one()
    for part in root._bulbs_node.inV('HasConnection') or []:
        connected_parts = []
        l.append({'title': part.label,
                  'key': part.eid,
                  'children': _get_connections_for_part(part, part),
        })
    l.sort(key=itemgetter('title'))
    return l


def _get_attributes_json():
    attr_types = {}
    for attribute in N.Attribute.get_all():
        parts = []
        for part in attribute._bulbs_node.inV('HasAttribute'):
            parts.append(part.label)
        parts.sort()

        if len(parts) > 1:
            (attr_type,) = attribute._bulbs_node.outV('HasAttrType')
            (unit,) = attr_type.outV('IsUnit')
            title = unit.format % {'unit': attribute.P.value} + ' [%s]' % len(parts)
            attr_type_dict = attr_types.setdefault(attr_type.label, {'title': attr_type.label, 'children': []})
            attr_type_dict['children'].append({'title': title, 'children': parts})

    l = []
    for key in sorted(attr_types):
        attribute_dict = attr_types[key]
        attribute_dict['children'].sort(key=itemgetter('title'))
        attribute_dict['title'] += ' [%s]' % len(attribute_dict['children'])
        l.append(attribute_dict)

    return l


def _get_element_json(parent_el):
    l = []
    for element in parent_el._bulbs_node.inV('IsA') or []:
        l.append({'title': element.label,
                  'key': element.eid,
                  'isFolder': hasattr(element, 'is_schema') and element.is_schema,
                  'children': _get_element_json(N.Part(element))})
    l.sort(key=itemgetter('title'))
    return l


def _get_part_schema_json(parent_el):
    l = []
    for element in parent_el._bulbs_node.inV('IsA') or []:
        if element.is_schema:
            d = {'title': element.label, 'key': element.eid }
            d['children'] = _get_part_schema_json(N.Part(element))
            l.append(d)
    l.sort(key=itemgetter('title'))
    return l


def _get_connection_schema_json(parent_el, edge_type):
    # the function is called the first time with edge_type='is_a'
    # all inner calls have edge_type='can_contain'
    l = []
    for element in parent_el._bulbs_node.inV(edge_type) or []:
        d = {'title': element.label, 'key': element.eid }
        d['children'] = _get_connection_schema_json(N.Part(element), 'CanBeContainedIn')
        l.append(d)
    l.sort(key=itemgetter('title'))
    return l


@app.route('/json')
def json():
    data_type = request.args['type']

    if data_type == 'parts':
        root = N.RootPart.get_one()
        result = _get_element_json(root)

    elif data_type == 'standards':
        root = N.RootStandard.get_one()
        result = _get_element_json(root)

    elif data_type == 'connectors':
        root = N.RootConnector.get_one()
        result = _get_element_json(root)

    elif data_type == 'os':
        root = N.RootOperatingSystem.get_one()
        result = _get_element_json(root)

    elif data_type == 'part_schema':
        root = N.RootPart.get_one()
        result = _get_part_schema_json(root)

    elif data_type == 'connection_schema':
        root = N.ConnectionSchemaRoot.get_one()
        result = _get_connection_schema_json(root, 'IsA')

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
        (parent,) = element.outV('IsA')
        # Hacky hacky hacky patteng
        if isinstance(parent, (N.RootConnector._bulbs_proxy.element_class,
                               N.RootPart._bulbs_proxy.element_class,
                               N.RootStandard._bulbs_proxy.element_class)):
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
    for attribute in element.outV('HasAttribute') or []:
        (attr_type,) = attribute.outV('HasAttrType')
        (unit,) = attr_type.outV('IsUnit')
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
