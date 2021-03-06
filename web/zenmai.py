""" Routing definition and Flask's entry point.

To run in debug mode: $ FLASK_APP=web/zenmai.py FLASK_DEBUG=1 flask run
"""

from flask import abort, current_app, flash, has_app_context, \
                  redirect, render_template, request, \
                  session, send_file, url_for
from . import create_app, create_csrf_token, validate_csrf_token, \
              CSRF_TOKEN_KEY, AUTH_USER_ID_KEY, NOT_AUTHENTICATED_MESSAGE

if not has_app_context():
    app = create_app()
else:
    current_app.logger.debug('app_context exists.')
    app = current_app

with app.app_context():
    import io
    from urllib.parse import urlparse, urljoin, quote
    from web.models.issue import Issue
    from web.models.comment import Comment
    from web.models.state import State
    from web.models.attached_file import AttachedFile
    from web.models.user import User
    from web.exceptions.zen_http_exception import ZenHttpException
    from web.form_helper import create_new_comment, create_new_user, do_login, \
                                edit_user_information

    def is_authenticated():
        """Return true if user is authenticated."""

        return AUTH_USER_ID_KEY in session

    def get_login_user():
        """Get authenticated user. Raise an exception
        if user is not authenticated or does not exist.

        Returns:
            An instance of User class.
        """

        if not is_authenticated():
            raise ZenHttpException(403) # Forbidden

        ret = User.get(session[AUTH_USER_ID_KEY])
        if ret is None:
            raise ZenHttpException(404) # Not Found

        return ret

    def is_safe_url(target):
        """Returns True if 'target' is safe url.
        http://flask.pocoo.org/snippets/62/
        """

        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in ('http', 'https') and \
               ref_url.netloc == test_url.netloc

    def get_redirect_destination(req):
        """Returns redirect destination from query parameter.
        If 'next' is not in query parameter or redirect url is
        not safe, return None.

        Args:
            req (flask.request): flask.request object.
        """

        if 'next' not in request.args:
            return None

        next = request.args['next']
        if not is_safe_url(next):
            return None

        return next

    app.jinja_env.globals['csrf_token_key'] = CSRF_TOKEN_KEY
    app.jinja_env.globals['create_csrf_token'] = create_csrf_token
    app.jinja_env.globals['get_login_user'] = get_login_user
    app.jinja_env.globals['quote_url'] = lambda url: quote(url, safe='')

    def _handle_exception(err):
        t = type(err)

        # TODO: write log

        if t is ZenHttpException:
            abort(err.status)
        else:
            abort(500)

    @app.before_request
    def before_request():
        if request.method == "POST":
            if not validate_csrf_token(request):
                abort(403)

    # GET /
    @app.route('/')
    def index():
        """Rendering top page.

        Renders all issues.
        """

        try:
            return render_template('issues.html', issues=Issue.all())
        except Exception as err:
            _handle_exception(err)

    # GET /1
    # POST /1
    @app.route('/<int:id>/', methods=['GET', 'POST'])
    def detail(id):
        """Rendering detail page.

        Renders a detail of issue.
        Accepts a post request to add a new comment.

        Args:
            id (int): issue id.
        """

        try:
            issue = Issue.get(id)
            states = State.all()
            if issue is None:
                raise ZenHttpException(404)
            if request.method == 'POST':
                # TODO: message flash
                new_comment = create_new_comment(request, issue, get_login_user())
                new_comment.add()
                return redirect(url_for('detail', id=id))
            return render_template('detail.html', issue=issue, states=states)
        except Exception as err:
            _handle_exception(err)

    # GET /download/1
    @app.route('/download/<int:attached_file_id>/', methods=['GET'])
    def download(attached_file_id):
        """Download attached file.

        Args:
            attached_file_id (int): attached file id.
        """

        try:
            attached_file = AttachedFile.get(attached_file_id)
            if attached_file is None:
                raise ZenHttpException(404)

            return send_file(
                    io.BytesIO(attached_file.data),
                    as_attachment = True,
                    attachment_filename=attached_file.name,
                    mimetype='application/octet-stream')
        except Exception as err:
            _handle_exception(err)

    # GET /new
    # POST /new
    @app.route('/new/', methods=['GET', 'POST'])
    def new_issue():
        """Rendering new issue page.

        Renders a empty issue.
        Accepts a post request to add a new issue.
        """

        try:
            issue = Issue(None, [], None)
            states = State.all()
            if request.method == 'POST':
                # TODO: message flash
                comment = create_new_comment(request, issue, get_login_user())
                issue.comments = [comment]
                issue.add()
                return redirect(url_for('detail', id=issue.id))

            if not is_authenticated():
                flash(NOT_AUTHENTICATED_MESSAGE, 'info')
                return redirect(url_for('login', next=request.url))
            return render_template('new_issue.html', issue=issue, states=states)
        except Exception as err:
            _handle_exception(err)

    # GET /user
    @app.route('/user/', methods=['GET'])
    def user():
        """Rendering user page."""

        try:
            if not is_authenticated():
                return redirect(url_for('login', next=request.url))
            return render_template('user.html')
        except Exception as err:
            _handle_exception(err)


    # GET /user/login
    # POST /user/login
    @app.route('/user/login/', methods=['GET', 'POST'])
    def login():
        """Rendering login page."""

        try:
            dest = get_redirect_destination(request)
            if not dest:
                dest = '/'

            if request.method == 'POST':
                if not do_login(request):
                    flash('id or password is incorrect.', 'warning')
                    return redirect(url_for('login', next=dest))
                else:
                    return redirect(dest)
            return render_template('login.html', next=dest)
        except Exception as err:
            _handle_exception(err)

    # GET /user/logout
    @app.route('/user/logout/', methods=['GET'])
    def logout():
        """Do logout."""

        try:
            session.pop(AUTH_USER_ID_KEY) # delete
            return redirect(url_for('index'))
        except Exception as err:
            _handle_exception(err)

    # GET /user/new
    # POST /user/new
    @app.route('/user/new/', methods=['GET', 'POST'])
    def new_user():
        """Renderring new user page."""

        try:
            if request.method == 'POST':
                (new_user, message) = create_new_user(request)
                if new_user is None:
                    flash(message, 'warning')
                    redirect(url_for('new_user'))
                else:
                    new_user.add()
                    flash("user '{}' is registered.".format(new_user), 'success')
                    return redirect(url_for('login'))
            return render_template('edit_user.html')
        except Exception as err:
            _handle_exception(err)

    # GET /user/edit
    # POST /user/edit
    @app.route('/user/edit/', methods=['GET', 'POST'])
    def edit_user():
        """Rendering edit user page."""

        try:
            user = get_login_user()
            if request.method == 'POST':
                (user, message) = edit_user_information(request, user)
                if user is None:
                    flash(message, 'warning')
                    return redirect(url_for('edit_user'))

                user.save()
                return redirect(url_for('user'))

            if not is_authenticated():
                flash(NOT_AUTHENTICATED_MESSAGE, 'info')
                return redirect(url_for('login', next=request.url))

            return render_template('edit_user.html', user=user)
        except Exception as err:
            _handle_exception(err)

