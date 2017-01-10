"""Initializing 'web' module."""

import uuid
from os.path import join
from flask import Flask, session

CSRF_TOKEN_KEY = 'csrf_token'
csrf_token_for_testing = ''

AUTH_USER_ID_KEY = 'authenticated_user_id'

def create_app():
    """Creates Flask application.

    Loads 'zenmai.config.py'

    Returns:
        Flask application.
    """

    app = Flask(__name__)
    app.logger.debug('__name__ = {name}\nroot_path = {root_path}'.format(
        name=__name__, root_path=app.root_path))
    app.config.from_pyfile(join(app.root_path, 'zenmai.config.py'))
    app.config['version'] = '0.0.1'
    return app

def create_csrf_token():
    """Creates CSRF token and store it to session.

    Returns:
        CSRF token.
    """

    if CSRF_TOKEN_KEY not in session:
        if csrf_token_for_testing:
            session[CSRF_TOKEN_KEY] = csrf_token_for_testing
        else:
            session[CSRF_TOKEN_KEY] = str(uuid.uuid4())
    return session[CSRF_TOKEN_KEY]

def validate_csrf_token(req):
    """Validates CSRF token.

    Args:
        req (flask.request): flask.request object.

    Returns:
        True if valid token.
    """

    if CSRF_TOKEN_KEY not in req.form or CSRF_TOKEN_KEY not in session:
        return False
    if req.form[CSRF_TOKEN_KEY] != session[CSRF_TOKEN_KEY]:
        return False
    return True

