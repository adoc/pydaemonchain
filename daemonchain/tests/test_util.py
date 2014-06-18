import os
import pickle
import unittest
import daemonchain.util

class TestState(unittest.TestCase):
    """
    # Currently very shallow tests.
    """

    def setUp(self):
        self.state1 = daemonchain.util.State('test_state1.file')

    def tearDown(self):
        if os.path.exists('test_state1.file'):
            os.unlink('test_state1.file')

    def test_construct(self):
        self.assertEqual(self.state1.persist_file, 'test_state1.file')
        self.assertEqual(self.state1._State__persist_every, 1000)
        self.assertEqual(self.state1._State__count_since_persist, 0)
        self.assertEqual(self.state1._State__state, {'data': {}, 'meta': {}})

    def test_update(self):
        data = {'some': 'data', 'for': 'u', 'foo': 1}
        meta = {'meta': 'data'}

        self.state1.update(data, meta=meta)
        self.assertEqual(self.state1.data, data)
        self.assertEqual(self.state1.meta['meta'], meta['meta'])
        self.assertIs(self.state1._State__count_since_persist, 1)

    def test_persist(self):
        data = {'some': 'data', 'for': 'u', 'foo': 1}
        meta = {'meta': 'data'}

        self.state1.update(data, meta=meta) # Using update here might be incorrect test methodology.
        self.state1.persist()

        self.assertIs(self.state1._State__count_since_persist, 0)

        loaded_data = pickle.load(open('test_state1.file','r'))
        self.assertEqual(loaded_data, self.state1._State__state)

    def test_load(self):
        raw_data = {'meta': {'ts_updated': 1403056560.422311, 'meta': 'data', 'ts_saved': 1403056560.422318}, 'data': {'foo': 1, 'some': 'data', 'for': 'u'}}
        pickle.dump(raw_data, open('test_state1.file', 'w'))

        self.state1.load()
        del self.state1._State__state['meta']['ts_loaded']

        self.assertEqual(raw_data, self.state1._State__state)