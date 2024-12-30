import sys
import atproto_client
from ssky.config import Config
from ssky.post_data_list import PostDataList
from ssky.util import disjoin_uri_cid, is_joined_uri_cid, join_uri_cid

class Repost:

    def name(self) -> str:
        return 'repost'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Repost')
        parser.add_argument('param', type=str, help='URI(at://...)[::CID]')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-O', '--output', type=str, default=None, metavar='DIR', help='Output to files')
        parser.set_defaults(format='')
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument('-I', '--id', action='store_const', dest='format', const='id', help='Print IDs (URI::CID) only')
        format_group.add_argument('-J', '--json', action='store_const', dest='format', const='json', help='Print in JSON format')
        format_group.add_argument('-L', '--long', action='store_const', dest='format', const='long', help='Print in long format')
        format_group.add_argument('-T', '--text', action='store_const', dest='format', const='text', help='Print text only')

    def do(self, args) -> bool:
        if is_joined_uri_cid(args.param):
            source_uri, source_cid = disjoin_uri_cid(args.param)
        else:
            source_uri = args.param
            source_cid = None

        try:
            client = Config().client()

            sources = client.get_posts([source_uri])
            for source_post in sources.posts:
                if source_post.uri == source_uri and (source_cid is None or source_post.cid == source_cid):
                    source = source_post
                    source_cid = source_post.cid
                    break

            repost = client.repost(source_uri, source_cid)
            if repost is None:
                return False

            post_data_list = PostDataList()
            post_data_list.append(source, uri_cid=join_uri_cid(repost.uri, repost.cid))
            post_data_list.print(format=args.format, output=args.output, delimiter=args.delimiter)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True