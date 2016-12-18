import sys
from web import create_app
from web.models import get_db

def init_db():
    """Initialize Database."""

    import web.models.issue
    import web.models.comment
    from web.models.state import State
    import web.models.attached_file

    db = get_db()
    db.create_all()
    db.session.add(State('Open', 1))
    db.session.add(State('Closed', 99))
    db.session.commit()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python dbutil.py ACTION (supported action: 'create')") # TODO: support migrate
        exit()

    app = create_app()
    action = sys.argv[1]

    with app.app_context():
        if action == 'create':
            init_db()
        else:
            print("Unknown action '{}'".format(action))

