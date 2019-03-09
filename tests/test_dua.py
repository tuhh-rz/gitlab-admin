from gitlab_admin import api
from gitlab_admin.helpers.dua import Dua
from unittest import TestCase

import gitlab

class CommandLineTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        parser = api.create_parser()
        cls.parser = parser


class TestDua(CommandLineTestCase):

    def test_with_empty_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_with_minimum_args(self):
        self.parser.parse_args(['https://collaborating.tuhh.de', 'foobar', 'dua'])

    def test_gitlab_forbidden(self):
        dua = Dua(gitlab_instance='https://collaborating.tuhh.de', private_token='', timedelta=1)
        with self.assertRaises(gitlab.exceptions.GitlabListError):
            dua.main()

    def test_gitlab_unauthorized(self):
        dua = Dua(gitlab_instance='https://collaborating.tuhh.de', private_token='foobar', timedelta=1)
        with self.assertRaises(gitlab.exceptions.GitlabAuthenticationError):
            dua.main()
