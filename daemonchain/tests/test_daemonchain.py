import unittest
import bitcoinrpc.authproxy
import daemonchain


class DaemonTestCase(unittest.TestCase):
    def setUp(self):
        self.daemon1 = daemonchain.Daemon('http://12345:12345@127.0.0.1:2222')


class TestDaemon(DaemonTestCase):
    """
    # Currently very shallow tests.
    """

    def test_construct(self):
        self.assertEqual(self.daemon1._Daemon__url, 'http://12345:12345@127.0.0.1:2222')
        self.assertEqual(self.daemon1._Daemon__whitelisted, set(['getinfo', 'getblockcount', 'getblockhash',
                         'getblock', 'gettransaction']))
        self.assertIsInstance(self.daemon1._Daemon__proxy, bitcoinrpc.authproxy.AuthServiceProxy)

    def test___getattr__(self):
        self.assertIsInstance(self.daemon1.getinfo, bitcoinrpc.authproxy.AuthServiceProxy)
        self.assertIsInstance(self.daemon1.getblockcount, bitcoinrpc.authproxy.AuthServiceProxy)
        self.assertIsInstance(self.daemon1.getblock, bitcoinrpc.authproxy.AuthServiceProxy)
        self.assertIsInstance(self.daemon1.gettransaction, bitcoinrpc.authproxy.AuthServiceProxy)
        self.assertRaises(AttributeError, lambda: self.daemon1.getrawtransaction)


class TestChain(DaemonTestCase):
    """
    """
    def setUp(self):
        DaemonTestCase.setUp(self)
        self.chain1 = daemonchain.Chain(self.daemon1)

    def test_construct(self):
        self.assertIs(self.chain1._Chain__daemon, self.daemon1)

    def test_block_count(self):
        self.assertGreater(self.chain1.block_count, 1)

    def test_get_blk(self):
        blk_hash, blk = self.chain1.get_blk(0)
        self.assertEqual(len(blk_hash), 64)
        self.assertIsInstance(blk, dict)

    def test_get_tx(self):
        blk_hash, blk = self.chain1.get_blk(1)
        tx_hash, tx = self.chain1.get_tx(blk, 0)
        self.assertEqual(len(tx_hash), 64)
        self.assertIsInstance(tx, dict)

    def test_iter_blks(self):
        for n, blk_hash, blk in self.chain1.iter_blks(10, 0):
            self.assertGreater(n, -1)
            self.assertEqual(len(blk_hash), 64)
            self.assertIsInstance(blk, dict)

    def test_iter_tx(self):
        blk_hash, blk = self.chain1.get_blk(1)
        for tx_id, tx in self.chain1.iter_tx(blk):
            self.assertEqual(len(tx_id), 64)
            self.assertIsInstance(tx, dict)

    def test_parse_tx_out(self):
        blk_hash, blk = self.chain1.get_blk(1)
        tx_hash, tx = self.chain1.get_tx(blk, 0)

        for output_n, output_address, output_value in \
                self.chain1.parse_tx_out(tx):
            self.assertGreater(output_n, -1)
            self.assertEqual(len(output_address), 34)
            self.assertGreater(output_value, 0)

    def test_parse_tx_in(self):
        blk_hash, blk = self.chain1.get_blk(1)
        tx_hash, tx = self.chain1.get_tx(blk, 0)

        for input_n, input_address, input_value in \
                self.chain1.parse_tx_in(tx):
            self.assertGreater(input_n, -1)
            self.assertTrue(len(input_address) == 34 or input_address == 'coinbase')
            self.assertGreater(input_value, 0)

    def test_get_tx_out(self):
        blk_hash, blk = self.chain1.get_blk(1)
        tx_hash, tx = self.chain1.get_tx(blk, 0)

        n, address, value = self.chain1.get_tx_out(tx, 0)
        self.assertEqual(n, 0)
        self.assertEqual(len(address), 34)
        self.assertGreater(value, 0)

    def test_find_tx_out_address(self):
        pass