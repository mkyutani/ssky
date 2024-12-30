from atproto_client import models
from ssky.config import Config
from ssky.util import join_uri_cid, summarize

class ProfileList:

    class Item:
        profile: models.AppBskyActorDefs.ProfileViewDetailed

        def __init__(self, actor: str) -> None:
            self.profile = Config().client().get_profile(actor)

        def id(self) -> str:
            return self.profile.did

        def short(self, delimiter: str = None) -> str:
            if delimiter is None:
                delimiter = ProfileList.get_default_delimiter()
            did = self.profile.did
            handle = self.profile.handle
            display_name_summary = summarize(self.profile.display_name)
            description_summary = summarize(self.profile.description, length_max=40)
            return delimiter.join([did, handle, display_name_summary, description_summary])

        def long(self) -> str:
            return '\n'.join(
                filter(
                    lambda x: x is not None,
                    [
                        f'DID: {self.profile.did}' if self.profile.did else None,
                        f'Handle: {self.profile.handle}' if self.profile.handle else None,
                        f'Display-Name: {self.profile.display_name}' if self.profile.display_name else None,
                        f'Created-At: {self.profile.created_at}' if self.profile.created_at else None,
                        '',
                        f'{self.profile.description.rstrip()}' if self.profile.description else None
                    ]
                )
            )

        def json(self) -> str:
            return models.utils.get_model_as_json(self.profile)

        def printable(self, format: str, delimiter: str = None) -> str:
            if format == 'id':
                return self.id()
            elif format == 'long':
                return self.long()
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
        return str(self.items)

    def append(self, actor: str) -> 'ProfileList':
        self.items.append(self.Item(actor))
        return self

    def print(self, format: str, delimiter: str = None) -> None:
        continued = False
        for item in self.items:
            if format == 'long':
                if continued:
                    print('----------------')
                else:
                    continued = True
            print(item.printable(format, delimiter=delimiter))