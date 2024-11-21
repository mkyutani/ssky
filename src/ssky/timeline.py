import re
import sys
from atproto import Client
import atproto_client
from ssky.env import Environment

class Timeline:

    def name(self) -> str:
        return 'timeline'

    def do(self, args) -> bool:
        return self.timeline(args)

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser('timeline', help='Show the timeline')
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument('-p', '--post', nargs=1, type=str, help='Post URI or CID to show by prefix search')
        format_group.add_argument('-u', '--user', nargs=1, type=str, help='User handle or display name to show by prefix search')
        format_group.add_argument('-t', '--text', nargs=1, type=str, help='Text fragment to show by full text search')

    def summarize(self, source, length_max):
        summary = re.sub(r'\s', '_', ''.join(list(map(lambda c: c if c > ' ' else ' ', source))))
        if len(summary) > length_max:
            summary = ''.join(summary[:length_max - 2]) + '..'
        return summary

    def timeline(self, args):
        env = Environment()

        try:
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
        except atproto_client.exceptions.UnauthorizedError as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return False
        except atproto_client.exceptions.BadRequestError as e:
            print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            return False
        except Exception as e:
            error_message = str(e)
            print(f'{error_message}', file=sys.stderr)
            return False

        return True