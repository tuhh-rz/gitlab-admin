
# Fix false external accounts

from gitlab import Gitlab, config

from gitlab_admin import getallusers, gettoken


class Ffe:
    def __init__(self, gitlab_instance=None, token_file=None, nono=True):

        self.nono = nono
        self.valid_tuhh_identity = ',ou=people,dc=tu-harburg,dc=de'

        private_token = gettoken(token_file)

        try:
            self.gl = Gitlab(
                gitlab_instance,
                private_token)
        except config.GitlabConfigMissingError as err:
            print(err)

    def main(self):
        if self.nono:
            print('No changes will be made.')

        for user in getallusers(self.gl):
            is_valid_tuhh_identity = False

            if user.external:
                for identity in user.identities:
                    # print(identity['extern_uid'])
                    if identity['extern_uid'].endswith(self.valid_tuhh_identity):
                        is_valid_tuhh_identity = True
                        break

                if is_valid_tuhh_identity:
                    print('{:>5} {} {}'.format(user.id, user.username, user.email))
                    if not self.nono:
                        user.external = False
                        user.projects_limit = 5
                        user.save()
