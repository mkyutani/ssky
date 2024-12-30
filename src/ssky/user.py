import sys
from atproto import models
import atproto_client
from ssky.profile_list import ProfileList
from ssky.config import Config

class User:

    def name(self) -> str:
        return 'user'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Search users')
        parser.add_argument('q', nargs='?', type=str, default='*', metavar='QUERY', help='Query string')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-N', '--limit', type=int, default=100, metavar='NUM', help='Limit lines (<=100)')
        parser.set_defaults(format='')
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument('-I', '--id', action='store_const', dest='format', const='id', help='Print IDs (URI::CID) only')
        format_group.add_argument('-J', '--json', action='store_const', dest='format', const='json', help='Print in JSON format')
        format_group.add_argument('-L', '--long', action='store_const', dest='format', const='long', help='Print in long format')

    def do(self, args) -> bool:
        try:
            res = Config().client().app.bsky.actor.search_actors(
                models.AppBskyActorSearchActors.Params(
                    limit=args.limit,
                    q=args.q
                )
            )

            actor_list = ProfileList()
            for actor in res.actors:
                actor_list.append(actor.did)
            actor_list.print(format=args.format, delimiter=args.delimiter)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False
        except atproto_client.exceptions.LoginRequiredError as e:
            print(str(e), file=sys.stderr)
            return False

        return True