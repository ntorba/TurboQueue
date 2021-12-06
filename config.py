class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/tq.db'

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/test_tq.db'
