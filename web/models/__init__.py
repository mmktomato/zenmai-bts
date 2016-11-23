from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy

def get_db():
    if 'db' not in g:
        current_app.logger.debug('construct SQLAlchemy instance.')
        db = SQLAlchemy(current_app)
        g.db = db
    return g.db
