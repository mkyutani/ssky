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
        client = Login().client()

        if is_joined_uri_cid(args.param):
            uri, _ = disjoin_uri_cid(args.param)
        else:
            uri = args.param

        try:
            status = client.delete_repost(uri)
            if status is False:
                return False
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return None

        return True