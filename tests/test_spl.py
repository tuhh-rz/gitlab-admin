from gitlab_admin import api
from gitlab_admin.helpers.spl import Spl
from unittest import TestCase

import gitlab

class CommandLineTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        parser = api.create_parser()
        cls.parser = parser


class TestSpl(CommandLineTestCase):

    def test_with_empty_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_with_minimum_args(self):
        self.parser.parse_args(['https://collaborating.tuhh.de', 'foobar', 'spl', '--limit', '1'])

    def test_gitlab_forbidden(self):
        spl = Spl(gitlab_instance='https://collaborating.tuhh.de', limit=1)
        with self.assertRaises(gitlab.exceptions.GitlabListError):
            spl.main()

    def test_gitlab_unauthorized(self):
        spl = Spl(gitlab_instance='https://collaborating.tuhh.de', private_token='foobar', limit=1)
        with self.assertRaises(gitlab.exceptions.GitlabAuthenticationError):
            spl.main()
