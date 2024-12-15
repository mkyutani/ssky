import sys
import atproto_client
from ssky.login import Login
from ssky.post_data import PostData
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

    def get_post(self, slug, user, cid) -> list:
        if user is None:
            profile = self.profile
        else:
            profile = self.client.get_profile(user)
        res = self.client.get_post(slug, profile.did, cid)
        post_data = [PostData(res.uri, res.cid, profile.did, profile.handle, profile.display_name, res.value.text)]
        return post_data

    def get_posts(self, uris) -> list:
        res = self.client.get_posts(uris)
        post_data = []
        for post in res.posts:
            post_data.append(PostData().set(post))
        return post_data

    def get_author_feed(self, user, limit=100) -> list:
        res = self.client.get_author_feed(user, limit=limit)
        post_data = []
        for feed in res.feed:
            post_data.append(PostData().set(feed.post))
        return post_data

    def get_timeline(self, limit=100) -> list:
        res = self.client.get_timeline(limit=limit)
        post_data = []
        for feed in res.feed:
            post_data.append(PostData().set(feed.post))
        return post_data

    def do(self, args) -> bool:
        PostData.set_default_delimiter(args.delimiter)

        try:
            login = Login()
            self.client = login.client()
            self.profile = login.profile()
            self.handle = login.handle()

            if args.param is None:
                post_data = self.get_timeline(limit=args.limit)
            elif args.param.startswith('at://'):
                if is_joined_uri_cid(args.param):
                    uri, cid = disjoin_uri_cid(args.param)
                else:
                    uri = args.param
                    cid = None
                returned_posts = self.get_posts([uri])
                post_data = []
                for returned_post in returned_posts:
                    if returned_post.uri == uri and (cid is None or returned_post.cid == cid):
                        post_data.append(returned_post)
            elif args.param.startswith('did:'):
                post_data = self.get_author_feed(args.param, limit=args.limit)
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
                post_data = self.get_post(slug, user, cid)
            else:
                actor = expand_actor(args.param)
                post_data = self.get_author_feed(actor, limit=args.limit)

            if post_data is None:
                return False
            else:
                continued = False
                for post in post_data:
                    if args.id:
                        print(post.get_uri_cid())
                    elif args.long:
                        if continued:
                            print('--------')
                        print(post.long())
                        continued = True
                    else:
                        print(post)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True