from atproto_client import models
from ssky.util import join_uri_cid, summarize

class ActorList:

    class Item:
        did: str = None
        handle: str = None
        display_name: str = None
        description: str = None
        avatar: str = None
        created_at: str = None

        def __init__(self, did: str, handle: str, display_name: str, description: str, avatar: str, created_at: str) -> None:
            self.did = did
            self.handle = handle
            self.display_name = display_name
            self.description = description
            self.avatar = avatar
            self.created_at = created_at

        def id(self) -> str:
            return self.did

        def short(self, delimiter: str = None) -> str:
            if delimiter is None:
                delimiter = ActorList.get_default_delimiter()
            did = self.did
            handle = self.handle
            display_name_summary = summarize(self.display_name)
            description_summary = summarize(self.description, length_max=40)
            return delimiter.join([did, handle, display_name_summary, description_summary])

        def long(self) -> str:
            return '\n'.join([
                f'DID: {self.did}',
                f'Handle: {self.handle}',
                f'Display-Name: {self.display_name}',
                f'Description: {self.description}',
                f'Avatar: {self.avatar}',
                f'Created-At: {self.created_at}'])

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

    def append(self, author: models.base.ModelBase, did: str = None, handle: str = None, display_name: str = None, description: str = None,  avatar: str = None, created_at: str = None) -> 'ActorList':
        if type(author) is models.AppBskyActorDefs.ProfileView:
            did = author.did if did is None else did
            handle = author.handle if handle is None else handle
            display_name = author.display_name if display_name is None else display_name
            description = author.description if description is None else description
            avatar = author.avatar if avatar is None else avatar
            created_at = author.created_at if created_at is None else created_at

        self.items.append(self.Item(did=did, handle=handle, display_name=display_name, description=description, avatar=avatar, created_at=created_at))

        return self

    def create_printable_list(self, id_only: bool = False, long_format: bool = False, delimiter: str = None) -> list[str]:
        if id_only:
            return [item.id() for item in self.items]
        elif long_format:
            return [item.long() for item in self.items]
        else:
            return [item.short(delimiter=delimiter) for item in self.items]

    def print(self, id_only: bool = False, long_format: bool = False, delimiter: str = None) -> None:
        printable_list = self.create_printable_list(id_only=id_only, long_format=long_format, delimiter=delimiter)
        continued = False
        for printable in printable_list:
            if long_format:
                if continued:
                    print('----------------')
                else:
                    continued = True
            print(printable)