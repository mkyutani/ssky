import sys
import atproto_client
from ssky.config import Config
from ssky.util import disjoin_uri_cid, is_joined_uri_cid

class Delete:

    def name(self) -> str:
        return 'delete'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Delete post')
        parser.add_argument('param', type=str, help='URI(at://...)[::CID]')

    def do(self, args) -> bool:
        if is_joined_uri_cid(args.param):
            uri, _ = disjoin_uri_cid(args.param)
        else:
            uri = args.param

        try:
            status = Config().client().delete_post(uri)
            if status is False:
                print('Failed to delete', file=sys.stderr)
                return False
            print('Deleted successfully', file=sys.stderr)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True