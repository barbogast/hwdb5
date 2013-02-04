from bulbs.model import Node, Relationship
from bulbs.property import String, Integer, DateTime, Bool


class BaseNode(Node):
    __mode__ = 'STRICT'


class LabeledNode(BaseNode):
    note = String(nullable=True)
    label = String(nullable=False)

    def __unicode__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.label)


class RootPart(BaseNode):
    element_type = 'root_part'

class Part(LabeledNode):
    element_type = "part"
    is_schema = Bool(nullable=False, default=False)

class Connector(LabeledNode):
    element_type = "connector"

class RootConnector(BaseNode):
    element_type = 'root_connector'

class Connection(BaseNode):
    element_type = "part_connection"
    quantity = Integer()

class ConnectionRoot(BaseNode):
    element_type = "connection_root"

class ConnectionSchemaRoot(BaseNode):
    element_type = "connection_schema_root"

class RootStandard(BaseNode):
    element_type = 'root_standard'

class Standard(LabeledNode):
    element_type = "standard"

class AttrType(LabeledNode):
    element_type = "attr_type"

class Company(LabeledNode):
    element_type = "company"

class Unit(LabeledNode):
    element_type = "unit"
    name = String(nullable=False)
    format = String(nullable=False)

class Attribute(BaseNode):
    element_type = "attribute"
    value = String(nullable=False)


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
    (AttrType,      HasAttrType,        AttrType),
    (AttrType,      IsUnit,             Unit),
)


g = None
