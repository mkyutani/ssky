import pprint
import re
import yaml
from atproto import Client
from ssky.env import Environment

class Timeline:

    def name(self) -> str:
        return 'timeline'

    def do(self, args) -> bool:
        return self.timeline(args)

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser('timeline', help='Show the timeline')
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument('--post', nargs=1, type=str, help='Specify the URI or CID to show')
        format_group.add_argument('--user', nargs=1, type=str, help='Specify the handle or display name to show')
        format_group.add_argument('--text', nargs=1, type=str, help='Specify the text to show')

    def summarize(self, source, length):
        summary = re.sub(r'\s', '_', ''.join(list(map(lambda c: c if c > ' ' else ' ', source))))
        if len(summary) > length:
            summary = ''.join(summary[:length - 2]) + '..'
        return summary

    def timeline(self, args):
        env = Environment()

        client = Client()
        client.login(env.username(), env.password())

        res = client.get_timeline()

        for feed in res.feed:
            if args.post:
                post_lower = args.post[0].lower()
                if not feed.post.uri.lower().startswith(post_lower) and not feed.post.cid.lower().startswith(post_lower):
                    continue
            if args.user:
                user_lower = args.user[0].lower()
                if not feed.post.author.handle.lower().startswith(user_lower) and not feed.post.author.display_name.lower().startswith(user_lower):
                    continue
            if args.text:
                text_lower = args.text[0].lower()
                if not feed.post.record.text.lower().find(text_lower) == 0:
                    continue

            text_summary = self.summarize(feed.post.record.text, 40)
            display_name_summary = self.summarize(feed.post.author.display_name, 20)
            print(f'{feed.post.uri} {feed.post.cid} {feed.post.author.handle} {display_name_summary} {text_summary}')

        return True