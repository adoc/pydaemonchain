"""Processes.
"""
import threading
import daemonchain

class CompileRich(threading.Thread):
    def __init__(self, daemon, state):
        self.__chain = daemonchain.Chain(daemon)
        self.__state = state

    def run(self):
        pass

