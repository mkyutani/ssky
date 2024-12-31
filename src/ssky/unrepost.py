import sys
import atproto_client
from ssky.config import Config
from ssky.util import disjoin_uri_cid, is_joined_uri_cid

class Unrepost:

    def name(self) -> str:
        return 'unrepost'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Unrepost a post')
        parser.add_argument('param', type=str, help='URI(at://...)[::CID]')

    def do(self, args) -> bool:
        if is_joined_uri_cid(args.param):
            source_uri, source_cid = disjoin_uri_cid(args.param)
        else:
            source_uri = args.param
            source_cid = None

        try:
            client = Config().client()
            sources = client.get_posts([source_uri])
            repost_uri = None
            for source_post in sources.posts:
                if source_post.uri == source_uri and (source_cid is None or source_post.cid == source_cid):
                    repost_uri = source_post.viewer.repost
                    break

            if repost_uri is None:
                print(f'Post not found', file=sys.stderr)
                return False

            status = client.unrepost(repost_uri)
            if status is False:
                print('Failed to unrepost', file=sys.stderr)
                return False
            print('Unreposted successfully', file=sys.stderr)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True