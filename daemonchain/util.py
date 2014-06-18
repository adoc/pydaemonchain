import os
import time
import pickle

class State(object):
    """Simple persistence
    """
    def __init__(self, persist_file, persist_every=1000):
        self.persist_file = persist_file
        self.__persist_every = persist_every
        self.__count_since_persist = 0
        self.__state = {'data': {}, 'meta': {}}

    @property
    def data(self):
        return self.__state['data']

    @property
    def meta(self):
        return self.__state['meta']

    def update(self, data, meta={}):
        assert isinstance(data, dict), "Data must be dict."
        assert isinstance(meta, dict), "Meta data must be dict."
        self.__count_since_persist += 1
        self.__state['meta'].update(meta)
        self.__state['meta'].update({'ts_updated': time.time()})
        self.__state['data'].update(data)

        if not self.__count_since_persist % self.__persist_every:
            self.persist()
            return True

    def persist(self):
        """Simple persist of state.
        """
        self.__state['meta'].update({'ts_saved': time.time()})
        pickle.dump(self.__state,
                        open(self.persist_file, 'w'))
        self.__count_since_persist = 0

    def load(self):
        """Load persisted data.
        """
        self.__state = pickle.load(open(self.persist_file, 'r'))
        self.__state['meta'].update({'ts_loaded': time.time()})
        self.__count_since_persist = 0

    def reset(self):
        """
        """
        self.__state = {}
        if os.path.exists(self.__persist_file):
            os.unlink(self.__persist_file)
        self.__count_since_persist = 0

class Lock(object):
    pass