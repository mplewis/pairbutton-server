from pairbutton.helpers import channel_with_id, file_with_id

import pytest
import sure  # NOQA


@pytest.mark.usefixtures('db')
class TestGetByID:
    def test_get_channel(self, channel):
        retrieved = channel_with_id(channel.id)
        channel.id.should.equal(retrieved.id)

    def test_get_file(self, file):
        retrieved = file_with_id(file.channel.id, file.id)
        file.id.should.equal(retrieved.id)
