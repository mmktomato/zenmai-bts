"""Initializing 'models' module."""

from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy

def get_db():
    """Creates a 'SQLAlchemy' instance.

    Creates a 'SQLAlchemy' instance and store it to 'flask.g.db'.
    Before this function is called, Flask's application context must be exist.

    Returns:
        a 'SQLAlchemy' instance.
    """

    if 'db' not in g:
        current_app.logger.debug('construct SQLAlchemy instance.')
        db = SQLAlchemy(current_app)
        g.db = db
    return g.db
