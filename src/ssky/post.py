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

def get_title_and_description(uris):
    title = None
    description = None

    headers = { 'Cache-Control': 'no-cache', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36' }

    for uri in uris:
        res = None
        try:
            res = requests.get(uri, headers=headers)
        except Exception as e:
            print(str(e), file=sys.stderr)
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
            print(f'Warning: No charset; assume utf-8', file=sys.stderr)
        else:
            charset = content_type_fragments[1].split('=')[1].strip().lower()
            if charset != 'utf-8':
                print(f'Unexpected charset {charset}', file=sys.stderr)
                continue

        if len(res.text) == 0:
            print('Empty content', file=sys.stderr)
            continue

        soup = BeautifulSoup(res.text, 'html.parser')

        result = soup.find('title')
        if result is None:
            title = 'No title'
        else:
            title = result.text

        result = soup.find('meta', attrs={'name': 'description'})
        if result is None:
            description = uri
        else:
            description = result.get('content')

        return {
            'title': title,
            'description': description,
            'uri': uri
        }

    return None

def create_embed_external(message):
    uris = re.findall(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', message)
    content = get_title_and_description(uris)
    if content is None:
        return None

    embed_external = models.AppBskyEmbedExternal.Main(
        external = models.AppBskyEmbedExternal.External(
            title = content['title'],
            description = content['description'],
            uri = content['uri']
        )
    )

    return embed_external

def ssky_post(args):
    env = Environment()

    client = Client()
    client.login(env.username(), env.password())

    if args.message:
        message = args.message
    else:
        message = sys.stdin.read()

    embed_external = create_embed_external(message)

    try:
        res = client.send_post(text=message, embed=embed_external)
    except atproto_client.exceptions.BadRequestError as e:
        print(f'{e.response.status_code} {e.response.content.message}', file=sys.stderr)
        return 1

    print(f'{res.uri} {res.cid}')

    return 0