pydaemonchain
=============

Python bitcoind blockchain parser. (i.e. Slow)

This uses the bitcoin daemon json RPC to walk through the blockchain and follow transactions.

This is experimental and not for production use. It might be used for simple calculations, rich list, block explorer verification, etc.

It will work with any bitcoind (or altcoin daemon) that supports the following RPC commands:

    * getinfo (optional)
    * getblockcount
    * getblockhash
    * getblock
    * gettransaction


Installation
============

pip install bitcoinrpc




Usage
=====
import daemonchain