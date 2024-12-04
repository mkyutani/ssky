import sys
import atproto_client
from ssky.login import Login
from ssky.util import disjoin_uri_cid, expand_actor, is_joined_uri_cid, join_uri_cid, summarize

class Repost:

    def name(self) -> str:
        return 'repost'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Repost')
        parser.add_argument('param', nargs='?', type=str, metavar='PARAM', help='URI(at://...)[::CID]')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-I', '--id', action='store_true', help='Print IDs (URI::CID) only')
        parser.add_argument('-L', '--limit', type=int, default=100, metavar='NUM', help='Limit lines (<=100)')

    def get_post(self, uris) -> list:
        try:
            res = self.client.get_posts(uris)
            post_data = []
            for post in res.posts:
                post_data.append(self.PostData(post.uri, post.cid, post.author.did, post.author.handle, post.author.display_name, post.record.text))
            return post_data
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return None

    def do(self, args) -> bool:
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
            if args.id:
                print(join_uri_cid(repost.uri, repost.cid))
            else:
                try:
                    sources = client.get_posts([source_uri])
                    for source_post in sources.posts:
                        if source_post.uri == source_uri and (source_cid is None or source_post.cid == source_cid):
                            display_name_summary = summarize(source_post.author.display_name)
                            text_summary = summarize(source_post.record.text, 40)
                            print(args.delimiter.join([join_uri_cid(repost.uri, repost.cid), source_post.author.did, source_post.author.handle, display_name_summary, text_summary]))
                except atproto_client.exceptions.RequestErrorBase as e:
                    print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
                    return None

        return True