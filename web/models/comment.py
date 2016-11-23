from datetime import datetime
from . import get_db

db = get_db()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    pub_date = db.Column(db.DateTime)
    body = db.Column(db.Text)

    def __init__(self, issue, body, pub_date=None):
        self.issue = issue
        self.body = body
        if pub_date is None:
            self.pub_date = datetime.utcnow()
        else:
            self.pub_date = pub_date

    def __repr__(self):
        return 'id={}, issue_id={}, pub_date={}'.format(
                self.id, self.issue_id, self.pub_date)

    def add(self):
        db.session.add(self)
        db.session.commit()
