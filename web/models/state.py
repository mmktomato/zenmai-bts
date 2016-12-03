"""State class definition."""

from . import get_db

db = get_db()

class State(db.Model):
    """State class.

    Extends Model of 'Flask-SQLAlchemy'.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    value = db.Column(db.Integer, unique=True)

    def __init__(self, name, value):
        """Creates a instance of this class."""

        self.name = name
        self.value = value

    def __repr(self):
        return '{}([])'.format(self.name, self.value)

    def all():
        """Returns all states. Ordered by 'value'."""

        return State.query.order_by(State.value.asc()).all()
