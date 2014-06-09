import unittest

class TestParser(unittest.TestCase):
    def setUp(self):
        # Expecting the Cinnicoin blockchain.
        self.max = 50100
        self.min = 50000
        self.svc = AuthServiceProxy("http://12345:12345@127.0.0.1:2222")

    def test_iter_blks(self):
        for blk_n, blk_hash, blk in iter_blks(self.max, min=self.min,
                                              svc=self.svc):
            self.assertIsInstance(blk_n, int)
            self.assertIsInstance(blk_hash, basestring)
            self.assertIsInstance(blk, dict)
            self.assertEqual(len(blk_hash), 64)
            self.assertGreater(blk['confirmations'], 1)

    def test_iter_tx(self):
        for _, _, blk in iter_blks(self.max, min=self.min,
                                              svc=self.svc):
            for tx_hash, tx in iter_tx(blk):
                self.assertIsInstance(tx_hash, basestring)
                self.assertIsInstance(tx, dict)
                self.assertEqual(len(tx_hash), 64)
                self.assertIn('vin', tx)
                self.assertIn('vout', tx)

    def test_zip_tx(self):
        for _, _, blk in iter_blks(self.max, min=self.min, svc=self.svc):
            for _, tx in iter_tx(blk):
                ins, outs = zip_tx(tx)
                for n, address, amount in ins:
                    self.assertIsInstance(n, int)
                    self.assertIsInstance(address, basestring)
                    self.assertIsInstance(amount, float)
                    self.assertEqual(len(address), 34)
                    self.assertGreaterEqual(amount, 0.0)
                for n, address, amount in outs:
                    self.assertIsInstance(n, int)
                    self.assertIsInstance(address, basestring)
                    self.assertIsInstance(amount, float)
                    self.assertEqual(len(address), 34) # this is the issue.
                    self.assertGreaterEqual(amount, 0.0)