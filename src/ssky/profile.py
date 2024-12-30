import sys
import atproto_client
from ssky.profile_list import ProfileList
from ssky.config import Config
from ssky.util import expand_actor

class Profile:

    def name(self) -> str:
        return 'profile'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Show profile')
        parser.add_argument('name', type=str, help='Handle or DID to show')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.set_defaults(format='')
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument('-I', '--id', action='store_const', dest='format', const='id', help='Print IDs (URI::CID) only')
        format_group.add_argument('-J', '--json', action='store_const', dest='format', const='json', help='Print in JSON format')
        format_group.add_argument('-L', '--long', action='store_const', dest='format', const='long', help='Print in long format')

    def do(self, args) -> bool:
        try:
            ProfileList().append(expand_actor(args.name)).print(format=args.format, delimiter=args.delimiter)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True