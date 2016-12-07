""" Routing definition and Flask's entry point.

To run in debug mode: $ FLASK_APP=web/zenmai.py FLASK_DEBUG=1 flask run
"""

from flask import abort, current_app, has_app_context, redirect, render_template, request, url_for
from . import create_app

if not has_app_context():
    app = create_app()
else:
    current_app.logger.debug('app_context exists.')
    app = current_app

with app.app_context():
    from web.models.issue import Issue
    from web.models.comment import Comment
    from web.models.state import State

    # GET /
    @current_app.route('/')
    def index():
        """Rendering top page.

        Renders all issues.
        """

        return render_template('issues.html', issues=Issue.all())

    # GET /1
    # POST /1
    @current_app.route('/<int:id>/', methods=['GET', 'POST'])
    def detail(id):
        """Rendering detail page.

        Renders a detail of issue.
        Accepts a post request to add a new comment.

        Args:
            id (int): issue id.
        """

        issue = Issue.get(id)
        states = State.all()
        if issue is None:
            abort(404)
        if request.method == 'POST':
            # TODO: validate
            # TODO: message flash
            # TODO: csrf
            # TODO: try-catch
            new_body = request.form['new_body']
            new_comment = Comment(issue, new_body)
            #new_comment.add()
            issue.state_id = request.form['new_state']
            issue.add()
        return render_template('detail.html', issue=issue, states=states)

    # GET /new
    # POST /new
    @current_app.route('/new/', methods=['GET', 'POST'])
    def new_issue():
        """Rendering new issue page.

        Renders a empty issue.
        Accepts a post request to add a new issue.
        """
        issue = Issue(None, [], None)
        states = State.all()
        if request.method == 'POST':
            # TODO: validate
            # TODO: message flash
            # TODO: csrf
            # TODO: try-catch
            issue.subject = request.form['new_subject']
            issue.state_id = request.form['new_state']
            issue.body = request.form['new_body']
            issue.comments = [Comment(issue, issue.body)]
            issue.add()
            return redirect(url_for('detail', id=issue.id))
        return render_template('new_issue.html', issue=issue, states=states)

