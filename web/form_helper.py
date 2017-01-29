"""Helper functions for form."""

from werkzeug.utils import secure_filename
from flask import session
from web import AUTH_USER_ID_KEY
from web.models.comment import Comment
from web.models.attached_file import AttachedFile
from web.models.user import User

def _get_user_information(req):
    """Get user information from form.

    Args:
        req (flask.request): flask.request object.

    Returns:
        dictionary.
    """

    # TODO: validate

    return {'user_id': req.form['user_id'],
            'user_name': req.form['user_name'],
            'password': req.form['password'],
            'password_retype': req.form['password_retype']}

def create_new_comment(req, issue, user):
    """Creates a comment instance from flask.request object.

    Args:
        req (flask.request): flask.request object.
        issue (Issue): issue that new comment belongs to.
        user (User): user who is authenticated.
    """

    # TODO: validate

    if 'new_subject' in req.form:
        issue.subject = req.form['new_subject']
    if 'new_state' in req.form:
        issue.state_id = req.form['new_state']
    if 'new_body' in req.form:
        body = req.form['new_body']
    else:
        body = None

    attached_files = [
            AttachedFile(None, secure_filename(v.filename), v.read())
            for k, v in req.files.items()
            if v.filename]
    if len(attached_files) < 1:
        attached_files = None

    return Comment(issue, user, body, attached_files=attached_files)

def do_login(req):
    """Do login.
    Authentication state is stored to session.

    Args:
        req (flask.request): flask.request object.

    Returns:
        True if authenticated.
    """

    # TODO: validate

    user_id = req.form['user_id']
    password = req.form['password']

    user = User.get(user_id)
    if user is None:
        return False

    authenticated = user.authenticate(password)

    if authenticated:
        session[AUTH_USER_ID_KEY] = user_id

    return authenticated

def create_new_user(req):
    """Create new user.

    Args:
        req (flask.request): flask.request object.

    Returns:
        A tuple (User, message). 'User' is None if
        form data is invalid.
    """

    user_info = _get_user_information(req)

    if user_info['password'] != user_info['password_retype']:
        return (None, 'password is not matched.')

    if User.get(user_info['user_id']) is not None:
        return (None, "id '{}' is already exists.".format(user_info['user_id']))

    return (User(user_info['user_id'], user_info['user_name'], user_info['password']), None)

def edit_user_information(req, user):
    """edit user information.

    Args:
        req (flask.request): flask.request object.
        user (User): authenticated user.

    Returns:
        A tuple (User, message). 'User' is None if
        form data is invalid.
    """

    user_info = _get_user_information(req)

    if user_info['password'] != user_info['password_retype']:
        return (None, 'password is not matched.')

    # name
    user.name = user_info['user_name']

    # password
    if user_info['password']:
        user.change_password(user_info['password'])

    return (user, None)

