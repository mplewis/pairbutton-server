from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    key = db.Column(db.Text)

    def __init__(self, name, key):
        self.name = name
        self.key = key

    def __repr__(self):
        return '<Channel: {}, {}>'.format(self.id, self.name)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    data = db.Column(db.Text)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship(Channel, backref='files')

    def __init__(self, name, data, channel):
        self.name = name
        self.data = data
        self.channel = channel

    def __repr__(self):
        some_data = self.data[:40]
        if len(self.data) > 40:
            some_data += '...'
        return ('<File: {}, {}, channel {}, {} ({} bytes)>'
                .format(self.id, self.name, self.channel.id,
                        some_data, len(self.data)))
