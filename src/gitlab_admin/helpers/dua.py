import argparse
import gitlab


class Dua:
    def __init__(self, args):

        self.gitlab_instance = args.gitlab_instance
        self.private_token = args.private_token
        self.nono = args.nono

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
            print ('No changes will be made.')
            
        for user in self.fetch_users():
            print('{:>5} {} {} {} {} {} {}'.format(str(user.id), user.username, user.email, user.external,
                                               user.projects_limit, user.can_create_group, user.can_create_project))


