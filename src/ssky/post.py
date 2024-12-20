import re
import sys
from atproto import IdResolver, models
import atproto_client
from bs4 import BeautifulSoup
import requests
from ssky.login import Login
from ssky.post_data import PostData
from ssky.util import disjoin_uri_cid, is_joined_uri_cid

class Post:

    def name(self) -> str:
        return 'post'

    def parse(self, subparsers) -> None:
        parser = subparsers.add_parser(self.name(), help='Post a message to the timeline')
        parser.add_argument('message', nargs='?', type=str, help='The message to post')
        parser.add_argument('-d', '--dry', action='store_true', help='Dry run')
        parser.add_argument('-i', '--image', action='append', type=str, default=[], metavar='PATH', help='Image files to attach')
        parser.add_argument('-q', '--quote', type=str, metavar='URI', help='Quote a post')
        parser.add_argument('-r', '--reply-to', type=str, metavar='URI', help='Reply to a post')
        parser.add_argument('-D', '--delimiter', type=str, default=' ', metavar='STRING', help='Delimiter')
        parser.add_argument('-I', '--id', action='store_true', help='Print IDs (URI::CID) only')

    def get_card(self, links):
        title = None
        description = None

        headers = { 'Cache-Control': 'no-cache', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36' }

        for key in links:
            uri = links[key]['uri']

            res = None
            try:
                res = requests.get(uri, headers=headers)
            except Exception as e:
                error_message = str(e)
                print(f'{error_message}', file=sys.stderr)
                continue

            if res.status_code >= 400:
                error = ' '.join([str(res.status_code), res.text if res.text is not None else ''])
                print(f'{error} ', file=sys.stderr)
                continue

            if not 'Content-Type' in res.headers:
                print('No Content-Type', file=sys.stderr)
                continue

            content_type_fragments = res.headers['Content-Type'].split(';')

            mime_type = content_type_fragments[0].strip().lower()
            if mime_type != 'text/html':
                print(f'Unexpected mime type {mime_type}', file=sys.stderr)
                continue

            if len(content_type_fragments) < 2:
                print(f'Warning: get_card: No charset; assume utf-8', file=sys.stderr)
            else:
                charset = content_type_fragments[1].split('=')[1].strip().lower()
                if charset != 'utf-8':
                    print(f'Unexpected charset {charset}', file=sys.stderr)
                    continue

            if len(res.text) == 0:
                print('Empty content', file=sys.stderr)
                continue

            soup = BeautifulSoup(res.content, 'html.parser')

            title = 'No title'
            result = soup.find('title')
            if result is not None:
                title = result.text
            else:
                result = soup.find('meta', attrs={'property': 'og:title'})
                if result is not None:
                    title = result.get('content')

            description = uri
            result = soup.find('meta', attrs={'name': 'description'})
            if result is not None:
                description = result.get('content')
            else:
                result = soup.find('meta', attrs={'property': 'og:description'})
                if result is not None:
                    description = result.get('content')

            thumbnail = None
            result = soup.find('meta', attrs={'property': 'og:image'})
            if result is not None:
                thumbnail = result.get('content')
                if len(thumbnail) == 0:
                    thumbnail = None

            return {
                'title': title,
                'description': description,
                'thumbnail': thumbnail,
                'uri': uri
            }

        return None

    def byte_len(self, text):
        return len(text.encode('UTF-8'))

    def search_items(self, text, pattern, property_name):
        matches = re.finditer(pattern, text)
        items = {}
        for m in matches:
            byte_start = self.byte_len(text[:m.start()])
            byte_end = byte_start + self.byte_len(m.group())
            items[f'{m.start():05d}'] = {
                'byte_start': byte_start,
                'byte_end': byte_end,
                'start': m.start(),
                'end': m.end(),
                property_name: m.group()
            }
        return items

    def get_links(self, message):
        return self.search_items(message, r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', 'uri')

    def get_tags(self, message):
        return self.search_items(message, r'#\S+', 'name')

    def get_mentions(self, message):
        mentions = self.search_items(message, r'@[\w.]+', 'handle')
        for key in mentions:
            name = mentions[key]['handle'][1:]
            resolver = IdResolver()
            did = resolver.handle.resolve(name)
            mentions[key]['did'] = did
        return mentions

    def get_thumbnail(self, uri):
        headers = { 'Cache-Control': 'no-cache', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36' }

        res = None
        try:
            res = requests.get(uri, headers=headers)
        except Exception as e:
            error_message = str(e)
            print(f'{error_message}', file=sys.stderr)
            return None

        if res.status_code >= 400:
            error = ' '.join([str(res.status_code), res.text if res.text is not None else ''])
            print(f'{error} ', file=sys.stderr)
            return None

        if not 'Content-Type' in res.headers:
            print('No Content-Type', file=sys.stderr)
            return None

        content_type_fragments = res.headers['Content-Type'].split(';')
        mime_type = content_type_fragments[0].strip().lower()
        if mime_type != 'image/jpeg' and mime_type != 'image/png' and mime_type != 'image/gif':
            print(f'Unexpected mime type {mime_type}', file=sys.stderr)
            return None

        return res.content

    def load_images(self, paths):
        images = []
        for path in paths:
            with open(path, 'rb') as f:
                images.append(f.read())
        return images

    def get_post(self, uri_cid):
        if is_joined_uri_cid(uri_cid):
            uri, cid = disjoin_uri_cid(uri_cid)
        else:
            uri = uri_cid
            cid = None
        retrieved_posts = Login().client().get_posts([uri])
        posts = []
        for retrieved_post in retrieved_posts.posts:
            if retrieved_post.uri == uri and (cid is None or retrieved_post.cid == cid):
                posts.append(retrieved_post)
        return posts[0]

    def do(self, args) -> bool:
        if args.message:
            message = args.message
        else:
            message = sys.stdin.read()

        message = message.strip()

        tags = self.get_tags(message)
        links = self.get_links(message)
        mentions = self.get_mentions(message)

        card = None
        if len(args.image) == 0 and not args.quote:
            card = self.get_card(links)

        if args.dry:
            print(message)
            for key in tags:
                print(args.delimiter.join(['Tag', tags[key]["name"]]))
            for key in links:
                print(args.delimiter.join(['Link', links[key]["uri"]]))
            for key in mentions:
                print(args.delimiter.join(['Mention', mentions[key]["did"], mentions[key]["handle"]]))
            for image in args.image:
                print(args.delimiter.join(['Image', image]))
            if card is not None:
                print(args.delimiter.join(['Card', card["uri"], card["title"], card["description"], card["thumbnail"]]))
            if args.reply_to:
                print(args.delimiter.join(['Reply to', args.reply_to]))
            return True

        facets = []
        for key in tags:
            facets.append(
                models.AppBskyRichtextFacet.Main(
                    features=[models.AppBskyRichtextFacet.Tag(tag=tags[key]['name'][1:])],
                    index=models.AppBskyRichtextFacet.ByteSlice(byte_start=tags[key]['byte_start'], byte_end=tags[key]['byte_end'])
                )
            )
        for key in links:
            facets.append(
                models.AppBskyRichtextFacet.Main(
                    features=[models.AppBskyRichtextFacet.Link(uri=links[key]['uri'])],
                    index=models.AppBskyRichtextFacet.ByteSlice(byte_start=links[key]['byte_start'], byte_end=links[key]['byte_end'])
                )
            )

        for key in mentions:
            facets.append(
                models.AppBskyRichtextFacet.Main(
                    features=[models.AppBskyRichtextFacet.Mention(did=mentions[key]['did'])],
                    index=models.AppBskyRichtextFacet.ByteSlice(byte_start=mentions[key]['byte_start'], byte_end=mentions[key]['byte_end'])
                )
            )

        try:
            client = Login().client()

            reply_to = None
            if args.reply_to:
                post_to_reply_to = self.get_post(args.reply_to)
                if post_to_reply_to is None:
                    return False
                reply_to = models.app.bsky.feed.post.ReplyRef(
                    parent=models.create_strong_ref(post_to_reply_to),
                    root=models.create_strong_ref(post_to_reply_to)
                )

            if card is not None:
                thumb_blob_ref = None
                if card['thumbnail'] is not None:
                    image = self.get_thumbnail(card['thumbnail'])
                    if image is not None:
                        res = client.upload_blob(image)
                        if res.blob is None:
                            print('Failed to upload thumbnail', file=sys.stderr)
                            return False
                        thumb_blob_ref = res.blob

                embed_external = models.AppBskyEmbedExternal.Main(
                    external = models.AppBskyEmbedExternal.External(
                        title = card['title'],
                        description = card['description'],
                        uri = card['uri'],
                        thumb = thumb_blob_ref
                    )
                )
                res = client.send_post(text=message, facets=facets, embed=embed_external, reply_to=reply_to)
            elif args.quote is not None:
                source = self.get_post(args.quote)
                if source is None:
                    return False
                embed_record = models.AppBskyEmbedRecord.Main(
                    record = models.ComAtprotoRepoStrongRef.Main(
                        uri = source.uri,
                        cid = source.cid
                    )
                )
                res = client.send_post(text=message, facets=facets, embed=embed_record, reply_to=reply_to)
            elif args.image is not None:
                if len(args.image) > 4:
                    print('Too many image files', file=sys.stderr)
                    return False
                images = self.load_images(args.image)
                res = client.send_images(text=message, facets=facets, images=images, reply_to=reply_to)
            else:
                res = client.send_post(text=message, facets=facets, reply_to=reply_to)

            posts = client.get_posts([res.uri])
            for post in posts.posts:
                post_data = PostData(delimiter=args.delimiter).set(post)
                if args.id:
                    print(post_data.get_uri_cid())
                else:
                    print(post_data)
        except atproto_client.exceptions.RequestErrorBase as e:
            if e.response:
                print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
            else:
                print(f'{e.__class__.__name__}', file=sys.stderr)
            return False

        return True