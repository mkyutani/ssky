import sys
import atproto_client
from ssky.login import Login
from ssky.util import disjoin_uri_cid, is_joined_uri_cid

class Unrepost:

    def name(self) -> str:
        return 'unrepost'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Unrepost a post')
        parser.add_argument('param', type=str, help='URI(at://...)[::CID]')

    def do(self, args) -> bool:
        if is_joined_uri_cid(args.param):
            uri, _ = disjoin_uri_cid(args.param)
        else:
            uri = args.param

        try:
            client = Login().client()
            status = client.delete_repost(uri)
            if status is False:
                return False
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True