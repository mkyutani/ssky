from atproto_client import models
from ssky.util import join_uri_cid, summarize

class PostData:

    delimiter = ' '

    @classmethod
    def set_delimiter(cls, delimiter: str) -> None:
        if delimiter is not None:
            cls.delimiter = delimiter

    def __init__(self, uri: str = None, cid: str = None, author_did: str = None, author_handle: str = None, author_display_name: str = None, text: str = None):
        self.uri = uri
        self.cid = cid
        self.author_did = author_did
        self.author_handle = author_handle
        self.author_display_name = author_display_name
        self.text = text

    def __str__(self):
        display_name_summary = summarize(self.author_display_name)
        text_summary = summarize(self.text, 40)
        return PostData.delimiter.join([join_uri_cid(self.uri, self.cid), self.author_did, self.author_handle, display_name_summary, text_summary])

    def get_uri_cid(self) -> str:
        return join_uri_cid(self.uri, self.cid)

    def set(self, model: models.base.ModelBase) -> 'PostData':
        if type(model) is models.app.bsky.feed.defs.PostView:
            self.uri = model.uri
            self.cid = model.cid
            self.author_did = model.author.did
            self.author_handle = model.author.handle
            self.author_display_name = model.author.display_name
            self.text = model.record.text
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
        return self