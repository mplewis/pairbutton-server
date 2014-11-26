from factory import Factory
from pairbutton.models import Channel, File


class ChannelFactory(Factory):
    class Meta:
        model = Channel

    name = 'mychannel'
    key = 'mypkey'


class FileFactory(Factory):
    class Meta:
        model = File

    name = 'myfile'
    data = 'mydata'
