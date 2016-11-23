from . import get_db
from .comment import Comment

db = get_db()

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256))
    comments = db.relationship('Comment', backref='issue', lazy='dynamic')

    def __init__(self, subject, comments):
        self.subject = subject
        self.comments = comments

    def __repr__(self):
        return 'id={}, subject={}, comment length={}'.format(
                self.id, self.subject, self.comments.count())

    def all():
        return Issue.query.all()

    def get(id):
        return Issue.query.get(id)

    def add(self):
        db.session.add(self)
        db.session.commit()

