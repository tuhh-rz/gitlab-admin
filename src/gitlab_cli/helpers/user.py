import argparse
import gitlab


class User:
    def __init__(self, args):

        self.gitlab_instance = args.gitlab_instance
        self.private_token = args.private_token
        self.id = args.id

        try:
            self.gl = gitlab.Gitlab(
                self.gitlab_instance,
                private_token=self.private_token)
        except gitlab.config.GitlabConfigMissingError as err:
            print(err)

    def fetch_users(self):
        users = self.gl.users.list()
        return users

    def fetch_user(self, id):
        try:
            user = self.gl.users.get(id)
            return user
        except gitlab.exceptions.GitlabGetError as err:
            print(err)


    def main(self):
        user = self.fetch_user(self.id)
        print('{:>5} {} {} {} {} {} {}'.format(str(user.id), user.username, user.email, user.external,
                                               user.projects_limit, user.can_create_group, user.can_create_project))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="user", description="ToDo: Add description")
    parser.add_argument(
        "gitlab_instance", help="URL of your GitLab instance, e.g. https://gitlab.com/")
    parser.add_argument(
        "private_token", help="Access token for the API. You can generate one at Profile -> Settings")
    parser.add_argument(
        "id", help="The ID of a GitLab project with issues", type=int)
    args = parser.parse_args()

    user = User(args)
    user.main()
