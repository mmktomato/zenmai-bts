""" Routing definition and Flask's entry point.

To run in debug mode: $ FLASK_APP=web/zenmai.py FLASK_DEBUG=1 flask run
"""

from flask import abort, current_app, has_app_context, redirect, render_template, request, send_file, url_for
from . import create_app

if not has_app_context():
    app = create_app()
else:
    current_app.logger.debug('app_context exists.')
    app = current_app

with app.app_context():
    import io
    from web.models.issue import Issue
    from web.models.comment import Comment
    from web.models.state import State
    from web.models.attached_file import AttachedFile
    from web.form_helper import create_new_comment

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
            # TODO: message flash
            # TODO: csrf
            # TODO: try-catch
            new_comment = create_new_comment(request, issue)
            new_comment.add()
            return redirect(url_for('detail', id=id))
        return render_template('detail.html', issue=issue, states=states)

    @current_app.route('/download/<int:attached_file_id>/', methods=['GET'])
    def download(attached_file_id):
        """Download attached file.

        Args:
            attached_file_id (int): attached file id.
        """

        attached_file = AttachedFile.get(attached_file_id)
        if attached_file is None:
            abort(404)

        return send_file(
                io.BytesIO(attached_file.data),
                as_attachment = True,
                attachment_filename=attached_file.name,
                mimetype='application/octet-stream')

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
            # TODO: message flash
            # TODO: csrf
            # TODO: try-catch
            comment = create_new_comment(request, issue)
            issue.comments = [comment]
            issue.add()
            return redirect(url_for('detail', id=issue.id))
        return render_template('new_issue.html', issue=issue, states=states)

