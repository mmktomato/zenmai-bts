import sys

if len(sys.argv) < 2:
    print("Usage: python dbutil.py ACTION (supported action: 'create')") # TODO: support migrate
    exit()

from web import create_app
from web.models import get_db

app = create_app()
action = sys.argv[1]

with app.app_context():
    import web.models.issue
    import web.models.comment
    db = get_db()

    if action == 'create':
        db.create_all()
    else:
        print("Unknown action '{}'".format(action))

