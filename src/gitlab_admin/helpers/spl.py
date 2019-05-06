import gitlab


class Spl:
    def __init__(self, gitlab_instance=None, private_token=None, nono=True, limit=None):

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
        self.nono = nono
        self.limit = limit

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
            if user.username != 'ghost':
                if not user.external and self.limit > user.projects_limit:
                    # print (user.external)
                    # print (user.projects_limit)
                    print('{} {:>5} {} {}'.format('set project limit to ' + str(self.limit) +
                                                  ' (currently ' + str(user.projects_limit) + ')', user.id, user.username, user.email))

                    if not self.nono:
                        user.projects_limit = self.limit
                        user.save()
