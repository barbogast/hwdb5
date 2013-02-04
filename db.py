from readcsv import read_all_files
import treetools
import data
from model import *


def init_graph():
    engine = 'neo4j'
    #engine = 'rexster'

    if engine == 'rexster':
        from bulbs.rexster import Graph, Config
        url = 'http://localhost:8182/graphs/hwdbgraph'
    elif engine == 'neo4j':
        from bulbs.neo4jserver import Graph, Config
        url = 'http://localhost:7474/db/data/'
    else:
        raise Exception('Unknown engine %s' % engine)

    config = Config(url)
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
    g.add_proxy("connection_schema_roots", ConnectionSchemaRoot)


    for node_from, rel, node_to in relationships:
        g.add_proxy(rel.label, rel)
    return g


def _load_units():
    for unit in data.units:
        d = {
            'name': unit.pop('label'),
            'label': unit.pop('name'),
            'format': unit.pop('format', '%(unit)s'),
            'note': unit.pop('note', None),
        }
        assert not unit
        g.units.create(**d)


def _load_attr_types():
    for attr_type in data.attr_types:
        (unit,) = list(g.units.index.lookup(label=attr_type.pop('unit')))
        attr_type['label'] = attr_type.pop('name')
        attr_type_obj = g.attr_types.create(**attr_type)
        g.is_unit.create(attr_type_obj, unit)


def _add_element(el_dict, parent_el, element_type, root_element_node, extra_properties={}):
    assert 'attr_types' not in el_dict, 'attr_types should be on the first level elements of the part tree (or should they?)'
    label = el_dict.pop('<name>')

    # Check if element is already present
    result = element_type.index.lookup(label=label)
    if result:
        (el,) = result
        if not hasattr(el, 'is_schema' or not el.is_schema):
            raise Exception('Element %r already present' % label)

    else:

        d = {
            'label': label,
            'note': el_dict.pop('<note>', None),
        }
        d.update(extra_properties)
        el = element_type.create(**d)

        if parent_el is None:
            g.is_a.create(el, root_element_node)
        else:
            g.is_a.create(el, parent_el)

        for attr_type_name in el_dict.pop('<attr_types>', []):
            (attr_type,) = g.attr_types.index.lookup(label=attr_type_name)
            g.can_have_attr_type.create(el, attr_type)

        for attr_type_name, attr_value in el_dict.pop('<attrs>', {}).iteritems():
            res = g.attr_types.index.lookup(label=attr_type_name)
            if not res:
                raise Exception('Could not find attr_type %s' % attr_type_name)
            (attr_type,) = res

            # Try to find an exisiting attribute with the same value and attr_type
            attribute = None
            for attribute_2 in g.attributes.index.lookup('value', attr_value) or []:
                (attr_type_2,) = attribute_2.outV('has_attr_type')
                if attr_type == attr_type_2:
                    attribute = attribute_2
                    break

            if not attribute:
                attribute = g.attributes.create(value=attr_value)
                g.has_attr_type.create(attribute, attr_type)

            g.has_attribute.create(el, attribute)

        for standard_name in el_dict.pop('<standards>', []):
            (standard,) = g.standards.index.lookup(label=standard_name)
            g.implements.create(el, standard)

        for conn_dict in el_dict.pop('<connectors>', []):
            conn_label = conn_dict.pop('<name>')
            result = g.connectors.index.lookup(label=conn_label)
            if not result:
                raise Exception('Could not find connector %r to connecto %r' % (conn_label, el.label))
            (connector,) = result
            g.has_connector.create(el, connector, quantity=conn_dict.pop('<quantity>', 1))

    for child_el_dict in el_dict.pop('<children>', []):
        _add_element(child_el_dict, el, element_type, root_element_node, extra_properties)

    assert not el_dict, el_dict


def _load_part_schema(csv_files):
    (root_part,) = g.root_parts.get_all()
    parts = treetools.inflate_tree(data.part_schema, csv_files, 'parts')
    for part_dict in parts:
        _add_element(part_dict, None, g.parts, root_part, extra_properties={'is_schema': True})


def _load_standards(csv_files):
    (root_standard,) = g.root_standards.get_all()
    standards = treetools.inflate_tree(data.standards, csv_files, 'standards')
    for standard_dict in standards:
        _add_element(standard_dict, None, g.standards, root_standard)


def _load_connectors(csv_files):
    (root_connector,) = g.root_connectors.get_all()
    connectors = treetools.inflate_tree(data.connectors, csv_files, 'connectors')
    for connector_dict in connectors:
        _add_element(connector_dict, None, g.connectors, root_connector)


def _load_parts(csv_files):
    parts = treetools.inflate_tree(data.parts, csv_files, 'parts')
    for part_dict in parts:
        (part,) = g.parts.index.lookup(label=part_dict.pop('<name>'))
        for child_part_dict in part_dict.pop('<children>'):
            _add_element(child_part_dict, part, g.parts, None)

        assert not part_dict, part_dict


def _load_connection_schema():
    def _add_connection_schema(parent_part, child_part_dicts):
        for child_part_dict in child_part_dicts:
            (child_part,) = g.parts.index.lookup(label=child_part_dict.pop('<name>'))
            g.can_be_contained_in.create(child_part, parent_part)
            _add_connection_schema(child_part, child_part_dict.pop('<children>', []))

    (connection_schema_root,) = g.connection_schema_roots.get_all()
    connections = treetools.inflate_tree(data.connection_schema)
    for root_part_dict in connections:
        (root_part,) = g.parts.index.lookup(label=root_part_dict.pop('<name>'))
        g.is_a.create(root_part, connection_schema_root)
        _add_connection_schema(root_part, root_part_dict.pop('<children>'))

        assert not root_part_dict


def _load_connections(systems):
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
            for child_dict in conn_dict.pop('<children>', []):
                _create_connection(system_part, parent_part, child_dict, connector)

        assert not part_dict, part_dict


    (connection_root,) = g.connection_roots.get_all()
    for system_dict in systems:
        (system_part,) = g.parts.index.lookup(label=system_dict.pop('<name>'))
        g.has_connection.create(system_part, connection_root)
        _add_connection(system_part, system_part, system_dict)
        assert not system_dict, system_dict


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
    connection_schema_root = g.connection_schema_roots.create()

    csv_files = read_all_files()
    print '== Import units =='
    _load_units()
    print '== Import attr types =='
    _load_attr_types()
    print '== Import part schema =='
    _load_part_schema(csv_files)
    print '== Import connection schema =='
    _load_connection_schema()
    print '== Import standards =='
    _load_standards(csv_files)
    print '== Import connectors =='
    _load_connectors(csv_files)
    print '== Import parts =='
    _load_parts(csv_files)
    print '== Import systems from data.py =='
    systems = treetools.inflate_tree(data.systems, 'connections')
    _load_connections(systems)
    print '== Import systems from csv=='
    _load_connections(csv_files['Pentium4_Willamette']['connections'])
    print 'Finished importing'
