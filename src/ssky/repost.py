import sys
import atproto_client
from ssky.login import Login
from ssky.post_data import PostData
from ssky.util import disjoin_uri_cid, is_joined_uri_cid

class Repost:

    def name(self) -> str:
        return 'repost'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Repost')
        parser.add_argument('param', type=str, help='URI(at://...)[::CID]')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-I', '--id', action='store_true', help='Print IDs (URI::CID) only')

    def do(self, args) -> bool:
        PostData.set_delimiter(args.delimiter)

        client = Login().client()

        if is_joined_uri_cid(args.param):
            source_uri, source_cid = disjoin_uri_cid(args.param)
        else:
            source_uri = args.param
            source_cid = None

        try:
            repost = client.repost(source_uri, source_cid)
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return None

        if repost is None:
            return False
        else:
            try:
                sources = client.get_posts([source_uri])
                for source_post in sources.posts:
                    if source_post.uri == source_uri and (source_cid is None or source_post.cid == source_cid):
                        post_data = PostData().set(source_post)
                        post_data.set_items({'uri': repost.uri, 'cid': repost.cid})
                        if args.id:
                            print(post_data.get_uri_cid())
                        else:
                            print(post_data)
            except atproto_client.exceptions.RequestErrorBase as e:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
                return None

        return True