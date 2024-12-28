import sys
import atproto_client
from ssky.config import Config

class Login:

    def name(self) -> str:
        return 'login'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Login')
        parser.add_argument('handle', type=str, help='User handle')
        parser.add_argument('password', type=str, help='User password')

    def do(self, args) -> bool:
        try:
            config = Config(args.handle, args.password)
            if config is None:
                return False
            config.persist()
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True