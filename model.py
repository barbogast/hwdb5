from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime, Bool



class BaseNode(Node):
    __mode__ = 'STRICT'

    @classmethod
    def get_proxy(cls):
        return getattr(g, cls.proxy_name)

    @classmethod
    def from_eid(cls, eid):
        return g.vertices.get(eid)

    @classmethod
    def create(cls, **kwargs):
        return cls.get_proxy().create(kwargs)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self, key, default=None):
        if hasattr(self, key):
            v = getattr(self, key)
            return default if v is None else v
        else:
            return default

    def update(self, d):
        for key in self.get_property_keys():
            if key in d:
                self[key] = d[key]


class LabeledNode(BaseNode):
    note = String(nullable=True)
    label = String(nullable=False, unique=True)

    @classmethod
    def create(cls, **kwargs):
        if cls.get_proxy().index.lookup(label=kwargs['label']):
            raise Exception('Duplicate entry %s' % kwargs['label'])
        return cls.get_proxy().create(kwargs)

    @classmethod
    def from_label(cls, label):
        res = cls.get_proxy().index.lookup(label=label)
        if not res:
            return None
        res = list(res)
        if len(res) != 1:
            raise Exception('Found multiple (%s) %s with label %s' % (len(res), cls.__name__, label))
        return res[0]

    @classmethod
    def get_count_from_label(cls, label):
        return len(list(cls.get_proxy().index.lookup(label=label) or []))

    def __unicode__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.label)

    def update(self, d):
        if d['label'] != self.label and self.get_count_from_label(d['label']) > 0:
            raise Exception('%s with label=%s is already present' % (self.__class__.__name__, d['label']))
        super(LabeledNode, self).update(d)


class RootPart(BaseNode):
    element_type = 'root_part'
    proxy_name = element_type + 's'

class Part(LabeledNode):
    element_type = "part"
    proxy_name = element_type + 's'
    is_schema = Bool(nullable=False, default=False)

class Connector(LabeledNode):
    element_type = "connector"
    proxy_name = element_type + 's'

class RootConnector(BaseNode):
    element_type = 'root_connector'
    proxy_name = element_type + 's'

class Connection(BaseNode):
    element_type = "connection"
    proxy_name = element_type + 's'
    quantity = Integer()

class ConnectionRoot(BaseNode):
    element_type = "connection_root"
    proxy_name = element_type + 's'

class ConnectionSchemaRoot(BaseNode):
    element_type = "connection_schema_root"
    proxy_name = element_type + 's'

class RootStandard(BaseNode):
    element_type = 'root_standard'
    proxy_name = element_type + 's'

class Standard(LabeledNode):
    element_type = "standard"
    proxy_name = element_type + 's'

class AttrType(LabeledNode):
    element_type = "attr_type"
    proxy_name = element_type + 's'

class Unit(LabeledNode):
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
            g.vertices.delete(self.eid)


class Attribute(BaseNode):
    element_type = "attribute"
    proxy_name = element_type + 's'
    value = String(nullable=False)

node_classes = (
    RootPart, Part, Connector, RootConnector, Connection, ConnectionRoot,
    ConnectionSchemaRoot, RootStandard, Standard, AttrType, Unit, Attribute
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
    (Standard,      IsA,                Standard),
    (Standard,      IsA,                RootStandard),
    (Connector,     IsA,                Connector),
    (Connector,     IsA,                RootConnector),
    (Part,          IsA,                Part),
    (Part,          CanBeContainedIn,   Part),
    (Part,          IsA,                RootPart),
    (Part,          IsA,                ConnectionSchemaRoot),
    (Part,          HasConnection,      ConnectionRoot),
    (Part,          HasConnector,       Connector),
    (Part,          Implements,         Standard),
    (Part,          HasAttribute,       Attribute),
    (Part,          CanHaveAttrTyp,     AttrType,),
    (Connection,    BelongsTo,          Part),
    (Connection,    ConnectedVia,       Connector),
    (Connection,    ConnectedFrom,      Part),
    (Connection,    ConnectedTo,        Part),
    (Attribute,     HasAttrType,        AttrType),
    (AttrType,      IsUnit,             Unit),
)


g = None
