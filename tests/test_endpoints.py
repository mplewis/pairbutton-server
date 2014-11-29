from .factories import ChannelFactory

from pairbutton.models import Channel

import pytest
import sure  # NOQA


class TestEndpointsWithoutAuth:
    @pytest.mark.usefixtures('db')
    class TestReadChannels:
        def test_read_channels(self, testapp, db):
            ChannelFactory()  # Create two channels
            ChannelFactory()
            resp = testapp.get('/channel')
            resp.json.should.have.length_of(2)
            resp.json[0].should_not.have.key('key')

    @pytest.mark.usefixtures('db')
    class TestCreateChannel:
        def test_create_channel(self, testapp, db):
            testapp.post('/channel')
            channels = db.session.query(Channel).all()
            len(channels).should.equal(1)

    @pytest.mark.usefixtures('db')
    class TestReadChannel:
        def test_read_channel(self, testapp, channel):
            testapp.get('/channel/{}'.format(channel.id))

    @pytest.mark.usefixtures('db')
    class TestReadFiles:
        def test_read_files(self, testapp, file):
            channel = file.channel
            headers = {'Auth-Key': channel.key}
            resp = testapp.get('/channel/{}/file'.format(channel.id),
                               headers=headers)
            resp.json.should.have.length_of(1)
            resp.json[0].should.have.key('id').should.equal(str(file.id))

    @pytest.mark.usefixtures('db')
    class TestReadFile:
        def test_read_file(self, testapp, file):
            channel = file.channel
            headers = {'Auth-Key': channel.key}
            testapp.get('/channel/{}/file/{}'.format(channel.id, file.id),
                        headers=headers)


class TestEndpointsWithAuth:
    @pytest.mark.usefixtures('db')
    class TestDeleteChannel:
        pass

    @pytest.mark.usefixtures('db')
    class TestCreateFile:
        pass

    @pytest.mark.usefixtures('db')
    class TestUpdateFile:
        pass

    @pytest.mark.usefixtures('db')
    class TestDeleteFile:
        pass
