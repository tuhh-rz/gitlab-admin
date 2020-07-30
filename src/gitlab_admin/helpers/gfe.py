import sys

from gitlab import Gitlab, config

from gitlab_admin import getallusers, gettoken


class Gfe:
    def __init__(self, gitlab_instance=None, token_file=None):

        private_token = gettoken(token_file)

        try:
            self.gl = Gitlab(
                gitlab_instance,
                private_token)
        except config.GitlabConfigMissingError as err:
            print(err, file=sys.stderr)

    def main(self):

        for user in getallusers(self.gl):
            if not user.external:
                internal = False
                for identity in user.identities:
                    if identity['provider'] == 'ldapmain':
                        internal = True
                        break

                if not internal:
                    print('{:>5} {} {} {:>5}'.format(user.id, user.username, user.email, len(user.projects.list())))

