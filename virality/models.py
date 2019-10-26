from hmac import new as hmac_new
from os import urandom
from base64 import b64encode

from flask_login import UserMixin, current_user
from sqlalchemy.exc import IntegrityError

from . import app, db
from .exceptions import IntegrityErrorException

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(64))
    description = db.Column(db.Text(), default='')
    invites = db.relationship('Invite', backref='user', lazy='dynamic')
    images = db.relationship('Image', backref='user', lazy=True)

    @staticmethod
    def _password_hash(raw_password):
        # yup, I know about pbkdf2 and why it is usefull
        return hmac_new(app.config.get('PASSWORD_SECRET'), str.encode(raw_password), digestmod='sha256').hexdigest()

    def __init__(self, raw_password, **kwargs):
        super().__init__(**kwargs)
        self.password = self._password_hash(raw_password)

    def __repr__(self):
        return self.email

    def register(self, invite):
        db.session.add(self)
        if invite:
            invite.redeemed = True

        try:
            db.session.commit()

        except IntegrityError:
            raise IntegrityErrorException

    def valid_password(self, raw_password):
        return self.password == self._password_hash(raw_password)


class Invite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    redeemed = db.Column(db.Boolean, default=False, index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = current_user
        self.code = b64encode(urandom(6), b'-_').decode('ascii')

    @staticmethod
    def get_token(code):
        hmac_digest = hmac_new(app.config.get('CONFIRMATION_SECRET'), str.encode(code), digestmod='sha1').digest()
        return b64encode(hmac_digest, b'-_').decode('ascii')[:12]

    @property
    def token(self):
        return self.get_token(self.code)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name = db.Column(db.String(100))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = current_user