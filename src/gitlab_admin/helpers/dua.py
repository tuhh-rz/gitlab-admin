from datetime import datetime, timedelta

import gitlab


class Dua:
    def __init__(self, gitlab_instance=None, private_token=None, nono=True, timedelta=None ):

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
        self.nono = nono
        self.timedelta = timedelta

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

        deadline = datetime.today() - timedelta(days=self.timedelta)
        # print(deadline)

        for user in self.fetch_users():
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
