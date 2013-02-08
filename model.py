import six
from bulbs.model import Node as BulbsNode, Relationship
from bulbs.property import String, Integer, DateTime, Bool



class BaseBulbsNode(BulbsNode):
    __mode__ = 'STRICT'


class LabeledBulbsNode(BaseBulbsNode):
    note = String(nullable=True)
    label = String(nullable=False, unique=True)


########################################################################
node_classes = []


def make_bulbs_node_class(name, element_type, properties):
    dct = properties.copy()
    dct['element_type'] = element_type
    return type('Bulbs'+name, (BulbsNode, ), dct)


class NodeMeta(type):
    def __init__(cls, name, bases, dct):
        properties = getattr(cls, 'properties', {})
        for base in bases:
            properties.update(getattr(base, 'properties', {}))

        if hasattr(cls, 'element_type'):
            node_classes.append(cls)


class Properties(object):
    def __init__(self, bulbs_node):
        object.__setattr__(self, '_bnode', bulbs_node)

    def __getattr__(self, name):
        return getattr(self._bnode, name)

    def __setattr__(self, name, value):
        return setattr(self._bnode, name, value)

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def __contains__(self, name):
        return hasattr(self._bnode, name)


class Node(six.with_metaclass(NodeMeta, object)):
#class Node(object):
#    __metaclass__ = NodeMeta
    __mode__ = 'STRICT'
    proxy_name = None


    @classmethod
    def get_proxy_name(cls):
        return cls.proxy_name or cls.element_type + 's'


    @classmethod
    def _get_proxy(cls):
        return getattr(g, cls.get_proxy_name())


    @classmethod
    def from_eid(cls, eid):
        bulbs_node = g.vertices.get(eid)
        if bulbs_node is None:
            return None
        return cls(bulbs_node)


    @classmethod
    def create(cls, **kwargs):
        bulbs_node = cls._get_proxy().create(kwargs)
        return cls(bulbs_node)


    def __init__(self, bulbs_node):
        self.P = Properties(bulbs_node)
        self.E = bulbs_node
        self.eid = bulbs_node.eid
        self._bulbs_node = bulbs_node


    def get(self, key, default=None):
        if key in self.P:
            return self.P[key]
        else:
            return default


    def update(self, d):
        for key in self.properties:
            if key in d:
                self.P[key] = d[key]


    def save(self):
        self._bulbs_node.save()



class LabeledNode(Node):
    properties = dict(
        note = String(nullable=True),
        label = String(nullable=False, unique=True),
    )

    @classmethod
    def create(cls, **kwargs):
        if cls._get_proxy().index.lookup(label=kwargs['label']):
            raise Exception('Duplicate entry %s' % kwargs['label'])
        bulbs_node = cls._get_proxy().create(kwargs)
        return cls(bulbs_node)

    @classmethod
    def from_label(cls, label):
        res = cls._get_proxy().index.lookup(label=label)
        if not res:
            return None
        res = list(res)
        if len(res) != 1:
            raise Exception('Found multiple (%s) %s with label %s' % (len(res), cls.__name__, label))
        return cls(res[0])

    @classmethod
    def get_count_from_label(cls, label):
        return len(list(cls._get_proxy().index.lookup(label=label) or []))

    def __unicode__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.label)

    def update(self, d):
        if d['label'] != self.P.label and self.get_count_from_label(d['label']) > 0:
            raise Exception('%s with label=%s is already present' % (self.__class__.__name__, d['label']))
        super(LabeledNode, self).update(d)


class Unit(LabeledNode):
    element_type = "unit"

    properties = dict(
        name = String(nullable=False),
        format = String(nullable=False),
    )

    def get_attr_types(self):
        return self.E.inV('is_unit') or []

    def delete(self):
        if self.get_attr_types():
            raise Exception('Could not delete')
        else:
            g.vertices.delete(self.eid)



class RootPart(BaseBulbsNode):
    element_type = 'root_part'
    proxy_name = element_type + 's'

class Part(LabeledBulbsNode):
    element_type = "part"
    proxy_name = element_type + 's'
    is_schema = Bool(nullable=False, default=False)

class Connector(LabeledBulbsNode):
    element_type = "connector"
    proxy_name = element_type + 's'

class RootConnector(BaseBulbsNode):
    element_type = 'root_connector'
    proxy_name = element_type + 's'

class Connection(BaseBulbsNode):
    element_type = "connection"
    proxy_name = element_type + 's'
    quantity = Integer()

class ConnectionRoot(BaseBulbsNode):
    element_type = "connection_root"
    proxy_name = element_type + 's'

class ConnectionSchemaRoot(BaseBulbsNode):
    element_type = "connection_schema_root"
    proxy_name = element_type + 's'

class RootStandard(BaseBulbsNode):
    element_type = 'root_standard'
    proxy_name = element_type + 's'

class Standard(LabeledBulbsNode):
    element_type = "standard"
    proxy_name = element_type + 's'

class AttrType(LabeledBulbsNode):
    element_type = "attr_type"
    proxy_name = element_type + 's'

'''class Unit(LabeledBulbsNode):
    element_type = "unit"
    proxy_name = element_type + 's'
    name = String(nullable=False)
    format = String(nullable=False)

    def get_attr_types(self):
        return self.inV('is_unit') or []

    def delete(self):
        if self.get_attr_types():
            raise Exception('Could not delete')
        else:
            g.vertices.delete(self.eid)'''


class Attribute(BaseBulbsNode):
    element_type = "attribute"
    proxy_name = element_type + 's'
    value = String(nullable=False)

bulbs_node_classes = (
    RootPart, Part, Connector, RootConnector, Connection, ConnectionRoot,
    ConnectionSchemaRoot, RootStandard, Standard, AttrType, Attribute
)


class IsA(Relationship): label = "is_a"
class BelongsTo(Relationship): label = "belongs_to"
class ConnectedVia(Relationship): label = "connected_via"
class ConnectedFrom(Relationship): label = "connected_from"
class ConnectedTo(Relationship): label = "connected_to"
class HasConnection(Relationship): label = "has_connection"
class Implements(Relationship): label = "implements"
class IsUnit(Relationship): label = "is_unit"
class HasAttrType(Relationship): label = "has_attr_type"
class CanHaveAttrTyp(Relationship): label = "can_have_attr_type"
class HasAttribute(Relationship): label = "has_attribute"
class CanBeContainedIn(Relationship): label = "can_be_contained_in"
class HasConnector(Relationship):
    label = 'has_connector'
    quantity = Integer(nullable=False)

relationship_classes = (
    IsA, BelongsTo, ConnectedVia, ConnectedFrom, ConnectedTo, HasConnection,
    Implements, IsUnit, HasAttrType, CanHaveAttrTyp, CanBeContainedIn,
    HasAttribute, HasConnector
)

relationships = (
    (Standard,      '1', IsA,                '*', Standard),
    (Standard,      '1', IsA,                '*', RootStandard),
    (Connector,     '1', IsA,                '*', Connector),
    (Connector,     '1', IsA,                '*', RootConnector),
    (Part,          '1', IsA,                '*', Part),
    (Part,          '*', CanBeContainedIn,   '*', Part),
    (Part,          '1', IsA,                '*', RootPart),
    (Part,          '1', IsA,                '*', ConnectionSchemaRoot),
    (Part,          '*', HasConnection,      '*', ConnectionRoot),
    (Part,          '*', HasConnector,       '*', Connector),
    (Part,          '*', Implements,         '*', Standard),
    (Part,          '*', HasAttribute,       '*', Attribute),
    (Part,          '*', CanHaveAttrTyp,     '*', AttrType,),
    (Connection,    '1', BelongsTo,          '*', Part),
    (Connection,    '1', ConnectedVia,       '*', Connector),
    (Connection,    '1', ConnectedFrom,      '*', Part),
    (Connection,    '1', ConnectedTo,        '*', Part),
    (Attribute,     '1', HasAttrType,        '*', AttrType),
    (AttrType,      '1', IsUnit,             '*', Unit),
)


g = None
