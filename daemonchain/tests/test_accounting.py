import unittest
import daemonchain.accounting

class TestAccounting(unittest.TestCase):
    """
    # Currently very shallow tests.
    """
    def test_update_book(self):
        book = {}
        daemonchain.accounting.update_book(book, '12345', 100)
        daemonchain.accounting.update_book(book, '12345', 100)
        daemonchain.accounting.update_book(book, '54321', 100)
        daemonchain.accounting.update_book(book, '54321', -50)

        def raises():
            daemonchain.accounting.update_book(book, '54321', -150)

        self.assertEqual(book, {'54321': 50, '12345': 200})
        self.assertRaises(AssertionError, raises)
        self.assertEqual(book, {'54321': 50, '12345': 200})

    def test_cull_book(self):
        book = {'12345': 123,
                '54321': 321,
                '11111': 0}
        daemonchain.accounting.cull_book(book)
        self.assertEqual(book, {'12345': 123, '54321': 321})