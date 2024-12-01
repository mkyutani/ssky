from atproto import Client
from ssky.env import Environment

class Login:

    class Session:
        def __init__(self, client=None, profile=None):
            self.client = client
            self.profile = profile

    session = None

    @classmethod
    def get_session(cls) -> Session:
        if cls.session is None:
            env = Environment()
            client = Client()
            profile = client.login(env.username(), env.password())
            cls.session = cls.Session(client, profile)
        return cls.session

    def client(self):
        return Login.get_session().client

    def profile(self):
        return Login.get_session().profile

    def did(self):
        return Login.get_session().profile.did

    def handle(self):
        return Login.get_session().profile.handle