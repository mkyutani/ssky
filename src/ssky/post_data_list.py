from datetime import datetime
import os
from atproto_client import models
from ssky.util import join_uri_cid, summarize

class PostDataList:

    class Item:
        uri: str = None
        cid: str = None
        author_did: str = None
        author_handle: str = None
        author_display_name: str = None
        text: str = None
        created_at: str = None

        def __init__(self, uri: str, cid: str, author_did: str, author_handle: str, author_display_name: str, text: str, created_at: str) -> None:
            self.uri = uri
            self.cid = cid
            self.author_did = author_did
            self.author_handle = author_handle
            self.author_display_name = author_display_name
            self.text = text
            self.created_at = created_at

        def id(self) -> str:
            return join_uri_cid(self.uri, self.cid)

        def text_only(self) -> str:
            return self.text.rstrip()

        def short(self, delimiter: str = None) -> str:
            if delimiter is None:
                delimiter = PostDataList.get_default_delimiter()
            uri_cid = self.id()
            author_did = self.author_did
            author_handle = self.author_handle
            display_name_summary = summarize(self.author_display_name)
            text_summary = summarize(self.text, length_max=40)
            return delimiter.join([uri_cid, author_did, author_handle, display_name_summary, text_summary])

        def long(self) -> str:
            return '\n'.join([
                f'Record-URI: {self.uri}',
                f'Record-CID: {self.cid}',
                f'Author-DID: {self.author_did}',
                f'Author-Handle: {self.author_handle}',
                f'Author-Display-Name: {self.author_display_name}',
                f'Created-At: {self.created_at}',
                f'',
                self.text.rstrip()])

        def printable(self, id_only: bool = False, text_only: bool = False, long_format: bool = False, delimiter: str = None) -> str:
            if id_only:
                return self.id()
            elif text_only:
                return self.text_only()
            elif long_format:
                return self.long()
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
        return str(self.items)

    def append(self, post: models.base.ModelBase, author: models.AppBskyActorDefs.ProfileViewDetailed = None, uri: str = None, cid: str = None, author_did: str = None, author_handle: str = None, author_display_name: str = None, text: str = None, created_at: str = None) -> 'PostDataList':
        if type(post) is models.AppBskyFeedPost.Record:
            if author is not None:
                author_did = author.did if author_did is None else author_did
                author_handle = author.handle if author_handle is None else author_handle
                author_display_name = author.display_name if author_display_name is None else author_display_name
            text = post.text if text is None else text
            created_at = post.created_at if created_at is None else created_at
        elif type(post) is models.AppBskyFeedDefs.PostView:
            uri = post.uri if uri is None else uri
            cid = post.cid if cid is None else cid
            if author is not None:
                author_did = author.did if author_did is None else author_did
                author_handle = author.handle if author_handle is None else author_handle
                author_display_name = author.display_name if author_display_name is None else author_display_name
            else:
                author_did = post.author.did if author_did is None else author_did
                author_handle = post.author.handle if author_handle is None else author_handle
                author_display_name = post.author.display_name if author_display_name is None else author_display_name
            text = post.record.text if text is None else text
            created_at = post.record.created_at if created_at is None else created_at

        self.items.append(self.Item(uri, cid, author_did, author_handle, author_display_name, text, created_at))

        return self

    def print(self, id_only: bool = False, text_only: bool = False, long_format: bool = False, output: str = None, delimiter: str = None) -> None:
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
                    f.write(item.printable(id_only=id_only, text_only=text_only, long_format=long_format, delimiter=delimiter))
                    f.write('\n')
        else:
            continued = False
            for item in self.items:
                if long_format:
                    if continued:
                        print('----------------')
                    else:
                        continued = True
                print(item.printable(id_only=id_only, text_only=text_only, long_format=long_format, delimiter=delimiter))