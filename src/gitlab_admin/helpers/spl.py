from gitlab import Gitlab, config

from gitlab_admin import getallusers, gettoken


class Spl:
    def __init__(self, gitlab_instance=None, token_file=None, nono=True, limit=None):

        self.nono = nono
        self.limit = limit

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
            if user.username != 'ghost':
                if not user.external and self.limit > user.projects_limit:
                    # print (user.external)
                    # print (user.projects_limit)
                    print('{} {:>5} {} {}'.format('set project limit to ' + str(self.limit) +
                                                  ' (currently ' + str(user.projects_limit) + ')', user.id,
                                                  user.username, user.email))

                    if not self.nono:
                        user.projects_limit = self.limit
                        user.save()
