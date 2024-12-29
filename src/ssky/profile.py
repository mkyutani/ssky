import sys
import atproto_client
from ssky.actor_list import ActorList
from ssky.config import Config
from ssky.util import expand_actor

class Profile:

    def name(self) -> str:
        return 'profile'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Show profile')
        parser.add_argument('name', type=str, help='Handle or DID to show')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-I', '--id', action='store_true', help='Print ID (DID) only')
        parser.add_argument('-L', '--long', action='store_true', help='Long output')

    def do(self, args) -> bool:
        try:
            actor = expand_actor(args.name)
            profile = Config().client().get_profile(actor)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        ActorList().append(profile).print(id_only=args.id, long_format=args.long, delimiter=args.delimiter)

        return True