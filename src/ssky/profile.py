import sys
import atproto_client
from ssky.login import Login
from ssky.util import summarize

class Profile:

    def name(self) -> str:
        return 'profile'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Show profile')
        parser.add_argument('name', nargs=1, type=str, help='Handle or DID to show')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', help='Delimiter')

    def do(self, args) -> bool:
        try:
            login = Login()
            client = login.client()

            profile = client.get_profile(args.name[0])
            did = profile.did
            handle = profile.handle
            display_name_summary = summarize(profile.display_name)

            print(args.delimiter.join([did, handle, display_name_summary]))
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return False

        return True