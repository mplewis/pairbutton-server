from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    key = db.Column(db.Text)
    files = db.relationship('File', backref='channel')

    def __init__(self, name, key):
        self.name = name
        self.key = key

    def __repr__(self):
        return '<Channel: {}, {}>'.format(self.id, self.name)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    data = db.Column(db.Text)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'),
                           nullable=False)

    def __init__(self, name, data, channel_id):
        self.name = name
        self.data = data
        self.channel_id = channel_id

    def __repr__(self):
        return ('<File: {}, {}, channel {}, {} ({} bytes)>'
                .format(self.id, self.name, self.channel.id,
                        self.data, len(self.data)))
