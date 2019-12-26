from datetime import datetime, timedelta

from gitlab import Gitlab, config

import gitlab_admin


class Dba:
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
            if str(user.state) == 'blocked' and user.external and user.username != 'ghost':
                if not user.email.split('@')[1] in gitlab_admin.trusted_domains:
                    if user.last_activity_on and deadline > datetime.strptime(
                            user.last_activity_on, '%Y-%m-%d'):
                        print('{} {:24} {:24} {:>5} {} {}'.format('delete blocked account', str(
                            user.last_activity_on), str(user.state), user.id, user.username, user.email))

                        if not self.nono:
                            user.delete()
