import sys
from atproto import IdResolver, models
import atproto_client
from ssky.config import Config
from ssky.util import expand_actor

class Follow:

    def name(self) -> str:
        return 'follow'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Follow')
        parser.add_argument('name', type=str, help='Handle or DID to follow')

    def do(self, args) -> bool:
        try:
            actor = expand_actor(args.name)
            profile = Config().client().get_profile(actor)
            Config().client().follow(profile.did)
            print('Followed successfully', file=sys.stderr)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True