from atproto_client import models
from ssky.config import Config
from ssky.util import summarize

class ProfileList:

    class Item:
        profile: models.AppBskyActorDefs.ProfileViewDetailed = None

        def __init__(self, profile: models.AppBskyActorDefs.ProfileViewDetailed) -> None:
            self.profile = profile

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
            return '\n'.join([
                f'Created-At: {self.profile.created_at}',
                f'DID: {self.profile.did}',
                f'Display-Name: {self.profile.display_name}',
                f'Handle: {self.profile.handle}',
                '',
                f'{self.profile.description.rstrip()}'
            ])

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
        self.actors = []
        self.items = None
        if default_delimiter is not None:
            self.default_delimiter = default_delimiter

    def __str__(self) -> str:
        return str(self.actors)

    def append(self, actor: str) -> 'ProfileList':
        self.actors.append(actor)
        return self

    def update(self) -> 'ProfileList':
        if self.items is None:
            self.items = []
            block_count = len(self.actors) // 25 + 1
            for i in range(block_count):
                begin = i * 25
                end = (i + 1) * 25 if i + 1 < block_count else len(self.actors)
                profiles = Config().client().get_profiles(self.actors[begin:end]).profiles
                for profile in profiles:
                    self.items.append(self.Item(profile))
        return self

    def print(self, format: str, delimiter: str = None) -> None:
        self.update()
        continued = False
        for item in self.items:
            if format == 'long':
                if continued:
                    print('----------------')
                else:
                    continued = True
            print(item.printable(format, delimiter=delimiter))