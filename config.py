# sensitive data must be hidden from the source files
# I keeped it here just as this is quite basic solution

import os

SERVER_NAME = '127.0.0.1:5000'

DEBUG = True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

SECRET_KEY = 'ehae#d*ieMoh7yeiX&a?ekeneMie)Zoh8oopeuph=ai}d=ei5C'

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/db.sqlite3'.format(BASE_DIR)
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = False

PASSWORD_SECRET = b'ohth5jai)Gh?avaiEeb[ea+k1ugeeh^o'
CONFIRMATION_SECRET = b'to(K6goo+x7oe5ow'

IMAGES_HOST = 'http://127.0.0.1:8080'
