"""Run unit test.

To run unit test: $ python runtest.py
"""

import os
import unittest
import tempfile
from flask import g
from web import create_app
from dbutil import init_db
from test import ctx

db_fd = None
db_path = None

def init(app):
    """Initialize Unit test."""

    app.config['TESTING'] = True

    # create database.
    global db_fd
    global db_path
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.logger.debug('database = ' + app.config['SQLALCHEMY_DATABASE_URI'])
    init_db()

    # define routing.
    import web.zenmai

    ctx['TEST_APP'] = app.test_client()
    ctx['APP'] = app

def finalize(app):
    """Finalize unit test."""

    os.close(db_fd)
    os.unlink(db_path)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            from test.test_zenmai import ZenmaiTestCase
            init(app)
            suite = unittest.TestSuite()
            suite.addTests([ZenmaiTestCase()])
            unittest.main()
        finally:
            finalize(app)
