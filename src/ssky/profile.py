import sys
from atproto import Client
import atproto_client
from ssky.env import Environment
from ssky.util import summarize

class Profile:

    def name(self) -> str:
        return 'profile'

    def do(self, args) -> bool:
        return self.profile(args)

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser('profile', help='Show profile')
        parser.add_argument('name', nargs=1, type=str, help='Handle or DID to show')

    def profile(self, args):
        env = Environment()

        try:
            client = Client()
            client.login(env.username(), env.password())

            profile = client.get_profile(args.name[0])
            did = profile.did
            handle = profile.handle
            display_name = profile.display_name
            avatar = profile.avatar
            banner = profile.banner

            print(f'{did} {handle} {summarize(display_name)} {avatar} {banner}')
        except atproto_client.exceptions.UnauthorizedError as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return False
        except atproto_client.exceptions.BadRequestError as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return False
        except Exception as e:
            error_message = str(e)
            print(f'{error_message}', file=sys.stderr)
            return False

        return True