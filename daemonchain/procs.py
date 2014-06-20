"""Processes.
"""

import time
import copy
import threading
import operator
import daemonchain
import daemonchain.accounting

class Killable(threading.Thread):
    """
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self._killed = False
    
    def kill(self):
        self._killed = True


class CompileBook(Killable):
    """
    """
    name = "book"
    interval = 60

    def __init__(self, daemon, state):
        Killable.__init__(self)
        self.__chain = daemonchain.Chain(daemon)
        self.__state = state

    def run(self):
        min = (self.__state.meta.get('last_blk',-1)+1)
        print("Compiling balance book starting at block %s" % (min))
        big_book = copy.deepcopy(self.__state.get_keyed('book'))
        for book, blk_n in self.__chain.compile_book(big_book, min=min):
            if 'coinbase' in book:
                del book['coinbase']
            self.__state.update('book', book, meta={'last_blk': blk_n})
            if self._killed is True:
                self.__state.persist()
                break


class RichList(Killable):
    """
    """
    name = "richlist"
    interval = 60
    def __init__(self, book, state):
        Killable.__init__(self)
        self.__book = book
        self.__state = state

    def run(self):
        #book = copy.deepcopy(self.__state.get_keyed('book'))
        book = daemonchain.accounting.cull_book(self.__book, min=1000)
        sorted_book = sorted(book.items(), key=operator.itemgetter(1))
        descending_book = list(reversed(sorted_book))
        self.__state.update('rich', {'list': descending_book})


class PushThread(Killable):
    """
    """
    name = "push"
    def __init__(self, extension, rich):
        Killable.__init__(self)
        self.__extension = extension
        self.__rich = rich

    def run(self):
        print("Pushing data...")
        self.__extension.push(self.__rich)
        i = 10 / 0.1
        while i > 0 and not self._killed:
            time.sleep(0.1)
            i-=1


