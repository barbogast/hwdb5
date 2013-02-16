import os

from readcsv import read_all_files
from model import R, g, get_node_classes
import treetools
import data



def _load_units():
    for unit in data.units:
        d = {
            'name': unit.pop('label'),
            'label': unit.pop('name'),
            'format': unit.pop('format', '%(unit)s'),
            'note': unit.pop('note', None),
        }
        assert not unit
        g.Unit.create(**d)


def _load_attr_types():
    for attr_type in data.attr_types:
        unit = g.Unit.get_one(label=attr_type.pop('unit'))
        attr_type['label'] = attr_type.pop('name')
        attr_type_obj = g.AttrType.create(**attr_type)
        R.IsUnit.create(attr_type_obj, unit)


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
            R.IsA.create(el, root_element_node)
        else:
            R.IsA.create(el, parent_el)

        for attr_type_name in el_dict.pop('<attr_types>', []):
            attr_type = g.AttrType.get_one(label=attr_type_name)
            R.CanHaveAttrType.create(el, attr_type)

        for attr_type_name, attr_value in el_dict.pop('<attrs>', {}).iteritems():
            res = g.AttrType.get_all(label=attr_type_name)
            if not res:
                raise Exception('Could not find attr_type %s' % attr_type_name)
            (attr_type,) = res

            # Try to find an exisiting attribute with the same value and attr_type
            attribute = None
            for attribute_2 in g.Attribute.get_all(value=attr_value) or []:
                (attr_type_2,) = attribute_2._bulbs_node.outV('HasAttrType')
                if attr_type._bulbs_node == attr_type_2:
                    attribute = attribute_2
                    break

            if not attribute:
                attribute = g.Attribute.create(value=attr_value)
                R.HasAttrType.create(attribute, attr_type)

            R.HasAttribute.create(el, attribute)

        for standard_name in el_dict.pop('<standards>', []):
            standard = g.Standard.get_one(label=standard_name)
            R.Implements.create(el, standard)

        for conn_dict in el_dict.pop('<connectors>', []):
            conn_label = conn_dict.pop('<name>')
            result = g.Connector.get_all(label=conn_label)
            if not result:
                raise Exception('Could not find connector %r to connecto %r' % (conn_label, el.label))
            (connector,) = result
            R.HasConnector.create(el, connector, quantity=conn_dict.pop('<quantity>', 1))

    for child_el_dict in el_dict.pop('<children>', []):
        _add_element(child_el_dict, el, element_type, root_element_node, extra_properties)

    assert not el_dict, el_dict


def _load_part_schema(root_part, csv_files):
    parts = treetools.inflate_tree(data.part_schema, csv_files, 'parts')
    for part_dict in parts:
        _add_element(part_dict, None, g.Part, root_part, extra_properties={'is_schema': True})


def _load_standards(root_standard, csv_files):
    standards = treetools.inflate_tree(data.standards, csv_files, 'standards')
    for standard_dict in standards:
        _add_element(standard_dict, None, g.Standard, root_standard)


def _load_connectors(root_connector, csv_files):
    connectors = treetools.inflate_tree(data.connectors, csv_files, 'connectors')
    for connector_dict in connectors:
        _add_element(connector_dict, None, g.Connector, root_connector)


def _load_operating_systems(root_os, csv_files):
    osses = treetools.inflate_tree(data.os, csv_files, 'operating_systems')
    for os_dict in osses:
        _add_element(os_dict, None, g.OperatingSystem, root_os)


def _load_parts(csv_files):
    parts = treetools.inflate_tree(data.parts, csv_files, 'parts')
    for part_dict in parts:
        part = g.Part.get_one(label=part_dict.pop('<name>'))
        for child_part_dict in part_dict.pop('<children>'):
            _add_element(child_part_dict, part, g.Part, None)

        assert not part_dict, part_dict


def _load_connection_schema(connection_schema_root):
    def _add_connection_schema(parent_part, child_part_dicts):
        for child_part_dict in child_part_dicts:
            child_part = g.Part.get_one(label=child_part_dict.pop('<name>'))
            R.CanBeContainedIn.create(child_part, parent_part)
            _add_connection_schema(child_part, child_part_dict.pop('<children>', []))

    connections = treetools.inflate_tree(data.connection_schema)
    for root_part_dict in connections:
        root_part = g.Part.get_one(label=root_part_dict.pop('<name>'))
        R.IsAConnectionSchemaRoot.create(root_part, connection_schema_root)
        _add_connection_schema(root_part, root_part_dict.pop('<children>'))

        assert not root_part_dict


def _load_connections(connection_root, systems):
    def _create_connection(system_part, parent_part, child_dict, connector):
        child_part = g.Part.get_one(label=child_dict.pop('<name>'))
        connection = g.Connection.create(quantity=child_dict.pop('<quantity>', 1))
        R.BelongsTo.create(connection, system_part)
        R.ConnectedFrom.create(parent_part, connection)
        R.ConnectedTo.create(connection, child_part)
        if connector:
            R.ConnectedVia.create(connection, connector)

        _add_connection(system_part, child_part, child_dict)
        assert not child_dict, child_dict


    def _add_connection(system_part, parent_part, part_dict):
        for child_dict in part_dict.pop('<no_connector>', []):
            _create_connection(system_part, parent_part, child_dict, None)

        for conn_dict in part_dict.pop('<connectors>', []):
            connector = g.Connector.get_one(label=conn_dict.pop('<name>'))
            for child_dict in conn_dict.pop('<children>', []):
                _create_connection(system_part, parent_part, child_dict, connector)

        assert not part_dict, part_dict


    for system_dict in systems:
        system_part = g.Part.get_one(label=system_dict.pop('<name>'))
        R.HasConnection.create(system_part, connection_root)
        _add_connection(system_part, system_part, system_dict)
        assert not system_dict, system_dict


def check_data():
    # check if the data structure is correct
    for name in 'part_schema connection_schema standards connectors parts systems'.split():
        treetools.inflate_tree(getattr(data, name))

    # check if the names are unique
    for name in 'part_schema connection_schema standards connectors parts'.split():
        treetools.inflate_tree(getattr(data, name), check_unique_names=True)


def reset_db(csv_path):
    check_data()

    root_part = g.RootPart.create()
    root_standard = g.RootStandard.create()
    root_connector = g.RootConnector.create()
    connection_root = g.ConnectionRoot.create()
    connection_schema_root = g.ConnectionSchemaRoot.create()
    operating_system_root = g.RootOperatingSystem.create()

    if os.path.isfile(csv_path):
        csv_files = read_all_files(csv_path)
    else:
        print '%s is no path, skipping reading of csv file' % csv_path
        csv_files = {}

    print '== Import units =='
    _load_units()
    print '== Import attr types =='
    _load_attr_types()
    print '== Import operating systems =='
    _load_operating_systems(operating_system_root, csv_files)
    print '== Import part schema =='
    _load_part_schema(root_part, csv_files)
    print '== Import connection schema =='
    _load_connection_schema(connection_schema_root)
    print '== Import standards =='
    _load_standards(root_standard, csv_files)
    print '== Import connectors =='
    _load_connectors(root_connector, csv_files)
    print '== Import parts =='
    _load_parts(csv_files)
    print '== Import systems from data.py =='
    systems = treetools.inflate_tree(data.systems, 'connections')
    _load_connections(connection_root, systems)

    if 'Pentium4_Willamette' in csv_files:
        print '== Import systems from csv=='
        _load_connections(connection_root, csv_files['Pentium4_Willamette']['connections'])
    else:
        print 'Warning: csv file part Pentium4_Willamette was not found, skipping import'

    print 'Finished importing'
