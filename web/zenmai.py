# To run in debug mode: $ FLASK_APP=web/zenmai.py FLASK_DEBUG=1 flask run

from flask import abort, current_app, redirect, render_template, request, url_for
from . import create_app

app = create_app()

with app.app_context():
    from web.models.issue import Issue
    from web.models.comment import Comment

    # GET /
    @current_app.route('/')
    def index():
        return render_template('issues.html', issues=Issue.all())

    # GET /1
    # POST /1
    @current_app.route('/<int:id>/', methods=['GET', 'POST'])
    def detail(id):
        issue = Issue.get(id)
        if issue is None:
            abort(404)
        if request.method == 'POST':
            # TODO: validate
            # TODO: message flash
            # TODO: csrf
            # TODO: try-catch
            new_body = request.form['new_body']
            new_comment = Comment(issue, new_body)
            new_comment.add()
        return render_template('detail.html', issue=issue)

    @current_app.route('/new/', methods=['GET', 'POST'])
    def new_issue():
        if request.method == 'POST':
            # TODO: validate
            # TODO: message flash
            # TODO: csrf
            # TODO: try-catch
            new_subject = request.form['new_subject']
            new_body = request.form['new_body']
            new_comment = Comment(None, new_body)
            new_issue = Issue(new_subject, [new_comment])
            new_issue.add()
            return redirect(url_for('detail', id=new_issue.id))
        return render_template('new_issue.html')

