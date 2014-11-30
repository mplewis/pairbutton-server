from .factories import ChannelFactory, fake_data, fake_file, fake_md5

from pairbutton.models import Channel
from pairbutton.helpers import diff, md5

import pytest
import sure  # NOQA


class TestEndpointsWithoutAuth:
    @pytest.mark.usefixtures('db')
    class TestReadChannels:
        def test_read_channels(self, testapp):
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
            channels.should.have.length_of(1)

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
        def test_delete_channel(self, testapp, db, channel):
            channels = db.session.query(Channel).all()
            channels.should.have.length_of(1)
            headers = {'Auth-Key': channel.key}
            testapp.delete('/channel/{}'.format(channel.id), headers=headers)
            channels = db.session.query(Channel).all()
            channels.should.have.length_of(0)

    @pytest.mark.usefixtures('db')
    class TestCreateFile:
        def test_create_file(self, testapp, channel):
            channel.files.should.have.length_of(0)
            headers = {'Auth-Key': channel.key}
            resp = testapp.post_json('/channel/{}/file'.format(channel.id),
                                     fake_file(), headers=headers)
            channel.files.should.have.length_of(1)
            resp.json.should_not.have.key('data')

    @pytest.mark.usefixtures('db')
    class TestUpdateFile:
        def test_update_file(self, testapp, file):
            old_data = file.data
            new_data = fake_data()
            data_diff = diff(old_data, new_data)
            expected_hash = md5(new_data)
            headers = {'Auth-Key': file.channel.key}
            diff_data = {'file_delta': data_diff,
                         'expected_hash': expected_hash}
            testapp.put_json('/channel/{}/file/{}'
                             .format(file.channel.id, file.id),
                             diff_data, headers=headers)
            file.data.should.equal(new_data)

        def test_update_file_bad_md5(self, testapp, file):
            old_data = file.data
            new_data = fake_data()
            data_diff = diff(old_data, new_data)
            headers = {'Auth-Key': file.channel.key}
            diff_data = {'file_delta': data_diff,
                         'expected_hash': fake_md5()}
            testapp.put_json('/channel/{}/file/{}'
                             .format(file.channel.id, file.id),
                             diff_data, headers=headers,
                             status=409)

        def test_update_file_bad_delta(self, testapp, file):
            new_data = fake_data()
            data_diff = diff(fake_data(), new_data)
            expected_hash = md5(new_data)
            headers = {'Auth-Key': file.channel.key}
            diff_data = {'file_delta': data_diff,
                         'expected_hash': expected_hash}
            testapp.put_json('/channel/{}/file/{}'
                             .format(file.channel.id, file.id),
                             diff_data, headers=headers,
                             status=409)

    @pytest.mark.usefixtures('db')
    class TestDeleteFile:
        def test_delete_file(self, testapp, file):
            file.channel.files.should.have.length_of(1)
            headers = {'Auth-Key': file.channel.key}
            testapp.delete_json('/channel/{}/file/{}'
                                .format(file.channel.id, file.id),
                                fake_file(), headers=headers)
            file.channel.files.should.have.length_of(0)
