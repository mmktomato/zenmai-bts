"""Utilities of test case class."""

import uuid
from web.models.issue import Issue
from web.models.comment import Comment

def create_issue(subject=None, comments=None, state_id=1):
    """Creates an issue instance."""

    if subject is None:
        subject = str(uuid.uuid4())
    if comments is None:
        comments = [create_comment()]
    return Issue(subject, comments, state_id)

def create_comment(issue=None, body=None, pub_date=None):
    """Creates a comment instance."""

    if body is None:
        body = str(uuid.uuid4())
    return Comment(issue, body, pub_date)

def delete_all_issues():
    """Deletes all rows of issue table."""

    Issue.query.delete()
