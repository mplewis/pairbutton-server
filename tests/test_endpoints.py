from pairbutton.models import Channel

import pytest
import sure  # NOQA


@pytest.mark.usefixtures('db')
class TestEndpointsWithoutAuth:
    def test_create_channel(self, testapp, db):
        testapp.post('/channel')
        channels = db.session.query(Channel).all()
        len(channels).should.equal(1)


@pytest.mark.usefixtures('db')
class TestEndpointsWithAuth:
    def test_get_channel(self, testapp, channel):
        headers = {'Auth-Key': channel.key}
        testapp.get('/channel/{}'.format(channel.id), headers=headers)

    def test_get_files(self, testapp, file):
        channel = file.channel
        headers = {'Auth-Key': channel.key}
        resp = testapp.get('/channel/{}/file'.format(channel.id),
                           headers=headers)
        resp.json.should.have.length_of(1)
        resp.json[0].should.have.key('id').should.equal(str(file.id))


    def test_get_file(self, testapp, file):
        channel = file.channel
        headers = {'Auth-Key': channel.key}
        testapp.get('/channel/{}/file/{}'.format(channel.id, file.id),
                    headers=headers)


@pytest.mark.usefixtures('db')
class TestEndpointsUnauthorized:
    def test_get_channel_bad_key(self, testapp, channel):
        headers = {'Auth-Key': 'INVALID_KEY'}
        testapp.get('/channel/{}'.format(channel.id), None, headers, status=403)

    def test_get_channel_no_key(self, testapp, channel):
        testapp.get('/channel/{}'.format(channel.id), status=403)
