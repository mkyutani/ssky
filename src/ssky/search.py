import sys
from atproto import models
import atproto_client
from ssky.login import Login
from ssky.util import expand_actor, summarize

class Search:

    def name(self) -> str:
        return 'search'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Search posts')
        parser.add_argument('q', type=str, help='Query string')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', help='Delimiter')
        parser.add_argument('-a', '--author', type=str, help='Author handle or DID')
        parser.add_argument('-I', '--id', action='store_true', help='Show ID (DID) only')
        parser.add_argument('-L', '--limit', type=int, default=100, help='Limit lines (<= 100; default: 100)')

    def do(self, args) -> bool:
        try:
            login = Login()
            client = login.client()

            res = client.app.bsky.feed.search_posts(
                models.app.bsky.feed.search_posts.Params(
                    author=expand_actor(args.author),
                    limit=args.limit,
                    q=args.q
                )
            )

            for post in res.posts:
                if args.id:
                    print(post.uri)
                else:
                    display_name_summary = summarize(post.author.display_name)
                    text_summary = summarize(post.record.text, 40)
                    print(args.delimiter.join([post.uri, post.cid, post.author.did, post.author.handle, display_name_summary, text_summary]))
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return False

        return True