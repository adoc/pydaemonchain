from bitcoinrpc.authproxy import AuthServiceProxy


class Daemon(object):
    """Just a simple wrapper for bitcoinrpc.authproxy.AuthServicesProxy.
    Calls `whitelist`ed daemon commands to provide some protection
    Reconnects on JSON RPC error.
    """

    # Some protection once this lib is on a live hosted service.
    __whitelisted = set('getinfo', 'getblockcount', 'getblockhash',
                     'getblock', 'gettransaction')

    def __init__(self, url, whitelist=set(), auto_connect=True):
        self.__url = url
        self.__whitelisted += whitelist # Additional whitelist entries.
        if auto_connect is True:
            self.connect()

    def connect(self):
        self.__proxy = AuthServiceProxy(url)

    def __getattr__(self, attr):
        if attr in self.__whitelisted:
            try:
                return getattr(self.__proxy, attr)
            except:
                raise # Handle once we know the exact error
                self.__connect()
                return getattr(self.__proxy, attr)
        else:
            raise AttributeError("`Daemon` object has no method `%s`. Not "
                "forwarding command to RPC proxy. It's not in the whitelist.")


class Chain(object):
    """Main object to parse and walk the blockchain using `daemon`.
    """
    def __init__(self, daemon):
        assert isinstance(daemon, connect.Daemon), "`daemon` argument must be"\
            "a daemon object."
        self.__daemon = daemon

    # Properties
    @property
    def block_count():
        return self.__daemon.getblockcount()

    # Base parsers
    def parse_tx_out(self, tx):
        """Parse transaction outputs.
        Yields (output_n, output_address, output_amount)
        """
        for out in tx['vout']:
            if 'addresses' in out['scriptPubKey']:
                addresses = out['scriptPubKey']['addresses']
                if len(addresses) > 1:
                    # This never happens?? We don't know what to do here.
                    raise NotImplementedError("More than one vout address.")
                yield out['n'], addresses[0], out['value']
                #yield out['n'], addresses[0], float(out['value']) #Not sure which is right.
            else:
                # No addresses. Do nothing for now.
                pass

    def parse_tx_in(self, tx):
        """Parse the outputs fundings this transaction. None if mined.
        """
        for in_ in tx['vin']:       # Iterate through tx inputs.
            if 'scriptSig' in in_:  # Only concerned with signed inputs.
                input_tx = self.__daemon(in_['txid'])  # Get previous
                                                       #   transaction
                # generate (output number, output address, output amount)
                yield self.get_tx_out(input_tx, in_['vout'])
            elif 'coinbase' in  in_:
                assert len(tx['vout'])==1, "Problem with parser. "\
                    "Expected only 1 output on a 'coinbase' transaction."
                # generate (output number, output address, output amount)
                yield, 0, 'coinbase', tx['vout'][0]['value']
            else:
                raise Exception("Bad transaction sent to `Chain.parse_tx_in`"
                                ". %s" % tx)

    # Filters
    def get_tx_out(self, tx, get_n):
        """Return nth output in a tx. Used in discovering input specifics.
        """
        for n, address, amount in self.parse_tx_out(tx):
            if get_n == n:
                # return (output number, output address, output amount)
                return n, address, amount

    def find_tx_out_address(self, tx, target):
        """Searches for address `target` in the outputs of a transaction.
        """
        for n, address, amount in self.parse_tx_out(tx):
            if address == target:
                # generate (output number, output address, output amount)
                yield n, address, amount

    def find_tx_in_address(self, tx, target):
        """Searches for address `target` in the inputs of a transaction.
        """
        for n, address, amount in self.parse_tx_in(tx):
            if address == target:
                # generate (input number, input address, input amount)
                yield n, address, amount

    # Iterators
    def iter_tx(self, blk_data):
        """Iterate through block transactions.
        """
        for tx in blk_data['tx']:
            # generate (transaction hash, transaction dict)
            yield tx['txid'], tx

    def iter_blks(self, max, min=0):
        """Main Iterator. Iterate through blocks yielding the block
        data and number. Overloaded in ProcessSafeChain to provide
        multiprocess support.
        """
        for blk_n in range(min, max):
            # Get the block hash of block n.
            blk_hash = self.__daemon.getblockhash(blk_n)
            # generate (block number, block hash, block dict)
            yield blk_n, blk_hash, self.__daemon.getblock(blk_hash, True)

    # Queries
    def find_address_transactions(self, address, max=None, min=0):
        """Iterate through blocks searching for transactions in from and out to
        `address`.
        """
        bal = 0
        max = max or self.block_count
        for blk_n, _, blk in self.iter_blks(max, min=min):
            for _, tx in self.iter_tx(blk):
                for _, address, amount in self.find_tx_out_address(tx, address):
                    bal += amount
                    # generate (direction, output address, output amount,
                    #           address balance)
                    yield address, amount, bal
                for _, address, amount in self.find_tx_in_address(tx, address):
                    bal -= amount
                    # generate (direction, input address, input amount,
                    #           address balance)
                    yield address, -amount, bal

    def all_transactions(max=None, min=0):
        """Iterate through blocks yielding all parsed transactions.
        yields (in or out, address, amount)
        """
        max = max or self.block_count
        for blk_n, _, blk in self.iter_blks(max, min=min):
            for _, tx in iter_tx(blk):
                for _, address, amount in self.parse_tx_out(tx):
                    yield address, amount, blk_n
                for _, address, amount in self.parse_tx_in(tx):
                    # generate (direction, input address, input amount,
                    #           address balance)
                    yield address, -amount, blk_n

    def compile_book(self, book={}, max=None, min=0):
        """Compile the list of addresses and balances.
        `book` is just dict or a key-value store with dict methods.
        """
        max = max or self.block_count
        for address, amount, blk_n in self.all_transactions(max=max,
                                                            min=min):
            accounting.update_book(book, address, amount)
            yield book, blk_n


class ProcessSafeChain(Chain):
    """A multi-processes safe version of `Chain`. This accomplished by
    acquiring a lock before processing a block
    # Not implemented.
    """
    def __init__(self, lock_mechanism):
        pass

    def iter_blks(self, max, min=0):
        """Iterate through blocks, yielding the block data and number
        if a lock could be acquired.
        """
        raise NotImplementedError()