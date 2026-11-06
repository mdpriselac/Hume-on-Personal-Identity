import os

basedir = os.path.abspath(os.path.dirname(__file__))


def _secret_key():
    key = os.environ.get('SECRET_KEY')
    if not key:
        raise RuntimeError('SECRET_KEY is not set. Set it to a long random string, '
                           'for example: SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")')
    return key


class Config(object):
    SECRET_KEY = _secret_key()
