import argparse
import io
import sys

from ssky.post import Post
from ssky.get import Get
from ssky.profile import Profile

function_map = [
    Post(),
    Profile(),
    Get()
]

def set_io_buffers():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=False)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=False)

def main():
    set_io_buffers()

    parser = argparse.ArgumentParser(description='Simple Bluesky Client')
    sp = parser.add_subparsers(dest='function', title='Function', required=True)

    for function in function_map:
        function.parse(sp)

    args = parser.parse_args()

    function_name = args.function
    for function in function_map:
        if function_name == function.name():
            return 0 if function.do(args) is True else 1

    return 0

if __name__ == '__main__':
    exit(main())