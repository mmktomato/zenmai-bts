"""Comment class definition."""

from datetime import datetime
from . import get_db
from .attached_file import AttachedFile
from .user import User

db = get_db()

class Comment(db.Model):
    """Comment class.

    Extends Model of 'Flask-SQLAlchemy'.
    """

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)
    body = db.Column(db.Text)

    attached_files = db.relationship('AttachedFile', lazy='dynamic')
    user = db.relationship('User', uselist=False, foreign_keys=[user_id])

    def __init__(self, issue, user, body, pub_date=None, attached_files=None):
        """Creates a instance of this class."""

        self.issue = issue
        self.user = user
        self.body = body
        if pub_date is None:
            self.pub_date = datetime.utcnow()
        else:
            self.pub_date = pub_date
        if attached_files is not None:
            self.attached_files = attached_files

    def __repr__(self):
        return 'id={}, issue_id={}, user_id={}, pub_date={}, attached_files length={}'.format(
                self.id, self.issue_id, self.user.id, self.pub_date, self.attached_files.count())

    def add(self):
        """Inserts this instance to database."""

        db.session.add(self)
        db.session.commit()
