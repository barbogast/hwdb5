import time
import json
import unittest

import model
import ui


model.init_relationship_classes()
model.init_graph(model.g)



class UiTestCase(unittest.TestCase):
    def setUp(self):
        ui.app.config['TESTING'] = True
        ui.app.debug = True
        ui.app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        ui.app.secret_key = 'Todo'
        self.app = ui.app.test_client()
        

    def test_index(self):
        rv = self.app.get('/')
        self.assertIn('Index', rv.data)

    def test_json_parts(self):
        rv = self.app.get('/json?type=parts')
        json_data = json.loads(rv.data)
        
    def test_json_standards(self):
        rv = self.app.get('/json?type=standards')
        json_data = json.loads(rv.data)

    def test_json_connectors(self):
        rv = self.app.get('/json?type=connectors')
        json_data = json.loads(rv.data)
        
    def test_json_os(self):
        rv = self.app.get('/json?type=os')
        json_data = json.loads(rv.data)
        
    def test_json_part_schema(self):
        rv = self.app.get('/json?type=part_schema')
        json_data = json.loads(rv.data)
        
    def test_json_connection_schema(self):
        rv = self.app.get('/json?type=connection_schema')
        json_data = json.loads(rv.data)
        
    def test_json_connections(self):
        rv = self.app.get('/json?type=connections')
        json_data = json.loads(rv.data)
        
    def test_json_attributes(self):
        rv = self.app.get('/json?type=attributes')
        
    def test_attr_types(self):
        rv = self.app.get('/schema/attr_types')
        self.assertIn('Attribute Types', rv.data)
        
    def test_units(self):
        rv = self.app.get('/schema/units')
        self.assertIn('Units', rv.data)
        
    def test_units_delete_not_allowed(self):
        one_unit = model.g.Unit.get_all().next()
        rv = self.app.post('/schema/edit_units', data={'delete_form': one_unit.eid})
        
        self.assertNotIn('Yes', rv.data)
        self.assertIn('Cannot delete unit, its used for', rv.data)
        
        
    def test_units_delete_allowed(self):
        one_unit = model.g.Unit.create(label='testestest %s' % time.time(), 
                                       name='xx', format='yy')
        rv = self.app.post('/schema/edit_units', data={'delete_form': one_unit.eid})
        
        self.assertIn('Yes', rv.data)
        self.assertNotIn('Cannot delete unit, its used for', rv.data)
                   
                   
    def test_units_new(self):
        data = {
            'action': 'new',
            'name': 'testesttest',
            'label': 'testestest %s' % time.time(),
            'format': 'asdfasdfas',
            'note': 'asdfasdf',
        }
        rv = self.app.post('/schema/edit_units', data=data)
        
        self.assertEqual(302, rv.status_code)
        
        one_unit = model.g.Unit.get_one(label=data['label'])
        self.assertEqual(one_unit.P.name, data['name'])
        self.assertEqual(one_unit.P.label, data['label'])
        self.assertEqual(one_unit.P.format, data['format'])
        self.assertEqual(one_unit.P.note, data['note'])
        

    def test_units_new_duplicate(self):
        label = 'testestest %s' % time.time()
        one_unit = model.g.Unit.create(label=label, name='xx', format='yy')
                                       
        data = {
            'action': 'new',
            'name': 'testesttest',
            'label': label,
            'format': 'asdfasdfas',
            'note': 'asdfasdf',
        }
        rv = self.app.post('/schema/edit_units', data=data)
        self.assertIn('Unit with this unit already present', rv.data)
        
      
    def _test_unit(self, label, eid):
        data = {
            'action': 'edit',
            'eid': eid,
            'name': 'AAA',
            'label': label,
            'format': 'BBB',
            'note': 'CCC',
        }
        
        rv = self.app.post('/schema/edit_units', data=data)
        
        self.assertEqual(302, rv.status_code)
        
        one_unit = model.g.get_from_eid(eid)
        self.assertEqual(one_unit.P.name, data['name'])
        self.assertEqual(one_unit.P.label, data['label'])
        self.assertEqual(one_unit.P.format, data['format'])
        self.assertEqual(one_unit.P.note, data['note'])
        
        
    def test_units_edit__different_label(self):
        label = 'testestest %s' % time.time()
        one_unit = model.g.Unit.create(label=label, name='111', format='222', note='333')
        different_label = 'tasdfasdfasdf %s' % time.time()
        self._test_unit(different_label, one_unit.eid)


    def test_units_edit__same_label(self):
        label = 'testestest %s' % time.time()
        one_unit = model.g.Unit.create(label=label, name='111', format='222', note='333')
        self._test_unit(label, one_unit.eid)
        
        
    
    def test_units_edit__duplicate_label(self):
        other_label = 'other testestest %s' % time.time()
        other_unit = model.g.Unit.create(label=other_label, name='111', format='222', note='333')
        
        one_label = 'one testestest %s' % time.time()
        one_unit = model.g.Unit.create(label=one_label, name='111', format='222', note='333')
        
        data = {
            'action': 'edit',
            'eid': one_unit.eid,
            'name': 'AAA',
            'label': other_label,
            'format': 'BBB',
            'note': 'CCC',
        }
        rv = self.app.post('/schema/edit_units', data=data)
        
        self.assertEqual(200, rv.status_code)
        self.assertIn('Unit name already taken', rv.data)
