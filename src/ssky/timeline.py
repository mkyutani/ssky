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
        parser.add_argument('uri', nargs='?', type=str, help='Specify the URI to show')
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument('-d', '--detail', action='store_true', help='Show detail')
        format_group.add_argument('-y', '--yaml', action='store_true', help='In YAML format')

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
            if args.uri and feed.post.uri != args.uri:
                continue

            if args.detail or args.yaml:
                detail = {
                    'post': {
                        'author': {
                            'avatar': feed.post.author.avatar,
                            'create_at': feed.post.author.created_at,
                            'did': feed.post.author.did,
                            'display_name': feed.post.author.display_name,
                            'handle': feed.post.author.handle,
                            'labels': [ label for label in feed.post.author.labels ] if feed.post.author.labels else None
                        },
                        'cid': feed.post.cid,
                        'embed': None,
                        'indexed_at': feed.post.indexed_at,
                        'labels': [ label for label in feed.post.labels ] if feed.post.labels else None,
                        'like_count': feed.post.like_count,
                        'quote_count': feed.post.quote_count,
                        'record': {
                            'created_at': feed.post.record.created_at,
                            'text': feed.post.record.text,
                            'embed': None,
                            'langs': [ lang for lang in feed.post.record.langs ] if feed.post.record.langs else None,
                            'labels': [ label for label in feed.post.author.labels ] if feed.post.record.labels else None,
                            'reply': feed.post.record.reply,
                            'tags': [ tag for tag in feed.post.record.tags ] if feed.post.record.tags else None,
                        },
                        'reply_count': feed.post.reply_count,
                        'repost_count': feed.post.repost_count,
                        'uri': feed.post.uri
                    }
                }

                if args.yaml:
                    print(yaml.dump(detail))
                else:
                    pprint.pprint(detail, indent=2, compact=True)
            else:
                text_summary = self.summarize(feed.post.record.text, 40)
                display_name_summary = self.summarize(feed.post.author.display_name, 20)
                print(f'{feed.post.uri} {feed.post.cid} {feed.post.author.handle} {display_name_summary} {text_summary}')

        return True