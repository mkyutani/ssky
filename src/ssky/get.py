import sys
import atproto_client
from ssky.config import Config
from ssky.post_data_list import PostDataList
from ssky.util import disjoin_uri_cid, expand_actor, is_joined_uri_cid

class Get:

    def name(self) -> str:
        return 'get'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Get posts')
        parser.add_argument('param', nargs='?', type=str, metavar='PARAM', help='URI(at://...), slug(HANDLE:SLUG[:CID]), DID(did:...), handle, or none as timeline')
        parser.add_argument('-l', '--long', action='store_true', help='Long output')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-I', '--id', action='store_true', help='Print IDs (URI::CID) only')
        parser.add_argument('-L', '--limit', type=int, default=100, metavar='NUM', help='Limit lines (<=100)')

    def get_post(self, slug, user, cid) -> None:
        if user is None:
            profile = Config().profile
        else:
            profile = Config().client().get_profile(user)
        res = Config().client().get_post(slug, profile.did, cid)
        self.post_data_list.append(res.value, author=profile, uri=res.uri, cid=res.cid)

    def get_posts(self, uri, cid) -> None:
        res = Config().client().get_posts([uri])
        for post in res.posts:
            if post.uri == uri and (cid is None or post.cid == cid):
                self.post_data_list.append(post)

    def get_author_feed(self, user, limit=100) -> None:
        res = Config().client().get_author_feed(user, limit=limit)
        for feed_post in res.feed:
            self.post_data_list.append(feed_post.post)

    def get_timeline(self, limit=100) -> None:
        res = Config().client().get_timeline(limit=limit)
        for feed_post in res.feed:
            self.post_data_list.append(feed_post.post)

    def do(self, args) -> bool:
        self.post_data_list = PostDataList()

        try:
            if args.param is None:
                self.get_timeline(limit=args.limit)
            elif args.param.startswith('at://'):
                if is_joined_uri_cid(args.param):
                    uri, cid = disjoin_uri_cid(args.param)
                else:
                    uri = args.param
                    cid = None
                self.get_posts(uri, cid)
            elif args.param.startswith('did:'):
                self.get_author_feed(args.param, limit=args.limit)
            elif args.param.count(':') > 0:
                if is_joined_uri_cid(args.param):
                    uri, cid = disjoin_uri_cid(args.param)
                else:
                    uri = args.param
                    cid = None
                param_elements = uri.split(':')
                if len(param_elements) < 1 or len(param_elements) > 2:
                    print(f'Invalid post format (USER:SLUG[::CID])', file=sys.stderr)
                    return False
                user = expand_actor(param_elements[0])
                slug = param_elements[1]
                self.get_post(slug, user, cid)
            else:
                actor = expand_actor(args.param)
                self.get_author_feed(actor, limit=args.limit)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False
        except atproto_client.exceptions.LoginRequiredError as e:
            print(str(e), file=sys.stderr)
            return False

        self.post_data_list.print(id_only=args.id, long_format=args.long, delimiter=args.delimiter)

        return True