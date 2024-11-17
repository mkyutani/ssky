import argparse
import io
import sys

from ssky.post import ssky_post, ssky_post_parser
from ssky.timeline import ssky_timeline, ssky_timeline_parser

function_map = {
    'post': { 'aliases': [ 'p' ], 'function': ssky_post, 'parser': ssky_post_parser },
    'timeline': { 'aliases': [ 'tl' ], 'function': ssky_timeline, 'parser': ssky_timeline_parser }
}

def set_io_buffers():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=False)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=False)

def main():
    set_io_buffers()

    parser = argparse.ArgumentParser(description='Simple Bluesky Client')
    sp = parser.add_subparsers(dest='function', title='Function', required=True)

    for function in function_map.values():
        function['parser'](sp)

    args = parser.parse_args()

    function = args.function
    for function_name in function_map.keys():
        if function == function_name:
            return function_map[function_name]['function'](args)

    return 0

if __name__ == '__main__':
    exit(main())