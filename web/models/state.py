"""State class definition."""

from . import get_db

db = get_db()

class State(db.Model):
    """State class.

    Extends Model of 'Flask-SQLAlchemy'.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    value = db.Column(db.Integer, unique=True, nullable=False)

    def __init__(self, name, value):
        """Creates a instance of this class."""

        self.name = name
        self.value = value

    def __repr(self):
        return '{}([])'.format(self.name, self.value)

    @classmethod
    def all(cls):
        """Returns all states. Ordered by 'value'."""

        return cls.query.order_by(cls.value.asc()).all()
