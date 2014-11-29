from factory import Sequence, SubFactory, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from pairbutton.models import db, Channel, File

from faker import Faker


fake = Faker()


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class ChannelFactory(BaseFactory):
    class Meta:
        model = Channel

    name = Sequence(lambda n: 'mychannel{}'.format(n))
    key = Sequence(lambda n: 'mykey{}'.format(n))


class FileFactory(BaseFactory):
    class Meta:
        model = File

    name = LazyAttribute(lambda x: fake_filename())
    data = LazyAttribute(lambda x: fake_data())
    channel = SubFactory(ChannelFactory)


def fake_filename():
    return '{}.txt'.format(fake.word())


def fake_data():
    return '\n'.join(fake.paragraphs(nb=3))


def fake_file():
    return {'name': fake_filename(), 'data': fake_data()}


def fake_md5():
    return fake.md5()
