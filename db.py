from logging import DEBUG

from readcsv import read_all_files
from model import N, make_bulbs_node_class, relationship_classes
import treetools
import data


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
    #g.config.set_logger(DEBUG)

    for name, node_cls in N.iteritems():
        bubls_node_cls = make_bulbs_node_class(name='Bulbs'+name,
                                               properties=node_cls.properties)
        g.add_proxy(node_cls.__name__, bubls_node_cls)
        node_cls._bulbs_proxy = getattr(g, node_cls.__name__)

    for rel_cls in relationship_classes:
        g.add_proxy(rel_cls.label, rel_cls)
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
        N.Unit.create(**d)


def _load_attr_types():
    for attr_type in data.attr_types:
        unit = N.Unit.get_one(label=attr_type.pop('unit'))
        attr_type['label'] = attr_type.pop('name')
        attr_type_obj = N.AttrType.create(**attr_type)
        g.is_unit.create(attr_type_obj._bulbs_node, unit._bulbs_node)


def _add_element(el_dict, parent_el, element_type, root_element_node, extra_properties={}):
    assert 'attr_types' not in el_dict, 'attr_types should be on the first level elements of the part tree (or should they?)'
    label = el_dict.pop('<name>')

    # Check if element is already present
    result = element_type.get_all(label=label)
    if result:
        (el,) = result
        if not 'is_schema' in el.properties or not el.P.is_schema:
            raise Exception('Element %r already present' % label)

    else:
        d = {
            'label': label,
            'note': el_dict.pop('<note>', None),
        }
        d.update(extra_properties)
        el = element_type.create(**d)

        if parent_el is None:
            g.is_a.create(el._bulbs_node, root_element_node._bulbs_node)
        else:
            g.is_a.create(el._bulbs_node, parent_el._bulbs_node)

        for attr_type_name in el_dict.pop('<attr_types>', []):
            attr_type = N.AttrType.get_one(label=attr_type_name)
            g.can_have_attr_type.create(el._bulbs_node, attr_type._bulbs_node)

        for attr_type_name, attr_value in el_dict.pop('<attrs>', {}).iteritems():
            res = N.AttrType.get_all(label=attr_type_name)
            if not res:
                raise Exception('Could not find attr_type %s' % attr_type_name)
            (attr_type,) = res

            # Try to find an exisiting attribute with the same value and attr_type
            attribute = None
            for attribute_2 in N.Attribute.get_all(value=attr_value) or []:
                (attr_type_2,) = attribute_2._bulbs_node.outV('has_attr_type')
                if attr_type._bulbs_node == attr_type_2:
                    attribute = attribute_2
                    break

            if not attribute:
                attribute = N.Attribute.create(value=attr_value)
                g.has_attr_type.create(attribute._bulbs_node, attr_type._bulbs_node)

            g.has_attribute.create(el._bulbs_node, attribute._bulbs_node)

        for standard_name in el_dict.pop('<standards>', []):
            standard = N.Standard.get_one(label=standard_name)
            g.implements.create(el._bulbs_node, standard._bulbs_node)

        for conn_dict in el_dict.pop('<connectors>', []):
            conn_label = conn_dict.pop('<name>')
            result = N.Connector.get_all(label=conn_label)
            if not result:
                raise Exception('Could not find connector %r to connecto %r' % (conn_label, el.label))
            (connector,) = result
            g.has_connector.create(el._bulbs_node, connector._bulbs_node, quantity=conn_dict.pop('<quantity>', 1))

    for child_el_dict in el_dict.pop('<children>', []):
        _add_element(child_el_dict, el, element_type, root_element_node, extra_properties)

    assert not el_dict, el_dict


def _load_part_schema(csv_files):
    root_part = N.RootPart.get_one()
    parts = treetools.inflate_tree(data.part_schema, csv_files, 'parts')
    for part_dict in parts:
        _add_element(part_dict, None, N.Part, root_part, extra_properties={'is_schema': True})


def _load_standards(csv_files):
    root_standard = N.RootStandard.get_one()
    standards = treetools.inflate_tree(data.standards, csv_files, 'standards')
    for standard_dict in standards:
        _add_element(standard_dict, None, N.Standard, root_standard)


def _load_connectors(csv_files):
    root_connector = N.RootConnector.get_one()
    connectors = treetools.inflate_tree(data.connectors, csv_files, 'connectors')
    for connector_dict in connectors:
        _add_element(connector_dict, None, N.Connector, root_connector)


def _load_parts(csv_files):
    parts = treetools.inflate_tree(data.parts, csv_files, 'parts')
    for part_dict in parts:
        part = N.Part.get_one(label=part_dict.pop('<name>'))
        for child_part_dict in part_dict.pop('<children>'):
            _add_element(child_part_dict, part, N.Part, None)

        assert not part_dict, part_dict


def _load_connection_schema():
    def _add_connection_schema(parent_part, child_part_dicts):
        for child_part_dict in child_part_dicts:
            child_part = N.Part.get_one(label=child_part_dict.pop('<name>'))
            g.can_be_contained_in.create(child_part._bulbs_node, parent_part._bulbs_node)
            _add_connection_schema(child_part, child_part_dict.pop('<children>', []))

    connection_schema_root = N.ConnectionSchemaRoot.get_one()
    connections = treetools.inflate_tree(data.connection_schema)
    for root_part_dict in connections:
        root_part = N.Part.get_one(label=root_part_dict.pop('<name>'))
        g.is_a.create(root_part._bulbs_node, connection_schema_root._bulbs_node)
        _add_connection_schema(root_part, root_part_dict.pop('<children>'))

        assert not root_part_dict


def _load_connections(systems):
    def _create_connection(system_part, parent_part, child_dict, connector):
        child_part = N.Part.get_one(label=child_dict.pop('<name>'))
        connection = N.Connection.create(quantity=child_dict.pop('<quantity>', 1))
        g.belongs_to.create(connection._bulbs_node, system_part._bulbs_node)
        g.connected_from.create(parent_part._bulbs_node, connection._bulbs_node)
        g.connected_to.create(connection._bulbs_node, child_part._bulbs_node)
        if connector:
            g.connected_via.create(connection._bulbs_node, connector._bulbs_node)

        _add_connection(system_part, child_part, child_dict)
        assert not child_dict, child_dict


    def _add_connection(system_part, parent_part, part_dict):
        for child_dict in part_dict.pop('<no_connector>', []):
            _create_connection(system_part, parent_part, child_dict, None)

        for conn_dict in part_dict.pop('<connectors>', []):
            connector = N.Connector.get_one(label=conn_dict.pop('<name>'))
            for child_dict in conn_dict.pop('<children>', []):
                _create_connection(system_part, parent_part, child_dict, connector)

        assert not part_dict, part_dict


    connection_root = N.ConnectionRoot.get_one()
    for system_dict in systems:
        system_part = N.Part.get_one(label=system_dict.pop('<name>'))
        g.has_connection.create(system_part._bulbs_node, connection_root._bulbs_node)
        _add_connection(system_part, system_part, system_dict)
        assert not system_dict, system_dict


def reset_db():
    root_part = N.RootPart.create()
    root_standard = N.RootStandard.create()
    root_connector = N.RootConnector.create()
    connection_root = N.ConnectionRoot.create()
    connection_schema_root = N.ConnectionSchemaRoot.create()

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
