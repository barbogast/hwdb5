import six
from bulbs.model import Relationship
from bulbs.property import String, Integer, DateTime, Bool
from bulbs.model import Node as BulbsNode



class _NodeProxy(object):
    def __init__(self, graph, cls, bulbs_proxy):
        self._g = graph
        self._cls = cls
        self._bulbs_proxy = bulbs_proxy


    def __call__(self, *args, **kwargs):
        return self._cls(*args, **kwargs)


    def create(self, **kwargs):
        unique_list = self._cls._get_unique_properties()
        d = {}
        for u in unique_list:
            if kwargs.get(u, None) is None:
                raise ValueError('Unique property %r may not be None' % u)
            d[u] = kwargs[u]

        if d:
            ((name, value), ) = d.items()
            if self._bulbs_proxy.index.lookup(name, value):
                raise Exception('Duplicate entry %s' % kwargs['label'])
        bulbs_node = self._bulbs_proxy.create(**kwargs)
        return self._cls(self._g, bulbs_node)


    def get_one(self, **kwargs):
        res = self.get_all(**kwargs)
        if not res:
            raise Exception('Found no %s with %r' % (self._cls.__name__, kwargs))
        el = res.next()
        try:
            res.next()
        except StopIteration:
            return el
        else:
            raise Exception('Found multiple (%s) %s with %r' % (len(res), self._cls.__name__, kwargs))


    def get_all(self, **kwargs):
        if kwargs:
            if len(kwargs) > 1:
                raise Exception('Not supported, doesnt work with bulbs')
            name, value = kwargs.items()[0]
            i = self._bulbs_proxy.index.lookup(name, value)
        else:
            i = self._bulbs_proxy.get_all()
        return (self._cls(self._g, o) for o in i) if i else []



class Graph(object):
    def __init__(self):
        self.classes = {}
        self.names = {}


    def set_bulbs_graph(self, bulbs_graph):
        self._bg = bulbs_graph


    def set_proxy(self, cls, name, bulbs_proxy):
        proxy = _NodeProxy(self, cls, bulbs_proxy)
        setattr(self, name, proxy)


    def _make_bulbs_node(self, name, cls):
        dct = cls.properties.copy()
        dct['element_type'] = name
        dct['__mode__'] = 'STRICT'
        bubls_node_cls = type(name, (BulbsNode, ), dct)
        self._bg.add_proxy(name, bubls_node_cls)
        bulbs_proxy = getattr(self._bg, cls.__name__)
        return bulbs_proxy


    def register_class(self, cls, name=None):
        if name is None:
            name = cls.__name__

        if name in self.classes:
            raise NameError('Name %r is alread present' % name)

        self.classes[name] = cls
        self.names[cls] = name

        bulbs_proxy = self._make_bulbs_node(name, cls)
        self.set_proxy(cls, name, bulbs_proxy)


    def get_from_eid(self, eid):
        assert eid is not None
        bulbs_node = self._bg.vertices.get(eid)
        if bulbs_node is None:
            return None
        cls = self.classes[bulbs_node.element_type]
        return cls(self, bulbs_node)


    def clear(self):
        self._bg.clear()
        for name, cls in self.classes.iteritems():
            bulbs_proxy = self._make_bulbs_node(name, cls)
            self.set_proxy(cls, name, bulbs_proxy)


g = Graph()



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



class Node(six.with_metaclass(NodeMeta, object)):
    properties = {}
    _bulbs_proxy = None


    @classmethod
    def _get_unique_properties(cls):
        l = []
        for name, p in cls.properties.iteritems():
            if p.unique:
                l.append(name)
        return l


    def __init__(self, graph, bulbs_node, **kwargs):
        self.P = Properties(bulbs_node, self.properties)
        self.update(**kwargs)
        self.E = bulbs_node
        self.eid = self.P['eid']
        self._bulbs_node = bulbs_node
        self.g = graph


    def __str__(self):
        s = []
        for name in self.properties:
            s.append('%s: %s' % (name, self.P[name]))
        return "{%s %s}" % (super(Node, self).__str__(), ', '.join(s))


    def __eq__(self, node):
        return self._bulbs_node == node._bulbs_node


    def get_proxy(self):
        return getattr(self.g, self.__class__.__name__)


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
                if obj.unique and d[name] != self.P[name] and self.get_proxy().get_all(**{name: d[name]}):
                    raise ValueError('%s with %s=%s is already present' % (self.__class__.__name__, name, d[name]))

                self.P[name] = d[name]


    def save(self):
        self._bulbs_node.save()



class LabeledNode(Node):
    properties = dict(
        note = String(nullable=True),
        label = String(nullable=False, unique=True),
    )


def get_node_classes():
    class RootPart(Node): pass
    class Connector(LabeledNode): pass
    class RootConnector(Node): pass
    class ConnectionRoot(Node): pass
    class ConnectionSchemaRoot(Node): pass
    class RootStandard(Node): pass
    class Standard(LabeledNode): pass
    class AttrType(LabeledNode): pass
    class OperatingSystem(LabeledNode): pass
    class RootOperatingSystem(Node): pass

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
            return self.E.inV('IsUnit') or []

        def delete(self):
            if self.get_attr_types():
                raise Exception('Could not delete')
            else:
                g.vertices.delete(self.eid)

    return locals().values()


class _RelationshipBase(Relationship):
    @classmethod
    def get_index_name(cls, cfg):
        return cls.__name__

    @classmethod
    def get_label(cls, cfg):
        return cls.__name__

    @classmethod
    def create(cls, outV, inV, **kwargs):
        return cls._bulbs_proxy.create(outV._bulbs_node, inV._bulbs_node, None, **kwargs)


def init_relationship_classes():
    class IsA(_RelationshipBase): pass
    class BelongsTo(_RelationshipBase): pass
    class ConnectedVia(_RelationshipBase): pass
    class ConnectedFrom(_RelationshipBase): pass
    class ConnectedTo(_RelationshipBase): pass
    class HasConnection(_RelationshipBase): pass
    class Implements(_RelationshipBase): pass
    class IsUnit(_RelationshipBase): pass
    class HasAttrType(_RelationshipBase): pass
    class IsAConnectionSchemaRoot(_RelationshipBase): pass
    class CanHaveAttrType(_RelationshipBase): pass
    class HasAttribute(_RelationshipBase): pass
    class CanBeContainedIn(_RelationshipBase): pass
    class HasConnector(_RelationshipBase):
        quantity = Integer(nullable=False)

    R.update(locals())


class Classes(dict):
    def __getattr__(self, name):
        return self[name]


#N = Classes()
R = Classes()


class Relationships(object):
    def _init_relationships(self):
        relationships = (
            (N.Standard,      '1', R.IsA,                '*', N.Standard),
            (N.Standard,      '1', R.IsA,                '*', N.RootStandard),
            (N.Connector,     '1', R.IsA,                '*', N.Connector),
            (N.Connector,     '1', R.IsA,                '*', N.RootConnector),
            (N.Part,          '1', R.IsA,                '*', N.Part),
            (N.Part,          '*', R.CanBeContainedIn,   '*', N.Part),
            (N.Part,          '1', R.IsA,                '*', N.RootPart),
            (N.Part,          '1', R.IsA,                '*', N.ConnectionSchemaRoot),
            (N.Part,          '*', R.HasConnection,      '*', N.ConnectionRoot),
            (N.Part,          '*', R.HasConnector,       '*', N.Connector),
            (N.Part,          '*', R.Implements,         '*', N.Standard),
            (N.Part,          '*', R.HasAttribute,       '*', N.Attribute),
            (N.Part,          '*', R.CanHaveAttrTyp,     '*', N.AttrType,),
            (N.Connection,    '1', R.BelongsTo,          '*', N.Part),
            (N.Connection,    '1', R.ConnectedVia,       '*', N.Connector),
            (N.Connection,    '1', R.ConnectedFrom,      '*', N.Part),
            (N.Connection,    '1', R.ConnectedTo,        '*', N.Part),
            (N.Attribute,     '1', R.HasAttrType,        '*', N.AttrType),
            (N.AttrType,      '1', R.IsUnit,             '*', N.Unit),
        )

    def get_in(self, cls):
        rels = []
        for out_node, out_number, edge, in_number, in_node in self.relationships:
            if in_node == cls:
                rels.append((out_node, out_number, in_number, edge))

        return rels

    #def get_mandatory_rels(self, cls):
    #    rels = []
    #    for out_node, out_number, edge, in_number, in_node in self.relationships:



def init_graph(graph):
    engine = 'neo4j'
    #engine = 'rexster'

    if engine == 'rexster':
        from bulbs.rexster import Graph as BulbsGraph, Config
        url = 'http://localhost:8182/graphs/hwdbgraph'
    elif engine == 'neo4j':
        from bulbs.neo4jserver import Graph as BulbsGraph, Config
        url = 'http://localhost:7474/db/data/'
    else:
        raise Exception('Unknown engine %s' % engine)

    config = Config(url)
    bg = BulbsGraph(config)

    from logging import DEBUG, ERROR, FileHandler, NullHandler
    bg.config.set_logger(ERROR, NullHandler)

    graph.set_bulbs_graph(bg)

    for node_cls in get_node_classes():
        graph.register_class(node_cls)

    for name, rel_cls in R.iteritems():
        bg.add_proxy(name, rel_cls)
        rel_cls._bulbs_proxy = getattr(bg, name)
