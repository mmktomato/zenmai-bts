"""Unit test"""

import unittest
import re
from datetime import datetime, timedelta
from . import ctx
from .zenmai_test_utils import create_issue, create_comment, delete_all_issues

class ZenmaiTestCase(unittest.TestCase):
    """TestCase class"""

    def test_issue_list(self):
        """Test case of issue list."""

        issue = create_issue(subject='test subject.test_issue_list.')
        issue.add()
        res = ctx['TEST_APP'].get('/')
        data = res.data.decode('utf-8')
        subject_regex = re.compile(r'<a href="/{}/">.*test subject\.test_issue_list\..*</a>'.format(issue.id))
        self.assertRegex(data, subject_regex)

    def test_no_issue_list(self):
        """Test case of no issues."""

        delete_all_issues()
        res = ctx['TEST_APP'].get('/')
        data = res.data.decode('utf-8')
        self.assertIn('No issues.', data)

    def test_issue_detail(self):
        """Test case of issue detail."""

        pub_date = datetime.utcnow() + timedelta(days=1) # tommorow
        comment = create_comment(body='test body.test_issue_detail.', pub_date=pub_date)
        issue = create_issue(subject='test subject.test_issue_detail.', comments=[comment], state_id=2)
        issue.add()
        res = ctx['TEST_APP'].get('/{}/'.format(issue.id))
        data = res.data.decode('utf-8')
        self.assertIn('<h1>test subject.test_issue_detail.</h1>', data)

        body_regex = re.compile(r'<div class="panel-body">.*<p>test body\.test_issue_detail\.</p>.*</div>', re.DOTALL)
        self.assertRegex(data, body_regex)

        pub_date_regex = re.compile('<div class="panel-heading">.*{}.*</div>'.format(str(pub_date)), re.DOTALL)
        self.assertRegex(data, pub_date_regex)

        state_name_regex = re.compile('<span class="label.*">{}</span>'.format(issue.state.name))
        self.assertRegex(data, state_name_regex)

    def test_no_issue_detail(self):
        """Test case of no issue detail."""

        issue = create_issue()
        issue.add()
        res = ctx['TEST_APP'].get('/{}/'.format(issue.id + 1))
        self.assertEqual(res.status_code, 404)

    def test_new_issue(self):
        """Test case of new issue page."""

        res = ctx['TEST_APP'].get('/new/')
        data = res.data.decode('utf-8')
        self.assertIn('<h1>Add new issue</h1>', data)
