import sys
from atproto import models
import atproto_client
from ssky.actor_list import ActorList
from ssky.config import Config

class User:

    def name(self) -> str:
        return 'user'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Search users')
        parser.add_argument('q', type=str, metavar='QUERY', help='Query string')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-I', '--id', action='store_true', help='Print IDs (URI::CID) only')
        parser.add_argument('-L', '--long', action='store_true', help='Long output')
        parser.add_argument('-N', '--limit', type=int, default=100, metavar='NUM', help='Limit lines (<=100)')

    def do(self, args) -> bool:
        try:
            res = Config().client().app.bsky.actor.search_actors(
                models.AppBskyActorSearchActors.Params(
                    limit=args.limit,
                    q=args.q
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

        if len(res.actors) > 0:
            actor_list = ActorList()
            for actor in res.actors:
                actor_list.append(actor)
            actor_list.print(id_only=args.id, long_format=args.long, delimiter=args.delimiter)

        return True