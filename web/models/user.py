"""User class definition."""

import bcrypt
from . import get_db

db = get_db()

class User(db.Model):
    """User class.

    Extends Model of 'Flask-SQLAlchemy'.
    """

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    hashed_password = db.Column(db.LargeBinary(64), nullable=False)

    def __init__(self, id, name, password):
        """Creates a instance of this class."""

        self.id = id
        self.name = name
        self.hashed_password = self._create_hashed_password(password)

    def __repr__(self):
        return '{}(id:{})'.format(self.name, self.id)

    @classmethod
    def get(cls, id):
        """Returns a user of specified id.

        Args:
            cls (User): this class.
            id (string): user id.
        """

        return cls.query.get(id)

    def add(self):
        """Inserts this instance to database."""

        db.session.add(self)
        db.session.commit()

    def save(self):
        """Save session."""

        # TODO: not good. fix this.

        db.session.commit()

    def _encode_password(self, password):
        """Encode password string.

        Args:
            self (User): this instance.
            password (string): plain text password.

        Returns:
            UTF-8 encoded password.
        """

        return password.encode('utf-8')

    def _create_hashed_password(self, password):
        """Creates password hash.

        Args:
            self (User): this instance.
            password (string): plain text password.

        Returns:
            Hashed password.
        """

        salt = bcrypt.gensalt(rounds=12)
        bpassword = self._encode_password(password)
        return bcrypt.hashpw(bpassword, salt)

    def authenticate(self, password):
        """Authenticate user.

        Args:
            self (User): this instance.
            password (string): plain text password.

        Returns:
            True if password is matched.
        """

        bpassword = self._encode_password(password)
        return bcrypt.checkpw(bpassword, self.hashed_password)

    def change_password(self, password):
        """Change user password."""

        self.hashed_password = self._create_hashed_password(password)

