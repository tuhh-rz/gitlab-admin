from datetime import datetime, timedelta

from gitlab import Gitlab, config

from gitlab_admin import getallusers, gettoken


class Dua:
    def __init__(self, gitlab_instance=None, token_file=None, nono=True, timedelta=None):

        self.nono = nono
        self.timedelta = timedelta

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

        deadline = datetime.today() - timedelta(days=self.timedelta)
        # print(deadline)

        for user in getallusers(self.gl):
            if str(user.confirmed_at) == 'None' and user.username != 'ghost':
                # print(user.created_at)
                # print(datetime.strptime(user.created_at, '%Y-%m-%dT%H:%M:%S.%fZ'))
                # print(type(deadline))
                # print(type(user.created_at))

                if deadline > datetime.strptime(user.created_at.split('+')[0], '%Y-%m-%dT%H:%M:%S.%f'):
                    print('{} {:24} {:24} {:>5} {} {}'.format('delete account', str(
                        user.created_at), str(user.confirmed_at), user.id, user.username, user.email))

                    if not self.nono:
                        user.delete()
