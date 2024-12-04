import re
import sys
from atproto import models
import atproto_client
from ssky.login import Login
from ssky.util import expand_actor, join_uri_cid, summarize

class Search:

    def name(self) -> str:
        return 'search'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Search posts')
        parser.add_argument('q', type=str, metavar='QUERY', help='Query string')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-a', '--author', type=str, metavar='ACTOR', help='Author handle or DID')
        parser.add_argument('-I', '--id', action='store_true', help='Print IDs (URI::CID) only')
        parser.add_argument('-L', '--limit', type=int, default=100, metavar='NUM', help='Limit lines (<=100)')
        parser.add_argument('-s', '--since', type=str, metavar='TIMESTAMP', help='Since timestamp (ex. 2001-01-01T00:00:00Z, 20010101000000, 20010101)')
        parser.add_argument('-u', '--until', type=str, metavar='TIMESTAMP', help='Until timestamp (ex. 2099-12-31T23:59:59Z, 20991231235959, 20991231)')

    def do(self, args) -> bool:
        try:
            login = Login()
            client = login.client()

            if args.since:
                if re.match(r'^\d{14}$', args.since):
                    since = f'{args.since[:4]}-{args.since[4:6]}-{args.since[6:8]}T{args.since[8:10]}:{args.since[10:12]}:{args.since[10:12]}Z'
                elif re.match(r'^\d{8}$', args.since):
                    since = f'{args.since[:4]}-{args.since[4:6]}-{args.since[6:8]}T00:00:00Z'
                else:
                    since = args.since
            else:
                since = None

            if args.until:
                if re.match(r'^\d{14}$', args.until):
                    until = f'{args.until[:4]}-{args.until[4:6]}-{args.until[6:8]}T{args.until[8:10]}:{args.until[10:12]}:{args.until[10:12]}Z'
                elif re.match(r'^\d{8}$', args.until):
                    until = f'{args.until[:4]}-{args.until[4:6]}-{args.until[6:8]}T23:59:59Z'
                else:
                    until = args.until
            else:
                until = None

            res = client.app.bsky.feed.search_posts(
                models.app.bsky.feed.search_posts.Params(
                    author=expand_actor(args.author),
                    limit=args.limit,
                    q=args.q,
                    since=since,
                    until=until
                )
            )

            for post in res.posts:
                if args.id:
                    print(join_uri_cid(post.uri, post.cid))
                else:
                    display_name_summary = summarize(post.author.display_name)
                    text_summary = summarize(post.record.text, 40)
                    print(args.delimiter.join([join_uri_cid(post.uri, post.cid), post.author.did, post.author.handle, display_name_summary, text_summary]))
        except atproto_client.exceptions.RequestErrorBase as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return False

        return True