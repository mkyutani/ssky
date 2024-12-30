import re
import sys
from atproto import models
import atproto_client
from ssky.config import Config
from ssky.post_data_list import PostDataList
from ssky.util import expand_actor

class Search:

    def name(self) -> str:
        return 'search'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Search posts')
        parser.add_argument('q', type=str, metavar='QUERY', help='Query string')
        parser.add_argument('-a', '--author', type=str, metavar='ACTOR', help='Author handle or DID')
        parser.add_argument('-s', '--since', type=str, metavar='TIMESTAMP', help='Since timestamp (ex. 2001-01-01T00:00:00Z, 20010101000000, 20010101)')
        parser.add_argument('-u', '--until', type=str, metavar='TIMESTAMP', help='Until timestamp (ex. 2099-12-31T23:59:59Z, 20991231235959, 20991231)')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-N', '--limit', type=int, default=100, metavar='NUM', help='Limit lines (<=100)')
        formatting_group = parser.add_mutually_exclusive_group()
        formatting_group.add_argument('-I', '--id', action='store_true', help='Print IDs (URI::CID) only')
        formatting_group.add_argument('-L', '--long', action='store_true', help='Long output')
        formatting_group.add_argument('-T', '--text', action='store_true', help='Print text only')

    def do(self, args) -> bool:
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

        try:
            res = Config().client().app.bsky.feed.search_posts(
                models.AppBskyFeedSearchPosts.Params(
                    author=expand_actor(args.author),
                    limit=args.limit,
                    q=args.q,
                    since=since,
                    until=until
                )
            )
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False
        except atproto_client.exceptions.LoginRequiredError as e:
            print(str(e), file=sys.stderr)
            return False

        if res.posts and len(res.posts) > 0:
            post_data_list = PostDataList()
            for post in res.posts:
                post_data_list.append(post)
            post_data_list.print(id_only=args.id, text_only = args.text, long_format=args.long, delimiter=args.delimiter)

        return True