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
    comments = db.relationship('Comment', backref='issue', lazy='dynamic')

    def __init__(self, subject, comments):
        """Creates a instance of this class."""

        self.subject = subject
        self.comments = comments

    def __repr__(self):
        return 'id={}, subject={}, comment length={}'.format(
                self.id, self.subject, self.comments.count())

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

