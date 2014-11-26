import pytest
from webtest import TestApp

from pairbutton.config import TestConfig
from pairbutton.app import create_app
from pairbutton.models import db as _db

from .factories import ChannelFactory, FileFactory


@pytest.yield_fixture(scope='function')
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def testapp(app):
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    _db.app = app

    yield _db

    _db.drop_all()


@pytest.fixture
def channel(db):
    channel = ChannelFactory()
    db.session.commit()
    return channel


@pytest.fixture
def file(db, channel=None):
    file = FileFactory()
    if not channel:
        channel = channel(db)
    file.channel_id = channel.id
    db.session.commit()
    return file
