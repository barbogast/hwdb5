import six
from bulbs.model import Node as BulbsNode, Relationship
from bulbs.property import String, Integer, DateTime, Bool



def make_bulbs_node_class(name, properties):
    dct = properties.copy()
    dct['element_type'] = name
    return type('Bulbs'+name, (BulbsNode, ), dct)


class NodeMeta(type):
    def __new__(meta, name, bases, dct):
        properties = dct.get('properties', {})
        for base in bases:
            for k, v in getattr(base, 'properties', {}).iteritems():
                if k in properties:
                    raise AttributeError('Overiding attributes (%r) is not allowed (should it?)' % k)
                properties[k] = v


        unique = None
        for key, obj in properties.iteritems():
            if obj.unique:
                if unique is not None:
                    raise Exception('Multiple unique properties %s, %s in %s. Only one unique property is allowed at the moment. Bulbs does not allow to select nodes more than one property' % (unique, key, name))
                unique = key

        return super(NodeMeta, meta).__new__(meta, name, bases, dct)


class Properties(object):
    def __init__(self, bulbs_node, allowed_properties):
        object.__setattr__(self, '_bnode', bulbs_node)
        object.__setattr__(self, '_allowed_properties', allowed_properties)

    def __str__(self):
        return str(self._bnode)

    def __getattr__(self, name):
        return getattr(self._bnode, name, None)

    def __setattr__(self, name, value):
        if not name in self._allowed_properties:
            raise AttributeError('Attribute %s not allowed for this node. Allowed attributes: %r' % (name, self._allowed_attributes))
        setattr(self._bnode, name, value)

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def __contains__(self, name):
        return name in self._allowed_properties


class Edge(object):
    def __init__(self, bulbs_node):
        self._bnode = bulbs_node

    def inV(self, s):
        return


class Node(six.with_metaclass(NodeMeta, object)):
    __mode__ = 'STRICT'
    properties = {}
    _bulbs_proxy = None


    @classmethod
    def _get_unique_properties(cls):
        l = []
        for name, p in cls.properties.iteritems():
            if p.unique:
                l.append(name)
        return l


    @classmethod
    def from_eid(cls, eid):
        assert eid is not None
        bulbs_node = g.vertices.get(eid)
        if bulbs_node is None:
            return None
        return cls(bulbs_node)


    @classmethod
    def create(cls, **kwargs):
        unique_list = cls._get_unique_properties()
        d = {}
        for u in unique_list:
            if kwargs.get(u, None) is None:
                raise ValueError('Unique property %r may not be None' % u)
            d[u] = kwargs[u]

        if d:
            ((name, value), ) = d.items()
            if cls._bulbs_proxy.index.lookup(name, value):
                raise Exception('Duplicate entry %s' % kwargs['label'])
        bulbs_node = cls._bulbs_proxy.create(**kwargs)
        return cls(bulbs_node)


    @classmethod
    def get_one(cls, **kwargs):
        res = cls.get_all(**kwargs)
        if not res:
            raise Exception('Found no %s with %r' % (cls.__name__, kwargs))
        el = res.next()
        try:
            res.next()
        except StopIteration:
            return el
        else:
            raise Exception('Found multiple (%s) %s with %r' % (len(res), cls.__name__, kwargs))


    @classmethod
    def get_all(cls, **kwargs):
        if kwargs:
            if len(kwargs) > 1:
                raise Exception('Not supported, doesnt work with bulbs')
            name, value = kwargs.items()[0]
            i = cls._bulbs_proxy.index.lookup(name, value)
        else:
            i = cls._bulbs_proxy.get_all()
        return (cls(o) for o in i) if i else []


    def __init__(self, bulbs_node, **kwargs):
        self.P = Properties(bulbs_node, self.properties)
        self.update(**kwargs)
        self.E = bulbs_node
        self.eid = self.P['eid']
        self._bulbs_node = bulbs_node


    def __str__(self):
        s = []
        for name in self.properties:
            s.append('%s: %s' % (name, self.P[name]))
        return "{%s %s}" % (super(Node, self).__str__(), ', '.join(s))


    def __eq__(self, node):
        return self._bulbs_node == node._bulbs_node


    def get(self, key, default=None):
        if key in self.P:
            return self.P[key]
        else:
            return default


    def update(self, d=None, **kwargs):
        d = d.copy() if d else {}
        d.update(kwargs)

        for name, obj in self.properties.iteritems():
            if name in d:
                # Check that altered unique properties are not already present in the db with the new value
                if obj.unique and d[name] != self.P[name] and self.get_all(**{name: d[name]}):
                    raise ValueError('%s with %s=%s is already present' % (self.__class__.__name__, name, d[name]))

                self.P[name] = d[name]


    def save(self):
        self._bulbs_node.save()



class LabeledNode(Node):
    properties = dict(
        note = String(nullable=True),
        label = String(nullable=False, unique=True),
    )


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
