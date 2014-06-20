"""Main script file.
"""
import sys
import time
import copy
import signal
import threading
import argparse

import daemonchain.procs
import daemonchain.util

LOOP_THROTTLE = 0.1

def parse_args():
    parse = argparse.ArgumentParser(description='Chainworks execution.',
                                    add_help=False)

    threads = parse.add_argument_group(title="Threads", description="")
    #subparsers = parse.add_subparsers(title="Threads", description="")
    #subparsers.add_parser('threads', help="Avail")

    threads.add_argument('-B', '--book', action="store_true",
                       help="Compile the balance book (Dict of addresses and balances).")

    threads.add_argument('-R', '--rich-list', action="store_true",
                       help="Sort the book (This invokes a -B thread as well.)")

    parse.add_argument('--min', action="store", default=0,
                       help="Min block number to process.")
    parse.add_argument('--max', action="store", default=-1,
                       help="Max block number to process.")
    parse.add_argument('-c', '--continuous', action="store_true",
                       help="Continuously parse new blocks as they come in "
                            "to the daemon.")
    parse.add_argument('-p', '--file', action="store", default="/tmp/chainworks.dat",
                       help="Persist file path. default: /tmp/chainworks.dat")
    parse.add_argument('-r', '--reset', action="store_true",
                       help="Remove presisted state and start fresh.")
    parse.add_argument('--list-extensions', action="store_true",
                       help="List available extensions.")

    available_extensions = []
    for name, ext in daemonchain.util.get_extensions():
        parse.add_argument('--%s' % name, action="store_true",
                           help=ext.Extension.__doc__)
        available_extensions.append((name, ext))

    partial, positional = parse.parse_known_args()

    enabled_extensions = []
    for name, ext in available_extensions:
        if getattr(partial, name) is True:
            ext.Extension.args(parse)
            enabled_extensions.append(ext)

    # Add help and required args.
    parse = argparse.ArgumentParser(parents=[parse])
    parse.add_argument('-u', '--url', type=str, required=True,
                       help="The RPC daemon URL including authentication "
                            "and port. ex: http://rpcuser:rpcpass@127.0.0.1:22222")

    config = parse.parse_args()

    config.extensions = enabled_extensions

    return config


def list_extensions(config):
    print("Available extensions:")
    for name, ext in daemonchain.util.get_extensions():
        print name.ljust(20) + ext.Extension.__doc__.rjust(60)


def handle_config(config):
    if config.list_extensions is True:
        list_extensions()
        sys.exit(0)
    return config


class ContinuousThread(threading.Thread):
    """Thread to spawn a chlid thread and join it continuiously.
    """
    # Figure out any sigint issues, though there shouldn't be with the joins.
    def __init__(self, thread_closure):
        threading.Thread.__init__(self)
        self.__thread_closure = thread_closure
        self.__killed = False
        self.name = thread_closure().name

    def run(self):
        while not self.__killed:
            self.__child = self.__thread_closure() # Eval lambda
            #print("Starting %s..." % self.__child.name)
            self.__child.start()
            self.__child.join()
            time.sleep(LOOP_THROTTLE)

    def kill(self):
        self.__killed = True
        if self.__child:
            self.__child.kill()


def main():
    config = handle_config(parse_args())
    daemon = daemonchain.Daemon(config.url)
    state = daemonchain.util.KeyedState(config.file,
                persist_omit=['rich'], auto_load=False)
    try:
        state.load()
    except IOError:
        print("No state to load.")

    threads = []
    if any([config.rich_list, config.book]):
        threads.append(lambda: daemonchain.procs.CompileBook(daemon, state))

    if config.rich_list:
        threads.append(lambda: daemonchain.procs.RichList(copy.copy(state.get_keyed('book')), state))

    if config.extensions:
        for ext in config.extensions:
            ext = ext.Extension(config)
            threads.append(lambda: daemonchain.procs.PushThread(ext, copy.copy(state.get_keyed('rich').get('list', []))))

    # Check for threads.
    if not threads:
        print("Nothing to do. (Maybe try a -B or -R.)")
        sys.exit(1)

    if config.continuous is True:
        threads = [ContinuousThread(thread) for thread in threads]
    else:
        threads = [thread() for thread in threads]

    # Fire all threads
    for thread in threads:
        print("Starting thread '%s'" % thread.name)
        thread.start()

    def sig_hand(sig, frame):
        print("Killing threads...")
        for thread in threads:
            thread.kill()

        deadlock_timeout = 10.0
        i = 0
        t = deadlock_timeout/LOOP_THROTTLE
        while i < t and any([thread.is_alive() for thread in threads]):
            time.sleep(LOOP_THROTTLE)
            i += 1

        if i == t:
            print("Deadlocked timeout reached. Could not exit cleanly.")
        else:
            print("Exited cleanly")
            sys.exit(0)

    signal.signal(signal.SIGINT, sig_hand)


    while True:
        #os.system('clear')
        time.sleep(LOOP_THROTTLE)
        #print(threads)
        for n, thread in enumerate(threads):
            if not thread.is_alive():
                print("Thread '%s' done." % thread.name)
                threads.pop(n)
                break


if __name__ == "__main__":
    main()