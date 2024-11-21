import re
from atproto import Client, IdResolver
from ssky.env import Environment

class User:

    def name(self) -> str:
        return 'user'

    def do(self, args) -> bool:
        return self.user(args)

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser('user', help='Show user')
        parser.add_argument('name', nargs=1, type=str, help='Handle or DID to show')

    def user(self, args):
        env = Environment()

        client = Client()
        client.login(env.username(), env.password())

        resolver = IdResolver()
        if args.name[0].lower().startswith('did:'):
            did = args.name[0]
        else:
            did = resolver.handle.resolve(args.name[0])
            if did is None:
                print(f'User not found')
                return False

        did_doc = resolver.did.resolve(did)
        if did_doc is None:
            print(f'User not found')
            return False

        did = did_doc.get_did()
        handle = did_doc.get_handle()
        print(f'{did} {handle}')

        return True