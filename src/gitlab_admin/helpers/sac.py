import gitlab

from datetime import datetime, timedelta
from googletrans import Translator

# Potentielle Spam Accounts ermitteln

class Sac:
    def __init__(self, gitlab_instance=None, private_token=None, nono=True ):

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
        self.nono = nono

        try:
            self.gl = gitlab.Gitlab(
                self.gitlab_instance,
                private_token=self.private_token)
        except gitlab.config.GitlabConfigMissingError as err:
            print(err)

    def fetch_all(self):
        users = self.gl.users.list(as_list=False)
        return users

    def fetch(self, id):
        try:
            user = self.gl.users.get(id)
            return user
        except gitlab.exceptions.GitlabGetError as err:
            print(err)

    # def fetch_groups(self, id=0):
    #     if id == 0:
    #         for group in self.gl.groups.list(as_list=False):
    #             print("MG " + group.full_path)
    #             self.fetch_groups(group.id)
    #     else:
    #         for group in self.gl.groups.get(id).subgroups.list(as_list=False):
    #             print("SG " + group.full_path)
    #             self.fetch_groups(group.id)

    def main(self):
        if self.nono:
            print('No changes will be made.')

        # self.fetch_groups()

        # Auch Subgroups erscheinen hier
        # Mir ist es egal, w´in welcher Gruppe ein User ist.
        # Deshalb interessiert mich nur, wer Mitglied in einer Gruppe ist
        groups = self.gl.groups.list(as_list=False)
        members = []

        for group in groups:
            try:
                members.append(group.members.list(as_list=False))
            except Exception as identifier:
                pass

        for element in self.fetch_all():
            if element.username != 'ghost' and element.external:
                # print(user.created_at)
                # print(datetime.strptime(user.created_at, '%Y-%m-%dT%H:%M:%S.%fZ'))
                # print(type(deadline))
                # print(type(user.created_at))

                personal_projects = 0
                group_membership = 0

                if element.website_url != '' and element.bio != '':
                    # translator = Translator()
                    # translation = translator.translate(element.bio, dest='de')

                    personal_projects = element.projects.list(as_list=False)
                    personal_projects_len = len(personal_projects)




                    if personal_projects_len == 0 and group_membership == 0:
                        print (element.external)
                        print (element.bio)
                        print (element.last_sign_in_at)
                        # print(element.id)
                        # print(element.website_url)
                        print(element.web_url)
                        print()
                    # print(translation.text)

                    # if not self.nono:
                    #     element.delete()
