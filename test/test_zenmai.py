"""Unit test"""

import unittest
import re
import io
from datetime import datetime, timedelta
from . import ctx
from .zenmai_test_utils import create_issue, create_comment, create_attached_file, delete_all_issues

class ZenmaiTestCase(unittest.TestCase):
    """TestCase class"""

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
        res = ctx['TEST_APP'].post('/{}/'.format(issue.id), data={
            'new_body': 'test body.test_post_issue_detail',
            'new_state': 1,
            'file': (io.BytesIO(b'test attached file content.test_post_issue_detail.'), 'test.txt')
        })
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

        res = ctx['TEST_APP'].post('/new/', data={
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

    def test_get_download_attached_file(self):
        """Test case of downloading attached file. (HTTP GET)"""

        attached_file = create_attached_file(data=b'test content of attached file.test_get_download_attached_file.')
        comment = create_comment(attached_files=[attached_file])
        issue = create_issue(comments=[comment])
        issue.add()
        res = ctx['TEST_APP'].get('/download/{}/'.format(attached_file.id))
        data = res.data.decode('utf-8')
        self.assertEqual(data, 'test content of attached file.test_get_download_attached_file.')


