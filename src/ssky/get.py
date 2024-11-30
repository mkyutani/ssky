import sys
from atproto import Client
import atproto_client
from ssky.env import Environment
from ssky.util import summarize

class Get:

    def name(self) -> str:
        return 'get'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Get posts')
        parser.add_argument('slug', type=str, help='URI slug (or slug with user handle or display name as USER:SLUG)')
        parser.add_argument('-c', '--cid', nargs=1, type=str, help='CID of the version')

    def do(self, args) -> bool:
        env = Environment()

        try:
            client = Client()
            profile = client.login(env.username(), env.password())

            if args.slug.startswith('at://'):
                if args.slug.count('/') != 4:
                    raise ValueError('Invalid URI format')
                slug_elements = args.slug.split('/')
                user = slug_elements[2]
                slug = slug_elements[4]
            elif args.slug.startswith('did:plc:'):
                slug_elements = args.slug.split(':')
                user = ':'.join(slug_elements[:3])
                slug = slug_elements[3]
            elif args.slug.count(':') == 1:
                slug_elements = args.slug.split(':')
                user = slug_elements[0]
                slug = slug_elements[1]
            else:
                user = None
                slug = args.slug

            if user is None:
                target_profile = profile
            else:
                target_profile = client.get_profile(user)
            cid = args.cid[0] if args.cid else None

            res = client.get_post(slug, profile_identify=user, cid=cid)
            text_summary = summarize(res.value.text, 40)
            target_profile_handle = target_profile.handle
            target_profile_display_name = target_profile.display_name
            print(f'{res.uri} {res.cid} {target_profile_handle} {target_profile_display_name} {text_summary}')
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