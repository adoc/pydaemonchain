import os
import time
import copy
import pickle
import daemonchain.ext


def get_extensions():
    ext = __import__('daemonchain.ext', globals(), locals(), daemonchain.ext.__all__, -1)
    return [(module, getattr(ext, module)) for module in dir(ext) if not module.startswith('_')]


def get_extension(name):
    ext = __import__('daemonchain.ext', globals(), locals(), [name, ], -1)
    return getattr(ext, name)


class State(object):
    """Simple persistence
    """
    def __init__(self, persist_file, persist_every=1000, persist_omit=[],
                 auto_load=False):
        self.persist_file = persist_file
        self.__persist_every = persist_every
        self.__persist_omit = persist_omit
        self.__count_since_persist = 0
        self._state = {'data': {}, 'meta': {}}

        if auto_load is True:
            self.load()

    @property
    def data(self):
        return self._state['data']

    @property
    def meta(self):
        return self._state['meta']

    def update(self, data, meta={}):
        """
        """
        assert isinstance(data, dict), "Data must be dict."
        assert isinstance(meta, dict), "Meta data must be dict."
        self.__count_since_persist += 1
        self._state['meta'].update(meta)
        self._state['meta'].update({'ts_updated': time.time()})
        self._state['data'].update(data)

        if not self.__count_since_persist % self.__persist_every:
            self.persist()
            return True

    def persist(self):
        """Simple persist of state.
        """
        print("Persisting state... (Block %s)" % (self.meta.get('last_blk')))
        self._state['meta'].update({'ts_saved': time.time()})
        
        #state = copy.deepcopy(self._state)
        #for omit in self.__persist_omit:
        #    if omit in state['data']:
        #        del state['data'][omit]

        pickle.dump(self._state,
                        open(self.persist_file, 'w'))
        self.__count_since_persist = 0

    def load(self):
        """Load persisted data.
        """
        self._state = pickle.load(open(self.persist_file, 'r'))
        self._state['meta'].update({'ts_loaded': time.time()})
        self.__count_since_persist = 0

    def reset(self):
        """
        """
        self._state = {}
        if os.path.exists(self.__persist_file):
            os.unlink(self.__persist_file)
        self.__count_since_persist = 0


class KeyedState(State):
    """Just a simple extension to allow for multiple data keys.
    """
    def get_keyed(self, key):
        if not key in self._state['data']:
            self._state['data'][key] = {}
        return self._state['data'][key]

    def update(self, key, data, meta={}):
        target = self.get_keyed(key)
        target.update(data)
        State.update(self, {key: target}, meta=meta)


class Lock(object):
    pass