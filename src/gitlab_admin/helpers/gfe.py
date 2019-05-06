import gitlab
from datetime import datetime, timedelta


class Gfe:
    def __init__(self, gitlab_instance=None, private_token=None):

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
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

        for user in self.fetch_users():
            if not user.external:
                internal = False
                for identity in user.identities:
                    if identity['provider'] == 'ldapmain':
                        internal = True
                        break

                if not internal:
                    print('{:>5} {} {} {:>5}'.format(user.id, user.username, user.email, len(user.projects.list())))

