# ssky - Simple bluesky client

## Introduction

### Requirements

* Python 3.12 or later

### Install

```bash
pip install git+https://github.com/mkyutani/ssky.git
```

### Setup

Set Bluesky handle and password in environment variables: SSKY_USERNAME and SSKY_PASSWORD respectively.

```sh
export SSKY_USERNAME=user.bsky.social
export SSKY_PASSWORD=xxxx-xxxxx-xxxx-xxxx
```

Temporal environment variables are also effective.

```sh
SSKY_USERNAME=user.bsky.social SSKY_PASSWORD=xxxx-xxxxx-xxxx-xxxx ssky ...
```

## Quick Start

Command line interfaces are formatted by `ssky subcommand [options]`, while subcommand is one of `get`, `post`, `profile`, and `search`. and options depends on the the subcommand without some common ones.

### Common options

* -D, --delimiter: Delimiter string in output
* -I, --id: Output only identifier, depending on context (ex. URI and DID)
* -L, --limit: limit lines when multiple line output like get and search subcommands

### Common names

* Each subcommand allows "myself" instead of the logged in user DID or handle.

### Get posts

Get subcommand retrieves my timeline, author's feed, and a post by URI or slug.

```sh
ssky get # Get my timeline (already described)
ssky get handle # Get other author's feed by handle
ssky get did:... # Get other author's feed by DID
ssky get at://... # Get a post specified by URI
ssky get at://...::cig # Get a post specified by URI and CIG
ssky get handle:slug # Get a post specified by author's handle and slug of URI
ssky get handle:slug:cid # Get a post specified by author's handle and slug of URI with CID version
```

### Get profile

Profile subcommand retrieves the user profile from handle or display name.

```sh
ssky profile user.bsky.social
ssky profile 'Display Name'
```

### Post

Post subcommand sends a post. The message to post is given by command line argument or the standard input.  Tags, link cards, mentions, reply-to and attached images are available.

```sh
ssky post Hello # Post from command line text
echo Hello | ssky post # Post from /dev/stdin
ssky post 'Hello, #bluesky @atproto.com https://bsky.app/' # Post with tags, mentions, and embed link card
ssky post 'Hello, bluesky!' --image hello.png hello2.png # Post with images
ssky post 'Hello, bluesky!' --reply-to at://... # Reply to the post specified by URI
ssky post 'Hello, bluesky!' --reply-to at://...::cig # Reply to the post specified by URI (CIG is ignored)

ssky post Hello --dry # Dry run
```

### Search post

Search subcommand searches posts with user query.

```sh
ssky search foo # Search posts including "foo"
ssky search foo -a handle # Search posts including "foo" by the specified author
```

### Delete post

Delete subcommand deletes a post.

```sh
ssky delete at://... # Delete the post specified by URI
ssky delete at://...::cig # Delete the post specified by URI (CIG is ignored)
```

### Repost

Repost subcommand repost the post.

```sh
ssky repost at://...::cig # Repost the post specified by URI and CIG
```

### Unrepost

Repost subcommand delete the repost to a post.

```sh
ssky unrepost at://... # Delete the repost specified by URI
ssky unrepost at://...::cig # Delete the repost specified by URI (CIG is ignored)
```

## Samples

### Reply to the last post by myself

```sh
ssky post Reply! --reply-to $(ssky get myself --limit 1 --id)
```

## License

[Apache 2.0 License](LICENSE)

## Author

[Miki Yutani](https://github.com/mkyutani)
