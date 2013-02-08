import six
from bulbs.model import Node as BulbsNode, Relationship
from bulbs.property import String, Integer, DateTime, Bool



def make_bulbs_node_class(name, properties):
    dct = properties.copy()
    dct['element_type'] = name
    return type('Bulbs'+name, (BulbsNode, ), dct)


class NodeMeta(type):
    def __init__(cls, name, bases, dct):
        properties = getattr(cls, 'properties', {})
        for base in bases:
            properties.update(getattr(base, 'properties', {}))



class Properties(object):
    def __init__(self, bulbs_node):
        object.__setattr__(self, '_bnode', bulbs_node)

    def __str__(self):
        return str(self._bnode)

    def __getattr__(self, name):
        return getattr(self._bnode, name)

    def __setattr__(self, name, value):
        return setattr(self._bnode, name, value)

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def __contains__(self, name):
        return hasattr(self._bnode, name)


class Edge(object):
    def __init__(self, bulbs_node):
        self._bnode = bulbs_node

    def inV(self, s):
        return


class Node(six.with_metaclass(NodeMeta, object)):
#class Node(object):
#    __metaclass__ = NodeMeta
    __mode__ = 'STRICT'
    proxy_name = None
    properties = {}


    @classmethod
    def get_proxy_name(cls):
        return cls.__name__


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
        bulbs_node = cls._get_proxy().create(**kwargs)
        return cls(bulbs_node)


    @classmethod
    def get_one(cls):
        res = cls._get_proxy().get_all()
        if not res:
            raise Exception('Found no %s with label %s' % (cls.__name__, label))
        el = cls(res.next())
        try:
            res.next()
        except StopIteration:
            return el
        else:
            raise Exception('Found multiple (%s) %s with label %s' % (len(res), cls.__name__, label))


    @classmethod
    def get_all(cls, **kwargs):
        if kwargs:
            if len(kwargs) > 1:
                raise Exception('Not supported, doesnt work with bulbs')
            name, value = kwargs.items()[0]
            i = cls._get_proxy().index.lookup(name, value)
        else:
            i = cls._get_proxy().get_all()
        return (cls(o) for o in i or [])


    def __init__(self, bulbs_node):
        self.P = Properties(bulbs_node)
        self.E = bulbs_node
        self.eid = bulbs_node.eid
        self._bulbs_node = bulbs_node


    def __str__(self):
        s = []
        for name in self.properties:
            s.append('%s: %s' % (name, self.P[name]))
        return "%s %s" % (super(Node, self).__str__(), ', '.join(s))


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
        bulbs_node = cls._get_proxy().create(**kwargs)
        return cls(bulbs_node)


    @classmethod
    def one_from_label(cls, label):
        res = cls._get_proxy().index.lookup(label=label)
        if not res:
            raise Exception('Found no %s with label %s' % (cls.__name__, label))
        el = cls(res.next())
        try:
            res.next()
        except StopIteration:
            return el
        else:
            raise Exception('Found multiple (%s) %s with label %s' % (len(res), cls.__name__, label))


    @classmethod
    def all_from_label(cls, label):
        res = cls._get_proxy().index.lookup(label=label)
        if not res:
            return
        else:
            return (cls(o) for o in res)


    def __unicode__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.label)

    def update(self, d):
        if d['label'] != self.P.label and self.all_from_label(d['label']):
            raise Exception('%s with label=%s is already present' % (self.__class__.__name__, d['label']))
        super(LabeledNode, self).update(d)


def _get_node_classes():
    class RootPart(Node): pass
    class Connector(LabeledNode): pass
    class RootConnector(Node): pass
    class ConnectionRoot(Node): pass
    class ConnectionSchemaRoot(Node): pass
    class RootStandard(Node): pass
    class Standard(LabeledNode): pass
    class AttrType(LabeledNode): pass

    class Part(LabeledNode):
        properties = dict(
            is_schema = Bool(nullable=False, default=False)
        )

    class Connection(Node):
        properties = dict(
            quantity = Integer()
        )

    class Attribute(Node):
        properties = dict(
            value = String(nullable=False)
        )

    class Unit(LabeledNode):
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

    class_list = locals()
    class Nodes(object):
        classes = class_list
        def __getattr__(self, name):
            return class_list[name]

        def iteritems(self):
            return class_list.iteritems()

        def __iter__(self):
            return iter(class_list)

    return Nodes()

N = _get_node_classes()

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
    (N.Standard,      '1', IsA,                '*', N.Standard),
    (N.Standard,      '1', IsA,                '*', N.RootStandard),
    (N.Connector,     '1', IsA,                '*', N.Connector),
    (N.Connector,     '1', IsA,                '*', N.RootConnector),
    (N.Part,          '1', IsA,                '*', N.Part),
    (N.Part,          '*', CanBeContainedIn,   '*', N.Part),
    (N.Part,          '1', IsA,                '*', N.RootPart),
    (N.Part,          '1', IsA,                '*', N.ConnectionSchemaRoot),
    (N.Part,          '*', HasConnection,      '*', N.ConnectionRoot),
    (N.Part,          '*', HasConnector,       '*', N.Connector),
    (N.Part,          '*', Implements,         '*', N.Standard),
    (N.Part,          '*', HasAttribute,       '*', N.Attribute),
    (N.Part,          '*', CanHaveAttrTyp,     '*', N.AttrType,),
    (N.Connection,    '1', BelongsTo,          '*', N.Part),
    (N.Connection,    '1', ConnectedVia,       '*', N.Connector),
    (N.Connection,    '1', ConnectedFrom,      '*', N.Part),
    (N.Connection,    '1', ConnectedTo,        '*', N.Part),
    (N.Attribute,     '1', HasAttrType,        '*', N.AttrType),
    (N.AttrType,      '1', IsUnit,             '*', N.Unit),
)


g = None
