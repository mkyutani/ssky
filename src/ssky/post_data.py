from atproto_client import models
from ssky.util import join_uri_cid, summarize

class PostData:

    default_delimiter = ' '

    @classmethod
    def set_default_delimiter(cls, delimiter: str) -> None:
        cls.default_delimiter = delimiter

    def __init__(self, uri: str = None, cid: str = None, author_did: str = None, author_handle: str = None, author_display_name: str = None, text: str = None, delimiter: str = None):
        self.uri = uri
        self.cid = cid
        self.author_did = author_did
        self.author_handle = author_handle
        self.author_display_name = author_display_name
        self.text = text
        self.created_at = None
        self.delimiter = delimiter if delimiter is not None else self.default_delimiter

    def __str__(self) -> str:
        uri_cid = self.get_uri_cid()
        author_did = self.author_did if self.author_did is not None else ''
        author_handle = self.author_handle if self.author_handle is not None else ''
        display_name_summary = summarize(self.author_display_name) if self.author_display_name is not None else ''
        text_summary = summarize(self.text, length_max=40) if self.text is not None else ''
        return self.delimiter.join([uri_cid, author_did, author_handle, display_name_summary, text_summary])

    def long(self) -> str:
        uri_cid = self.get_uri_cid()
        return '\n'.join([
            f'Record-URI: {self.uri if self.uri is not None else ""}',
            f'Record-CID: {self.cid if self.cid is not None else ""}',
            f'Author-DID: {self.author_did if self.author_did is not None else ""}',
            f'Author-Handle: {self.author_handle if self.author_handle is not None else ""}',
            f'Author-Display-Name: {self.author_display_name if self.author_display_name is not None else ""}',
            f'Created-At: {self.created_at if self.created_at is not None else ""}',
            f'',
            self.text])

    def get_uri_cid(self) -> str:
        return join_uri_cid(self.uri, self.cid) if self.uri is not None or self.cid is not None else ''

    def set_delimiter(self, delimiter: str) -> 'PostData':
        self.delimiter = delimiter if delimiter is not None else self.default_delimiter
        return self

    def set(self, model: models.base.ModelBase) -> 'PostData':
        if type(model) is models.AppBskyFeedDefs.PostView:
            self.uri = model.uri
            self.cid = model.cid
            self.author_did = model.author.did
            self.author_handle = model.author.handle
            self.author_display_name = model.author.display_name
            self.text = model.record.text
            self.created_at = model.record.created_at
        else:
            raise ValueError('Unsupported model type')
        return self

    def set_items(self, items: dict) -> 'PostData':
        self.uri = items['uri'] if 'uri' in items else self.uri
        self.cid = items['cid'] if 'cid' in items else self.cid
        self.author_did = items['author_did'] if 'author_did' in items else self.author_did
        self.author_handle = items['author_handle'] if 'author_handle' in items else self.author_handle
        self.author_display_name = items['author_display_name'] if 'author_display_name' in items else self.author_display_name
        self.text = items['text'] if 'text' in items else self.text
        self.created_at = items['created_at'] if 'created_at' in items else self.text
        return self