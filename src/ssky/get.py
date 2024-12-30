import sys
import atproto_client
from ssky.config import Config
from ssky.post_data_list import PostDataList
from ssky.util import disjoin_uri_cid, expand_actor, is_joined_uri_cid, join_uri_cid

class Get:

    def name(self) -> str:
        return 'get'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Get posts')
        parser.add_argument('param', nargs='?', type=str, metavar='PARAM', help='URI(at://...), DID(did:...), handle, or none as timeline')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-O', '--output', type=str, default=None, metavar='DIR', help='Output to files')
        parser.add_argument('-N', '--limit', type=int, default=100, metavar='NUM', help='Limit lines (<=100)')
        parser.set_defaults(format='')
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument('-I', '--id', action='store_const', dest='format', const='id', help='Print IDs (URI::CID) only')
        format_group.add_argument('-L', '--long', action='store_const', dest='format', const='long', help='Print in long format')
        format_group.add_argument('-T', '--text', action='store_const', dest='format', const='text', help='Print text only')

    def get_posts(self, uri, cid) -> None:
        res = Config().client().get_posts([uri])
        post_data_list = PostDataList()
        for post in res.posts:
            if post.uri == uri and (cid is None or post.cid == cid):
                post_data_list.append(post)
        return post_data_list

    def get_author_feed(self, user, limit=100) -> None:
        res = Config().client().get_author_feed(user, limit=limit)
        post_data_list = PostDataList()
        for feed_post in res.feed:
            post_data_list.append(feed_post.post)
        return post_data_list

    def get_timeline(self, limit=100) -> None:
        res = Config().client().get_timeline(limit=limit)
        post_data_list = PostDataList()
        for feed_post in res.feed:
            post_data_list.append(feed_post.post)
        return post_data_list

    def do(self, args) -> bool:
        try:
            if args.param is None:
                post_data_list = self.get_timeline(limit=args.limit)
            elif args.param.startswith('at://'):
                if is_joined_uri_cid(args.param):
                    uri, cid = disjoin_uri_cid(args.param)
                else:
                    uri = args.param
                    cid = None
                post_data_list = self.get_posts(uri, cid)
            elif args.param.startswith('did:'):
                post_data_list = self.get_author_feed(args.param, limit=args.limit)
            else:
                actor = expand_actor(args.param)
                post_data_list = self.get_author_feed(actor, limit=args.limit)
    
            post_data_list.print(format=args.format, output=args.output, delimiter=args.delimiter)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False
        except atproto_client.exceptions.LoginRequiredError as e:
            print(str(e), file=sys.stderr)
            return False

        return True