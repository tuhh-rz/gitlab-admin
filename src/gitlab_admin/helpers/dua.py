import argparse
import gitlab
from datetime import datetime, timedelta


class Dua:
    def __init__(self, args):

        self.gitlab_instance = args.gitlab_instance
        self.private_token = args.private_token
        self.nono = args.nono

        try:
            self.gl = gitlab.Gitlab(
                self.gitlab_instance,
                private_token=self.private_token)
        except gitlab.config.GitlabConfigMissingError as err:
            print(err)

    def fetch_users(self):
        users = self.gl.users.list(as_list=False)
        return users

    def fetch_user(self, id):
        try:
            user = self.gl.users.get(id)
            return user
        except gitlab.exceptions.GitlabGetError as err:
            print(err)

    def main(self):
        if self.nono:
            print('No changes will be made.')

        deadline = datetime.today() - timedelta(days=7)

        for user in self.fetch_users():
            if str(user.confirmed_at) == 'None' and user.username != 'ghost':
                    print('{:24} {:24} {:>5} {} {}'.format(str(
                        user.created_at), str(user.confirmed_at), user.id, user.username, user.email))
