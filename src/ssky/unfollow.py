import sys
import atproto_client
from atproto import models
from ssky.config import Config
from ssky.util import expand_actor

class Unfollow:

    def name(self) -> str:
        return 'unfollow'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Unfollow')
        parser.add_argument('name', type=str, help='Handle or DID to unfollow')

    def do(self, args) -> bool:
        try:
            actor = expand_actor(args.name)
            res = Config().client().get_follows(Config().profile().did)
            for follow in res.follows:
                if follow.did == actor or follow.handle == actor:
                    if follow.viewer.following:
                        status = Config().client().unfollow(follow.viewer.following)
                        if status is False:
                            print('Failed to unfollow', file=sys.stderr)
                            return False
                        print('Unfollowed successfully', file=sys.stderr)
                    else:
                        print(f'You are not following {actor}', file=sys.stderr)
                    break
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True