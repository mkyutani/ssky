# ssky - Simple Bluesky Client

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

Command line interfaces are formatted by `ssky subcommand [options]`, while subcommand is one of timeline, post, profile, etc. and options depends on the the subcommand.

### Timeline

Timeline subcommand retrieves the latest time line of the logged in user.

```sh
ssky timeline
```

### Post

Post subcommand send a post. The message to post is given by command line argument or the standard input.  Tags, link cards and mentions are avaiable but reply-to mechanism is not implemented yet.  Optional argument --image specifies the local image file path to send with the message.  Optional flag --dry make the command not to send a post but only to print the message.

```sh
ssky post Hello
echo Hello | ssky post
ssky 'Hello, #bluesky! https://bsky.app/ @atproto.com'
ssky 'Hello, bluesky!' --image hello.png hello2.png

ssky post Hello --dry # Dry run
```

### Get post

Get subcommand retrieves post from slug of the post URI, that is the last unique string, such as https://bsky.app/profile/user.bsky.social/post/**slug**.
User handle or display name is necessary to be retrieved posts other than the logged in user.  Optional argument with --cid specifies CID for the version of the post.

```sh
ssky get user:slug
ssky get slug # logged in user's post
ssky get slug --cid cid
```

### Get profile

Profile subcommand retrieves the user profile from handle or display name.

```sh
ssky profile user.bsky.social
ssky profile 'Display Name'
```

## License

[Apache 2.0 License](LICENSE)

## Author

[Miki Yutani](mkyutnai@gmail.com)
