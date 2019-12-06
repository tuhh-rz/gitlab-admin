from datetime import datetime, timedelta

from gitlab import Gitlab, config

import gitlab_admin


class Dua:
    def __init__(self, gitlab_instance=None, token_file=None, nono=True, timedelta=None):

        self.nono = nono
        self.timedelta = timedelta

        private_token = gitlab_admin.gettoken(token_file)

        try:
            self.gl = Gitlab(
                gitlab_instance,
                private_token)
        except config.GitlabConfigMissingError as err:
            print(err)

    def main(self):
        if self.nono:
            print('No changes will be made.')

        deadline = datetime.today() - timedelta(days=self.timedelta)
        # print(deadline)

        for user in gitlab_admin.getallusers(self.gl):
            if not user.confirmed_at and user.username != 'ghost':
                if deadline > datetime.strptime(user.created_at.split('+')[0], '%Y-%m-%dT%H:%M:%S.%f'):
                    print('{} {:24} {:24} {:>5} {} {}'.format('delete account', str(
                        user.created_at), str(user.confirmed_at), user.id, user.username, user.email))

                    if not self.nono:
                        user.delete()
