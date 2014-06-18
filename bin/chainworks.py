"""Main script file.
"""
import sys
import argparse

import daemonchain.util

def parse_args():
    parse = argparse.ArgumentParser(description='Daemonchain execution.')
    parse.add_argument('url', type=str, nargs="?")
    parse.add_argument('-R', '--rich', action="store_true",
                       help="Compile Rich List.")
    parse.add_argument('-n', '--min', action="store", default=0,
                       help="Min block number to process.")
    parse.add_argument('-m', '--max', action="store", default=-1,
                       help="Max block number to process.")
    parse.add_argument('-c', '--continuous', action="store_true",
                       help="Continuously parse new blocks as they come in "
                            "to the daemon.")
    parse.add_argument('-p', '--persist', action="store_true", 
                       help="Persist calculations to file.")
    parse.add_argument('-r', '--reset', action="store_true",
                       help="Remove presisted state and start fresh.")
    parse.add_argument('-x', '--ext', action="store",
                       help="Use an extension.")
    parse.add_argument('--list-extensions', action="store_true",
                       help="List available extensions.")
    return parse.parse_args()


def handle_config(config):
    if config.list_extensions is True:
        print("Available extensions:")

        for ext in daemonchain.util.get_extensions():
            print(ext.Extension.__doc__)

def main():
    config = parse_args()
    handle_config(config)



if __name__ == "__main__":
    main()