"""Issue class definition."""

from . import get_db
from .comment import Comment

db = get_db()

class Issue(db.Model):
    """Issue class.

    Extends Model of 'Flask-SQLAlchemy'.
    """

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)

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

    @classmethod
    def all(cls):
        """Returns all issues."""

        return cls.query.all()

    @classmethod
    def get(cls, id):
        """Returns an issue of specified id.

        Args:
            cls (Issue): this class.
            id (int): issue id.
        """

        return cls.query.get(id)

    def add(self):
        """Inserts this instance to database."""

        db.session.add(self)
        db.session.commit()
