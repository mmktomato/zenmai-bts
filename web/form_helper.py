"""Helper functions for form."""

from werkzeug.utils import secure_filename
from web.models.comment import Comment
from web.models.attached_file import AttachedFile

def create_new_comment(req, issue):
    """Creates a comment instance from flask.request object.

    Args:
        req (flask.request): flask.request object.
        issue (Issue): issue that new comment belongs to.
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

    return Comment(issue, body, attached_files=attached_files)
