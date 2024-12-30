import json
import os
from atproto import Client
import atproto_client

class Config:

    class Session:
        def __init__(self, client=None, profile=None):
            self.client = client
            self.profile = profile

    env_path = os.path.expanduser('~/.ssky')
    session = None

    @classmethod
    def at_login(cls, handle=None, password=None, session_string=None):
        client = Client()
        profile = client.login(login=handle, password=password, session_string=session_string)
        cls.session = cls.Session(client, profile)
        return cls.session

    @classmethod
    def login(cls, handle=None, password=None):
        if cls.session is None:
            var_user = os.environ.get('SSKY_USER')
            if var_user is not None:
                handle, password = var_user.split(':')
                cls.at_login(handle=handle, password=password)
            elif handle is not None or password is not None:
                cls.at_login(handle=handle, password=password)
            elif os.path.exists(cls.env_path) and os.path.isfile(cls.env_path):
                with open(cls.env_path, 'r') as f:
                    persistent_config = json.load(f)
                    session_string = persistent_config.get('session_string')
                    cls.at_login(session_string=session_string)
            else:
                raise atproto_client.exceptions.LoginRequiredError('No credentials found. Please set SSKY_USER (HANDLE:PASSWORD) environment variable or run ssky login')

        if cls.session is None:
            raise atproto_client.exceptions.LoginRequiredError('Login first')
        return cls.session.client

    @classmethod
    def persist(cls):
        if cls.session is not None:
            session_string = cls.session.client.export_session_string()
            with open(cls.env_path, 'w') as f:
                json.dump({
                    'session_string': session_string
                }, f)

    def __init__(self, handle=None, password=None):
        Config.login(handle=handle, password=password)

    def client(self):
        if self.session is None:
            raise ValueError('Login first')
        return self.session.client

    def profile(self):
        if self.session is None:
            raise ValueError('Login first')
        return self.session.profile