from os.path import join
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.logger.debug('__name__ = {name}\nroot_path = {root_path}'.format(
        name=__name__, root_path=app.root_path))
    app.config.from_pyfile(join(app.root_path, 'zenmai.config.py'))
    return app
