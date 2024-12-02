import sys
import atproto_client
from ssky.login import Login
from ssky.util import expand_actor, summarize

class Profile:

    def name(self) -> str:
        return 'profile'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Show profile')
        parser.add_argument('name', type=str, help='Handle or DID to show')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-I', '--id', action='store_true', help='Print ID (DID) only')

    def do(self, args) -> bool:
        try:
            login = Login()
            client = login.client()

            actor = expand_actor(args.name)
            profile = client.get_profile(actor)
            display_name_summary = summarize(profile.display_name)

            if args.id:
                print(profile.did)
            else:
                print(args.delimiter.join([profile.did, profile.handle, display_name_summary]))
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return False

        return True