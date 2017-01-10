"""Utilities of test case class."""

import uuid
from contextlib import contextmanager
from . import ctx
from web.models.issue import Issue
from web.models.comment import Comment
from web.models.attached_file import AttachedFile
from web.models.user import User

def create_issue(subject=None, comments=None, state_id=1):
    """Creates an issue instance."""

    if subject is None:
        subject = str(uuid.uuid4())
    if comments is None:
        comments = [create_comment()]
    return Issue(subject, comments, state_id)

def create_comment(issue=None, user=None, body=None, pub_date=None, attached_files=None):
    """Creates a comment instance."""

    if body is None:
        body = str(uuid.uuid4())
    if user is None:
        user = create_user()
    return Comment(issue, user, body, pub_date, attached_files)

def create_attached_file(comment=None, name=None, data=None):
    """Creates a attached file instance."""

    if name is None:
        name = str(uuid.uuid4()) + '.txt'
    if data is None:
        data = uuid.uuid4().bytes

    return AttachedFile(comment, name, data)

def create_user(id=None, name=None, password=None):
    """Creates an user instance."""

    if id is None:
        id = str(uuid.uuid4())
    if name is None:
        name = str(uuid.uuid4())
    if password is None:
        password = str(uuid.uuid4())

    ret = User(id, name, password)
    ret.add()
    return ret

def delete_all_issues():
    """Deletes all rows of issue table."""

    Issue.query.delete()

@contextmanager
def login(user=None, password=None, do_logout=True):
    """Login as 'user'. if 'user' is None, new user is created."""

    if password is None:
        password = 'test'
    if user is None:
        user = create_user(password=password)

    res = ctx['TEST_APP'].post('/user/login/', data={
        'csrf_token': ctx['CSRF_TOKEN'],
        'user_id': user.id,
        'password': password
    }, follow_redirects=True)

    yield (user, res)

    if do_logout:
        logout()

def logout():
    """Logout."""

    return ctx['TEST_APP'].get('/user/logout/', follow_redirects=True)

