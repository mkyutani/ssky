import sys
import atproto_client
from ssky.login import Login
from ssky.util import disjoin_uri_cid, expand_actor, is_joined_uri_cid, join_uri_cid, summarize

class Get:

    def name(self) -> str:
        return 'get'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Get posts')
        parser.add_argument('param', nargs='?', type=str, metavar='PARAM', help='URI(at://...), slug(HANDLE:SLUG[:CID]), DID(did:...), handle, or timeline')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-I', '--id', action='store_true', help='Print IDs (URI::CID) only')
        parser.add_argument('-L', '--limit', type=int, default=100, metavar='NUM', help='Limit lines (<=100)')

    class PostData:
        def __init__(self, uri: str, cid: str, author_did: str, author_handle: str, author_display_name: str, text: str):
            self.uri = uri
            self.cid = cid
            self.author_did = author_did
            self.author_handle = author_handle
            self.author_display_name = author_display_name
            self.text = text

    def get_post(self, slug, user, cid) -> list:
        try:
            if user is None:
                profile = self.profile
            else:
                profile = self.client.get_profile(user)
            res = self.client.get_post(slug, profile.did, cid)
            post_data = [self.PostData(res.uri, res.cid, profile.did, profile.handle, profile.display_name, res.value.text)]
            return post_data
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return None

    def get_posts(self, uris) -> list:
        try:
            res = self.client.get_posts(uris)
            post_data = []
            for post in res.posts:
                post_data.append(self.PostData(post.uri, post.cid, post.author.did, post.author.handle, post.author.display_name, post.record.text))
            return post_data
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return None

    def get_author_feed(self, user, limit=100) -> list:
        try:
            res = self.client.get_author_feed(user, limit=limit)
            post_data = []
            for feed in res.feed:
                post_data.append(self.PostData(feed.post.uri, feed.post.cid, feed.post.author.did, feed.post.author.handle, feed.post.author.display_name, feed.post.record.text))
            return post_data
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return None

    def get_timeline(self, limit=100) -> list:
        try:
            res = self.client.get_timeline(limit=limit)
            post_data = []
            for feed in res.feed:
                post_data.append(self.PostData(feed.post.uri, feed.post.cid, feed.post.author.did, feed.post.author.handle, feed.post.author.display_name, feed.post.record.text))
            return post_data
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return None

    def do(self, args) -> bool:
        login = Login()
        self.client = login.client()
        self.profile = login.profile()
        self.handle = login.handle()

        if args.param is None:
            posts = self.get_timeline(limit=args.limit)
        elif args.param.startswith('at://'):
            if is_joined_uri_cid(args.param):
                uri, cid = disjoin_uri_cid(args.param)
            else:
                uri = args.param
                cid = None
            returned_posts = self.get_posts([uri])
            posts = []
            for returned_post in returned_posts:
                if returned_post.uri == uri and (cid is None or returned_post.cid == cid):
                    posts.append(returned_post)
        elif args.param.startswith('did:'):
            posts = self.get_author_feed(args.param, limit=args.limit)
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
            posts = self.get_post(slug, user, cid)
        else:
            actor = expand_actor(args.param)
            posts = self.get_author_feed(actor, limit=args.limit)

        if posts is None:
            return False
        else:
            for post in posts:
                if args.id:
                    print(join_uri_cid(post.uri, post.cid))
                else:
                    display_name_summary = summarize(post.author_display_name)
                    text_summary = summarize(post.text, 40)
                    print(args.delimiter.join([join_uri_cid(post.uri, post.cid), post.author_did, post.author_handle, display_name_summary, text_summary]))

        return True