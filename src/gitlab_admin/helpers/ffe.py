
# Fix false external accounts

import gitlab


class Ffe:
    def __init__(self, gitlab_instance=None, private_token=None, nono=True):

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
        self.nono = nono

        self.valid_tuhh_identity = ',ou=people,dc=tu-harburg,dc=de'

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

        for user in self.fetch_users():
            is_valid_tuhh_identity = False

            if user.external:
                for identity in user.identities:
                    # print(identity['extern_uid'])
                    if identity['extern_uid'].endswith(self.valid_tuhh_identity):
                        is_valid_tuhh_identity = True
                        break

                if is_valid_tuhh_identity:
                    is_valid_tuhh_identity = False
                    print('{:>5} {} {}'.format(user.id, user.username, user.email))
                    if not self.nono:
                        user.external = False
                        user.projects_limit = 5
                        user.save()