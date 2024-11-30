from atproto import Client
from ssky.env import Environment

class Login:

    class Session:
        def __init__(self):
            self.client = None
            self.profile = None

    session = None

    @classmethod
    def init(cls) -> Session:
        if cls.session is None:
            env = Environment()
            cls.session = cls.Session()
            cls.session.client = Client()
            cls.session.profile = cls.session.client.login(env.username(), env.password())
        return cls.session

    def client(self):
        session = self.init()
        return self.session.client

    def profile(self):
        session = self.init()
        return self.session.profile