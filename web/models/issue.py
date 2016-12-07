"""Issue class definition."""

from . import get_db
from .comment import Comment

db = get_db()

class Issue(db.Model):
    """Issue class.

    Extends Model of 'Flask-SQLAlchemy'.
    """

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256))
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))

    comments = db.relationship('Comment', backref='issue', lazy='dynamic')
    state = db.relationship('State', uselist=False, foreign_keys=[state_id])

    def __init__(self, subject, comments, state_id):
        """Creates a instance of this class."""

        self.subject = subject
        self.comments = comments
        self.state_id = state_id

    def __repr__(self):
        return 'id={}, subject={}, state_id={}, comment length={}'.format(
                self.id, self.subject, self.state_id, self.comments.count())

    def all():
        """Returns all issues."""

        return Issue.query.all()

    def get(id):
        """Returns an issue of specified id.

        Args:
            id (int): issue id.
        """

        return Issue.query.get(id)

    def add(self):
        """Inserts this instance to database."""

        db.session.add(self)
        db.session.commit()
