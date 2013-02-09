from unittest import TestCase, expectedFailure
from logging import DEBUG

from bulbs.property import String, Integer, DateTime, Bool
from bulbs.model import Node as BulbsNode

from model import Node, Properties
from db import make_bulbs_node_class



class MyNode(Node):
    properties = dict(
        prop1 = String(nullable=False),
        prop2 = Integer(),
    )

class MyNode2(Node):
    properties = dict(
        prop1 = String(nullable=False),
        prop2 = Integer(unique=True),
    )


def init_test_graph(engine='neo4j'):
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

    for name, node_cls in (('MyNode', MyNode), ('MyNode2', MyNode2)):
        bubls_node_cls = make_bulbs_node_class(name='Bulbs'+name,
                                               properties=node_cls.properties)
        g.add_proxy(node_cls.__name__, bubls_node_cls)
        node_cls._bulbs_proxy = getattr(g, node_cls.__name__)

    return g


class Test_NodeMeta(TestCase):
    def test_(self):
        class Node:
            properties = dict(a=String())
        
    
    def test_2(self):
        class MyNode(Node): 
            properties = dict(a=String())
        
    
    def test_inheritance(self):
        class MyBaseNode(Node): 
            properties = dict(a=String())
        
        class MyNode(MyBaseNode): 
            properties = dict(b=Integer())
        
        self.assertEqual(MyBaseNode.properties.keys(), ['a'])
        self.assertEqual(sorted(MyNode.properties.keys()), ['a', 'b'])
        
    
    def test_inheritance_overriding_properties(self):
        class MyBaseNode(Node): 
            properties = dict(a=String())
        
        with self.assertRaises(AttributeError) as e:
            class MyNode(MyBaseNode): 
                properties = dict(a=Integer())
            
            
    def test_only_one_unique_property(self):
        with self.assertRaises(Exception) as e:
            class MyNode(Node):
                properties = dict(
                    a=String(unique=True),
                    b=String(unique=True),
                )
        
    
class Test_Node(TestCase):
    assert_equal = TestCase.assertEqual
    assert_not_equal = TestCase.assertNotEqual
    
    def setUp(self):
        self.g = init_test_graph()
        import model
        model.g = self.g
        self.g.clear()
        self.g = init_test_graph()
        
    def test_get_one(self):
        node = MyNode.create(prop1='x')
        self.assert_equal(MyNode.get_one(), node)
        
        MyNode.create(prop1='y')
        self.assert_equal(MyNode.get_one(prop1='x'), node)

    def test_get_one_of_none(self):
        """ Node.get_one() should raise an Exception if it finds 
        no Node in the db """
        self.assertRaises(Exception, MyNode.get_one)
        
    def test_get_one_of_two(self):
        """ Node.get_one() should raise an Exception if it finds 
        multiple Nodes in the db """
        node1 = MyNode.create(prop1='x')
        node2 = MyNode.create(prop1='y')
        self.assertRaises(Exception, MyNode.get_one)

    def test_eq(self):
        """ test Node.__eq__ """
        node1 = MyNode.create(prop1='x')
        node2 = MyNode.create(prop1='y')
        
        (returned_node1,) = MyNode.get_all(prop1='x')
        (returned_node2,) = MyNode.get_all(prop1='y')
        
        self.assert_equal(node1, returned_node1)
        self.assert_equal(node2, returned_node2)
        self.assert_not_equal(node1, returned_node2)
        
    def test_get_all(self):
        nodes = set([
            MyNode.create(prop1='x'),
            MyNode.create(prop1='y'),
        ])
        result = list(MyNode.get_all())
        for n in nodes:
            self.assertIn(n, result)
            
    def test_get_all_with_property(self):
        node1 = MyNode.create(prop1='x')
        node2 = MyNode.create(prop1='y')
        
        result = list(MyNode.get_all(prop1='y'))
        self.assertEqual(result, [node2])
        
    @expectedFailure
    def test_get_all_with_multiple_properties(self):
        node1 = MyNode.create(prop1='x', prop2=1)
        node2 = MyNode.create(prop1='x')
        
        result = list(MyNode.get_all(prop1='x', prop2=1))
        self.assertEqual(result, [node1])
        
    def test_get_all_with_property_none(self):
        node1 = MyNode.create(prop1='x')
        result = list(MyNode.get_all(prop1='y'))
        self.assertEqual(result, [])
        
    def test_get_all_of_none(self):
        self.assertEqual(MyNode.get_all(), [])
        
    def test_get_unique_properties(self):
        l = MyNode2._get_unique_properties()
        self.assertEqual(['prop2',], l)
        

    def test_update(self):
        n = MyNode(BulbsNode(None), prop1='x')
        n.update(prop1='xx', prop2='y')
        self.assertEqual(n.P['prop1'], 'xx')
        self.assertEqual(n.P['prop2'], 'y')
        
        n.update({'prop1': 'xxx'})
        self.assertEqual(n.P['prop1'], 'xxx')
        
        # No exception
        n.update({'wrong_prop': 'xxx'})
        
        
    def test_update_unique(self):
        n1 = MyNode2.create(prop1='x', prop2=1)
        
        n2 = MyNode2.create(prop1='x', prop2=2)
        n2.update(prop1='xx', prop2=3) # change to a new unique value
        n2.save()
        
        n2.update(prop2=3) # change to a same value
        n2.save()
        
        with self.assertRaises(ValueError):
            n2.update(prop2=1) # change to a value already present
            
        
    def test_create_with_unique(self):
        with self.assertRaises(ValueError):
            # unique values may not be None
            MyNode2.create()
            
        MyNode2.create(prop1='x', prop2=1)
        MyNode2.create(prop1='x', prop2=2)
        
        with self.assertRaises(Exception):
            MyNode2.create(prop1='x', prop2=1)
            
        
    
class Test_Properties(TestCase):
    def test_set_not_allowed(self):
        properties = dict(
            prop1 = String(nullable=False),
            prop2 = Integer(unique=True),
        )
    
        p = Properties(BulbsNode(None), properties)
        self.assertIn('prop1', p)
        self.assertEqual(p.prop1, None)
        
        p.prop1 = 'x'
        
        self.assertEqual(p.prop1, 'x')
        self.assertEqual(p._bnode.prop1, 'x')
        
        self.assertEqual(p['prop1'], 'x')
        p['prop1'] = 'y'
        self.assertEqual(p['prop1'], 'y')
                
        with self.assertRaises(AttributeError) as e:
            p.unknown_prop = 'x'
    
