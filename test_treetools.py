import unittest

from treetools import inflate_tree, WrongTreeError, MixedBracketsError



def _deep_sort(el):
    """ Recurses the data structure into lists and dicts and sorts all
    lists """
    def _sort(ell):
        if isinstance(ell, list):
            for x in ell:
                _sort(x)
            ell.sort()
        elif isinstance(ell, dict):
            for v in ell.values():
                sort(v)
        elif isinsance(ell, basestring):
            pass
        else:
            raise Exception('Datatype %s not supported.'%type(ell))


class Test_inflate_tree(unittest.TestCase):
    def test_simple_list(self):
        t = ['A', 'B', 'C', 'D']
        expected = [{'<name>': 'A'}, {'<name>': 'B'}, {'<name>': 'C'}, {'<name>': 'D'}]
        self.assertEqual(expected, inflate_tree(t))


    def test_with_dict(self):
        # List containing elements and a subdict
        t = [
            'A',
            'B',
            {
            'C': ['C1', 'C2'],
            'D': ['D1', 'D2'],
            }
        ]
        expected = [
            {'<name>': 'A'},
            {'<name>': 'B'},
            {'<name>': 'C', '<children>': [ {'<name>': 'C1'}, {'<name>': 'C2'}]},
            {'<name>': 'D', '<children>': [ {'<name>': 'D1'}, {'<name>': 'D2'}]},
        ]
        result = inflate_tree(t)
        self.assertEqual(_deep_sort(expected), _deep_sort(result))



    def test_with_subdict(self):
        # Dict with subdicts
        t = [{
            'A': ['A1', 'A2'],
            'B': ['B1', 'B2'],
            'C': [{
                'C1': ['C11', 'C12'],
                'C2': ['C21', 'C22'],
            }],
        }]
        expected = [
            {'<name>': 'A', '<children>': [{'<name>': 'A1'}, {'<name>': 'A2'}]},
            {'<name>': 'B', '<children>': [{'<name>': 'B1'}, {'<name>': 'B2'}]},
            {'<name>': 'C', '<children>': [
                {'<name>': 'C1', '<children>': [{'<name>': 'C11'}, {'<name>': 'C12'}]},
                {'<name>': 'C2', '<children>': [{'<name>': 'C21'}, {'<name>': 'C22'}]},
            ]}
        ]
        result = inflate_tree(t)
        self.assertEqual(_deep_sort(expected), _deep_sort(result))



    def test_with_properties(self):
        # Elements with properties
        t = [{
            'A': {'<attr1>': ('a', 'b')},
            'B': {
                '<attr2>': ('a', 'b'),
                '<children>': [
                    'B1',
                    {'B2': ['B21', 'B22']},
                ]
            },
            'C': ['C1', 'C2'],
            'D': ['D1', {'D2': ['D21', 'D22']}]
            },
            'E',
        ]
        expected = [{
                '<name>': 'A',
                '<attr1>': ('a', 'b')
            },{
                '<name>': 'B',
                '<attr2>': ('a', 'b'),
                '<children>': [
                    {'<name>': 'B1'},
                    {'<name>': 'B2',
                     '<children>': [{'<name>': 'B21'}, {'<name>': 'B22'}]},
                ]
            },{
                '<name>': 'C',
                '<children>': [{'<name>': 'C1'},{'<name>': 'C2'},]
            },{
                '<name>': 'D',
                '<children>': [
                    {'<name>': 'D1'},
                    {'<name>': 'D2',
                     '<children>': [{'<name>': 'D21'}, {'<name>': 'D22'}]},
                ]
            },
            {'<name>': 'E'},
        ]

        result = inflate_tree(t)
        self.assertEqual(_deep_sort(expected), _deep_sort(result))


    def test_raises_inner_dict_not_list(self):
        # Error: inner dict is not contained in list
        t = [{
            'C': { '<children>': {
                'C1': ['C11', 'C12'],
                'C2': ['C21', 'C22'],
            }},
        }]
        self.assertRaises(WrongTreeError, inflate_tree, t)


    def test_raises_inner_dict_not_list(self):
        # Error: inner dict is not contained in list
        t = [{
            'C': { '<children>': {
                'C1': ['C11', 'C12'],
                'C2': ['C21', 'C22'],
            }},
        }]
        self.assertRaises(WrongTreeError, inflate_tree, t)


    def test_raises_mixed_properties_with_elements(self):
        # Error: mixed properties with elements in one dict
        t = [{
            'A': {'<attr1>': ('a', 'b'),
                  'A1': ['A11', 'A12']},
        }]
        self.assertRaises(MixedBracketsError, inflate_tree, t)
