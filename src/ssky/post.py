import re
import sys
from atproto import Client, models
import atproto_client
from bs4 import BeautifulSoup
import requests
from ssky.env import Environment

def ssky_post_parser(subparsers):
    parser = subparsers.add_parser('post', help='Post a message to the timeline')
    parser.add_argument('message', nargs='?', type=str, help='The message to post')
    parser.add_argument('--image', nargs='+', type=str, help='Image files to attach')
    parser.add_argument('--dry', action='store_true', help='Dry run')

def get_card(links):
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
            print(f'get_card: {error_message}', file=sys.stderr)
            continue

        if res.status_code >= 400:
            error = ' '.join([str(res.status_code), res.text if res.text is not None else ''])
            print(f'{error} ', file=sys.stderr)
            continue

        if not 'Content-Type' in res.headers:
            print('get_card: No Content-Type', file=sys.stderr)
            continue

        content_type_fragments = res.headers['Content-Type'].split(';')

        mime_type = content_type_fragments[0].strip().lower()
        if mime_type != 'text/html':
            print(f'get_card: Unexpected mime type {mime_type}', file=sys.stderr)
            continue

        if len(content_type_fragments) < 2:
            print(f'Warning: get_card: No charset; assume utf-8', file=sys.stderr)
        else:
            charset = content_type_fragments[1].split('=')[1].strip().lower()
            if charset != 'utf-8':
                print(f'get_card: Unexpected charset {charset}', file=sys.stderr)
                continue

        if len(res.text) == 0:
            print('get_card: Empty content', file=sys.stderr)
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

        return {
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'uri': uri
        }

    return None

def byte_len(text):
    return len(text.encode('UTF-8'))

def get_links(message):
    links = {}

    matches =  re.finditer(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', message)
    for m in matches:
        byte_start = byte_len(message[:m.start()])
        byte_end = byte_start + byte_len(m.group())
        links[f'{m.start():05d}'] = {
            'byte_start': byte_start,
            'byte_end': byte_end,
            'start': m.start(),
            'end': m.end(),
            'uri': m.group()
        }

    return links

def get_thumbnail(uri):
    headers = { 'Cache-Control': 'no-cache', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36' }

    res = None
    try:
        res = requests.get(uri, headers=headers)
    except Exception as e:
        error_message = str(e)
        print(f'get_thumbnail: {error_message}', file=sys.stderr)
        return None

    if res.status_code >= 400:
        error = ' '.join([str(res.status_code), res.text if res.text is not None else ''])
        print(f'get_thumbnail: {error} ', file=sys.stderr)
        return None

    if not 'Content-Type' in res.headers:
        print('get_thumbnail: No Content-Type', file=sys.stderr)
        return None

    content_type_fragments = res.headers['Content-Type'].split(';')
    mime_type = content_type_fragments[0].strip().lower()
    if mime_type != 'image/jpeg' and mime_type != 'image/png' and mime_type != 'image/gif':
        print(f'get_thumbnail: Unexpected mime type {mime_type}', file=sys.stderr)
        return None

    return res.content

def get_tags(message):
    tags = {}

    matches = re.finditer(r'#\S+', message)
    for m in matches:
        byte_start = byte_len(message[:m.start()])
        byte_end = byte_start + byte_len(m.group())
        tags[f'{m.start():05d}'] = {
            'byte_start': byte_start,
            'byte_end': byte_end,
            'start': m.start(),
            'end': m.end(),
            'name': m.group()
        }

    return tags

def load_images(paths):
    images = []
    for path in paths:
        with open(path, 'rb') as f:
            images.append(f.read())
    return images

def ssky_post(args):
    env = Environment()

    if args.message:
        message = args.message
    else:
        message = sys.stdin.read()

    message = message.strip()

    tags = get_tags(message)
    links = get_links(message)

    if args.image is not None:
        card = None
    else:
        card = get_card(links)

    if args.dry:
        print(message)
        for key in tags:
            print(f'- tag {tags[key]["name"]}')
        for key in links:
            print(f'- link {links[key]["uri"]}')
        if card is not None:
            print(f'- card {card["uri"]} {card["title"]} {card["description"]} {card["thumbnail"]}')
        if args.image is not None:
            print(f'- images {",".join(args.image)}')
    else:
        try:
            client = Client()
            client.login(env.username(), env.password())

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

            if card is not None:
                thumb_blob_ref = None
                if card['thumbnail'] is not None:
                    image = get_thumbnail(card['thumbnail'])
                    if image is not None:
                        res = client.upload_blob(image)
                        if res.blob is None:
                            print('ssky_post: Failed to upload thumbnail', file=sys.stderr)
                            return 1
                        thumb_blob_ref = res.blob

                embed_external = models.AppBskyEmbedExternal.Main(
                    external = models.AppBskyEmbedExternal.External(
                        title = card['title'],
                        description = card['description'],
                        uri = card['uri'],
                        thumb = thumb_blob_ref
                    )
                )
                res = client.send_post(text=message, facets=facets, embed=embed_external)
            elif args.image is not None:
                if len(args.image) > 4:
                    print('ssky_post: Too many image files', file=sys.stderr)
                    return 1
                images = load_images(args.image)
                res = client.send_images(text=message, facets=facets, images=images)
            else:
                res = client.send_post(text=message, facets=facets)

            print(f'{res.uri} {res.cid}')
        except atproto_client.exceptions.UnauthorizedError as e:
            print(f'{e.response.status_code} ssky_post: {e.response.content.message}', file=sys.stderr)
            return 1
        except atproto_client.exceptions.BadRequestError as e:
            print(f'{e.response.status_code} ssky_post: {e.response.content.message}', file=sys.stderr)
            return 1
        except Exception as e:
            error_message = str(e)
            print(f'ssky_post: {error_message}', file=sys.stderr)
            return 1

    return 0