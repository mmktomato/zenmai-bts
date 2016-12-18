"""Comment class definition."""

from datetime import datetime
from . import get_db
from .attached_file import AttachedFile

db = get_db()

class Comment(db.Model):
    """Comment class.

    Extends Model of 'Flask-SQLAlchemy'.
    """

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    pub_date = db.Column(db.DateTime)
    body = db.Column(db.Text)

    attached_files = db.relationship('AttachedFile', lazy='dynamic')

    def __init__(self, issue, body, pub_date=None, attached_files=None):
        """Creates a instance of this class."""

        self.issue = issue
        self.body = body
        if pub_date is None:
            self.pub_date = datetime.utcnow()
        else:
            self.pub_date = pub_date
        if attached_files is not None:
            self.attached_files = attached_files

    def __repr__(self):
        return 'id={}, issue_id={}, pub_date={}, attached_files length={}'.format(
                self.id, self.issue_id, self.pub_date, self.attached_files.count())

    def add(self):
        """Inserts this instance to database."""

        db.session.add(self)
        db.session.commit()
