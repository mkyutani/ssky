import os
import types
from dotenv import load_dotenv

class Environment:

    env = None

    @classmethod
    def init(cls):
        if cls.env is None:
            cls.env = types.SimpleNamespace()

            load_dotenv('.env')
            cls.env.username = os.environ.get('SSKY_USERNAME')
            cls.env.password = os.environ.get('SSKY_PASSWORD')

        return cls.env

    def user(self):
        env = Environment.init()
        if env.username is None or env.password is None:
            raise ValueError('Username and password must be set in the environment')
        return env.username, env.password

    def username(self):
        username, _ = self.user()
        return username

    def password(self):
        _, password = self.user()
        return password