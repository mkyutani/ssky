from datetime import datetime
import os
from atproto_client import models
from ssky.util import disjoin_uri_cid, join_uri_cid, summarize

class PostDataList:

    class Item:
        post: models.AppBskyFeedDefs.PostView = None

        def __init__(self, post: models.AppBskyFeedDefs.PostView, profile: models.AppBskyActorDefs.ProfileViewDetailed = None, uri_cid: str = None) -> None:
            self.post = post
            if profile:
                self.post.author = models.AppBskyActorDefs.ProfileViewBasic(
                    associated=profile.associated,
                    avatar=profile.avatar,
                    created_at=profile.created_at,
                    did=profile.did,
                    display_name=profile.display_name,
                    handle=profile.handle,
                    labels=profile.labels,
                    viewer=profile.viewer
                )
            if uri_cid:
                self.post.uri, self.post.cid = uri_cid.split('::')

        def id(self) -> str:
            return join_uri_cid(self.post.uri, self.post.cid)

        def text_only(self) -> str:
            return self.post.record.text.rstrip()

        def short(self, delimiter: str = None) -> str:
            if delimiter is None:
                delimiter = PostDataList.get_default_delimiter()
            uri_cid = self.id()
            author_did = self.post.author.did
            author_handle = self.post.author.handle
            display_name_summary = summarize(self.post.author.display_name)
            text_summary = summarize(self.post.record.text, length_max=40)
            return delimiter.join([uri_cid, author_did, author_handle, display_name_summary, text_summary])

        def long(self) -> str:
            uri, cid = disjoin_uri_cid(self.id())
            return '\n'.join([
                f'Author-DID: {self.post.author.did}',
                f'Author-Display-Name: {self.post.author.display_name}',
                f'Author-Handle: {self.post.author.handle}',
                f'Created-At: {self.post.record.created_at}',
                f'Record-CID: {cid}',
                f'Record-URI: {uri}',
                f'',
                self.post.record.text.rstrip()])

        def json(self) -> str:
            return models.utils.get_model_as_json(self.post)

        def printable(self, format: str, delimiter: str = None) -> str:
            if format == 'id':
                return self.id()
            elif format == 'long':
                return self.long()
            elif format == 'text':
                return self.text_only()
            elif format == 'json':
                return self.json()
            else:
                return self.short(delimiter=delimiter)

    default_delimiter = ' '

    @classmethod
    def set_default_delimiter(cls, delimiter: str) -> None:
        cls.default_delimiter = delimiter

    @classmethod
    def get_default_delimiter(cls) -> str:
        return cls.default_delimiter

    def __init__(self, default_delimiter: str = None) -> None:
        self.items = []
        if default_delimiter is not None:
            self.default_delimiter = default_delimiter

    def __str__(self) -> str:
        return str(self.uri_cids)

    def append(self, post: models.base.ModelBase, profile: models.AppBskyActorDefs.ProfileViewDetailed = None, uri_cid: str = None) -> 'PostDataList':
        self.items.append(self.Item(post, profile=profile, uri_cid=uri_cid))
        return self

    def print(self, format: str, output: str = None, delimiter: str = None) -> None:
        if output:
            for item in self.items:
                iso_datetime_str = item.created_at
                if iso_datetime_str is None:
                    iso_datetime_str = "1970-01-01T00:00:00.000Z"
                try:
                    datetime_obj = datetime.strptime(iso_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    datetime_obj = datetime.strptime(iso_datetime_str, "%Y-%m-%dT%H:%M:%S.%f+00:00")
                formatted_datetime_str = datetime_obj.strftime("%Y%m%d%H%M%S%fUTC")
                formatted_datetime_str = formatted_datetime_str[:-6] + formatted_datetime_str[-6:-3] + "000000UTC"
                filename = f"{item.author_handle}.{formatted_datetime_str}.txt"
                path = os.path.join(output, filename)
                with open(path, 'w') as f:
                    f.write(item.printable(format, delimiter=delimiter))
                    f.write('\n')
        else:
            continued = False
            for item in self.items:
                if format == 'long':
                    if continued:
                        print('----------------')
                    else:
                        continued = True
                print(item.printable(format, delimiter=delimiter))