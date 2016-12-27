"""Attached file class definition."""

from . import get_db

db = get_db()

class AttachedFile(db.Model):
    """Attached file class.

    Extends Model of 'Flask-SQLAlchemy'.
    """

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    name = db.Column(db.String(256))
    data = db.Column(db.LargeBinary)

    def __init__(self, comment_id, name, data):
        """Creates a instance of this class."""

        self.comment_id = comment_id
        self.name = name
        self.data = data

    def __repr__(self):
        return 'id={}, comment_id={}, name = {}, data size={}'.format(
                self.id, self.comment_id, self.name, len(self.data))

    @classmethod
    def get(cls, id):
        """Returns an attached file of specified id.

        Args:
            cls (AttachedFile): this class.
            id (int): attached file id.
        """

        return cls.query.get(id)
