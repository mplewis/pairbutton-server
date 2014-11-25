class TestConfig:
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # in-memory


class DevConfig:
    TESTING = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class ProdConfig:
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///prod.db'
