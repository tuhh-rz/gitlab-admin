import unittest
import gitlab

from . src.gitlab_admin.helpers.user import User

class TestUser(unittest.TestCase):

    def setUp(self):
        self.user = User

    def test_fetch_users(self):
        users = self.user.fetch_users
        self.assertNotEqual(len(users), 0, "No users found!")

if __name__ == "__main__":
    unittest.main()
