"""Unit test"""

import unittest
import re
import io
from datetime import datetime, timedelta
from flask import request, session
from . import ctx
from .zenmai_test_utils import create_issue, create_comment, create_attached_file, create_user, \
                                login, logout, delete_all_issues
from web.models.user import User

class ZenmaiTestCase(unittest.TestCase):
    """TestCase class"""

    def _assert_403(self, data):
        """Helper method of 403 assertion."""

        self.assertIn('403', data)
        self.assertIn('Forbidden', data)

    def _assert_issue_detail(self, data, subject, body, pub_date, state_name, attached_file_name):
        """Helper method of issue detail page assertion.

        Args:
            data (string): HTTP Response body.
            subject (string): Regex string of subject.
            body (string): Regex string of body.
            pub_date (string): Regex string of pub_date.
            state_name (string): Regex string of state name.
            attached_file_name (string): Regex string of attached file name.
        """

        # subject
        subject_regex = re.compile('<h1>{}</h1>'.format(subject))
        self.assertRegex(data, subject_regex)

        # body
        body_regex = re.compile(r'<div class="panel-body">.*<p class="zen-comment-body">{}</p>.*</div>'.format(body), re.DOTALL)
        self.assertRegex(data, body_regex)

        # pub_date
        pub_date_regex = re.compile('<div class="panel-heading">.*{}.*</div>'.format(pub_date), re.DOTALL)
        self.assertRegex(data, pub_date_regex)

        # state_name
        state_name_regex = re.compile('<span class="label.*">{}</span>'.format(state_name))
        self.assertRegex(data, state_name_regex)

        # attached_file_name
        attached_file_name_regex = re.compile('<div class="panel-footer">.*download: <a href="/download/\d+/">{}</a>.*</div>'.format(attached_file_name), re.DOTALL)
        self.assertRegex(data, attached_file_name_regex)

    def test_get_issue_list(self):
        """Test case of issue list. (HTTP GET)"""

        issue = create_issue(subject='test subject.test_get_issue_list.')
        issue.add()
        res = ctx['TEST_APP'].get('/')
        data = res.data.decode('utf-8')
        subject_regex = re.compile(r'<a href="/{}/">.*test subject\.test_get_issue_list\..*</a>'.format(issue.id))
        self.assertRegex(data, subject_regex)

    def test_get_empty_issue_list(self):
        """Test case of no issues. (HTTP GET)"""

        delete_all_issues()
        res = ctx['TEST_APP'].get('/')
        data = res.data.decode('utf-8')
        self.assertIn('No issues.', data)

    def test_get_issue_detail(self):
        """Test case of issue detail. (HTTP GET)"""

        pub_date = datetime.utcnow() + timedelta(days=1) # tommorow
        attached_file = create_attached_file(name='test.txt')
        comment = create_comment(body='test body.test_get_issue_detail.', pub_date=pub_date, attached_files=[attached_file])
        issue = create_issue(subject='test subject.test_get_issue_detail.', comments=[comment], state_id=2)
        issue.add()
        res = ctx['TEST_APP'].get('/{}/'.format(issue.id))
        data = res.data.decode('utf-8')

        self._assert_issue_detail(
                data=data,
                subject='test subject\.test_get_issue_detail\.',
                body='test body\.test_get_issue_detail\.',
                pub_date=str(pub_date),
                state_name=issue.state.name,
                attached_file_name='test\.txt')

    def test_post_issue_detail(self):
        """Test case of issue detail. (HTTP POST)"""

        issue = create_issue()
        issue.add()

        # without authentication.
        res = ctx['TEST_APP'].post('/{}/'.format(issue.id), data={
            'csrf_token': ctx['CSRF_TOKEN']
        }, follow_redirects=True)
        self._assert_403(res.data.decode('utf-8'))

        # with authentication.
        with login() as (user, _):
            res = ctx['TEST_APP'].post('/{}/'.format(issue.id), data={
                'csrf_token': ctx['CSRF_TOKEN'],
                'new_body': 'test body.test_post_issue_detail',
                'new_state': 1,
                'file': (io.BytesIO(b'test attached file content.test_post_issue_detail.'), 'test.txt')
            }, follow_redirects=True)
            data = res.data.decode('utf-8')

            self._assert_issue_detail(
                    data=data,
                    subject=issue.subject,
                    body=issue.comments[0].body,
                    pub_date=str(issue.comments[0].pub_date),
                    state_name=issue.state.name,
                    attached_file_name='test\.txt')

    def test_get_no_issue_detail(self):
        """Test case of no issue detail. (HTTP GET)"""

        issue = create_issue()
        issue.add()
        res = ctx['TEST_APP'].get('/{}/'.format(issue.id + 1))
        self.assertEqual(res.status_code, 404)

    def test_get_new_issue(self):
        """Test case of new issue page. (HTTP GET)"""

        res = ctx['TEST_APP'].get('/new/')
        data = res.data.decode('utf-8')
        self.assertIn('<h1>Add new issue</h1>', data)

    def test_post_new_issue(self):
        """Test case of new issue page. (HTTP POST)"""

        # without authentication.
        res = ctx['TEST_APP'].post('/new/', data={
            'csrf_token': ctx['CSRF_TOKEN']
        }, follow_redirects=True)
        self._assert_403(res.data.decode('utf-8'))

        # with authentication.
        with login() as (user, _):
            res = ctx['TEST_APP'].post('/new/', data={
                'csrf_token': ctx['CSRF_TOKEN'],
                'new_subject': 'test subject.test_post_new_issue.',
                'new_body': 'test body.test_post_new_issue.',
                'new_state': 1,
                'file': (io.BytesIO(b'test attached file content.test_post_new_issue.'), 'test.txt')
            }, follow_redirects=True)
            data = res.data.decode('utf-8')

            self._assert_issue_detail(
                    data=data,
                    subject='test subject\.test_post_new_issue\.',
                    body='test body\.test_post_new_issue\.',
                    pub_date='.*', # no assert. TODO: fix
                    state_name='Open',
                    attached_file_name='test\.txt')

    def test_post_large_attached_file(self):
        """Test case of post request with too large attached file."""

        large_buf = bytes(ctx['APP'].config['MAX_CONTENT_LENGTH'] + 1)
        res = ctx['TEST_APP'].post('/new/', data={
            'new_subject': 'test subject.test_post_new_issue.',
            'new_body': 'test body.test_post_new_issue.',
            'new_state': 1,
            'file': (io.BytesIO(large_buf), 'test.txt')
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 413)

    def test_get_download_attached_file(self):
        """Test case of downloading attached file. (HTTP GET)"""

        attached_file = create_attached_file(data=b'test content of attached file.test_get_download_attached_file.')
        comment = create_comment(attached_files=[attached_file])
        issue = create_issue(comments=[comment])
        issue.add()
        res = ctx['TEST_APP'].get('/download/{}/'.format(attached_file.id))
        data = res.data.decode('utf-8')
        self.assertEqual(data, 'test content of attached file.test_get_download_attached_file.')

    def test_get_login_page(self):
        """Test case of login page. (HTTP GET)"""

        res = ctx['TEST_APP'].get('/user/login/')
        data = res.data.decode('utf-8')
        self.assertIn('<title>Zenmai - login</title>', data)
        self.assertEqual(res.status_code, 200)

    def test_post_login_page(self):
        """Test case of login. (HTTP POST)"""

        user = create_user( \
                id='testid.test_post_login_page', \
                name='testname.test_post_login_page', \
                password='testpassword.test_post_login_page')

        with login(user, 'testpassword.test_post_login_page') as (_, res):
            data = res.data.decode('utf-8')

            self.assertEqual(res.status_code, 200)
            self.assertIn('<li>{}(id:{})</li>'.format(user.name, user.id), data)

    def test_get_logout_page(self):
        """Test case of logout. (HTTP GET)"""

        user = create_user( \
                id='testid.test_get_logout_page', \
                name='testname.test_post_logout_page', \
                password='testpassword.test_post_logout_page')

        with login(user, 'testpassword.test_post_logout_page', do_logout=False):
            pass
        res = logout()

        data = res.data.decode('utf-8')
        self.assertEqual(res.status_code, 200)
        self.assertIn('<title>Zenmai - issues</title>', data)

    def test_get_user_register_page(self):
        """Test case of user register page. (HTTP GET)"""

        res = ctx['TEST_APP'].get('/user/new/')
        data = res.data.decode('utf-8')
        self.assertIn('<title>Zenmai - register</title>', data)
        self.assertEqual(res.status_code, 200)

    def test_post_register_valid_user(self):
        """Test case of valid user registration. (HTTP POST)"""

        res = ctx['TEST_APP'].post('/user/new/', data={
            'csrf_token': ctx['CSRF_TOKEN'],
            'user_id': 'testid.test_post_register_valid_user',
            'user_name': 'testname.test_post_register_valid_user',
            'password': 'testpassword.test_post_register_valid_user',
            'password_retype': 'testpassword.test_post_register_valid_user'
        }, follow_redirects=True)
        data = res.data.decode('utf-8')
        self.assertIn('<title>Zenmai - login</title>', data)
        self.assertEqual(res.status_code, 200)

    def test_post_register_invalid_user(self):
        """Test case of invalid user registration. (HTTP POST)"""

        # password is not matched.
        res = ctx['TEST_APP'].post('/user/new/', data={
            'csrf_token': ctx['CSRF_TOKEN'],
            'user_id': 'testid.test_post_register_invalid_user',
            'user_name': 'testname.test_post_register_invalid_user',
            'password': 'testpassword.test_post_register_invalid_user',
            'password_retype': 'invalid password'
        }, follow_redirects=True)
        data = res.data.decode('utf-8')
        self.assertIn('<title>Zenmai - register</title>', data)
        self.assertEqual(res.status_code, 200)

        # already exist.
        ctx['TEST_APP'].post('/user/new/', data={
            'csrf_token': ctx['CSRF_TOKEN'],
            'user_id': 'testid.test_post_register_invalid_user',
            'user_name': 'testname.test_post_register_invalid_user',
            'password': 'testpassword.test_post_register_invalid_user',
            'password_retype': 'testpassword.test_post_register_invalid_user'
        }, follow_redirects=True)
        res = ctx['TEST_APP'].post('/user/new/', data={
            'csrf_token': ctx['CSRF_TOKEN'],
            'user_id': 'testid.test_post_register_invalid_user',
            'user_name': 'testname.test_post_register_invalid_user',
            'password': 'testpassword.test_post_register_invalid_user',
            'password_retype': 'testpassword.test_post_register_invalid_user'
        }, follow_redirects=True)
        data = res.data.decode('utf-8')
        self.assertIn('<title>Zenmai - register</title>', data)
        self.assertEqual(res.status_code, 200)

