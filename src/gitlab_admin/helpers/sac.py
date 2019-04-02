import gitlab
import json
import os

import time

from datetime import datetime, timedelta
from googletrans import Translator
from pathlib import Path

# Potentielle Spam Accounts ermitteln

class Sac:
    def __init__(self, gitlab_instance=None, private_token=None, nocache=True, nono=True ):

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
        self.nocache = nocache
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

    def main(self):
        if self.nono:
            print('No changes will be made.')

        print ("Reading group members …")

        if not self.nocache and Path("cache/groups_member_ids.json").is_file():
            print ("… using cache")
            with open('cache/groups_member_ids.json') as handle:
                groups_member_ids = json.loads(handle.read())
        else:
            # Auch Subgroups erscheinen hier
            # Mir ist es egal, w´in welcher Gruppe ein User ist.
            # Deshalb interessiert mich nur, wer Mitglied in einer Gruppe ist
            groups = self.gl.groups.list(as_list=False)
            groups_member_ids = set()
            for group in groups:
                try:
                    group_members = group.members.list(as_list=False)
                    for group_member in group_members:
                        groups_member_ids.add(group_member.id)
                except Exception as identifier:
                    pass
            with open('cache/groups_member_ids.json', 'w') as handle:
                json.dump(list(groups_member_ids), handle)

        print ("Reading project members …")

        if not self.nocache and Path("cache/projects_member_ids.json").is_file():
            print ("… using cache")
            with open('cache/projects_member_ids.json') as handle:
                projects_member_ids = json.loads(handle.read())
        else:
            projects = self.gl.projects.list(as_list=False)
            projects_member_ids = set()
            for project in projects:
                try:
                    project_members = project.members.list(as_list=False)
                    for project_member in project_members:
                        projects_member_ids.add(project_member.name)
                except Exception as identifier:
                    pass
            with open('cache/projects_member_ids.json', 'w') as handle:
                json.dump(list(projects_member_ids), handle)

        timestr = time.strftime("%Y%m%d-%H%M%S")
        spam = open('spam_out/' + timestr, 'w')

        for element in self.fetch_all():
            if element.username != 'ghost' and element.external:
                # print(user.created_at)
                # print(datetime.strptime(user.created_at, '%Y-%m-%dT%H:%M:%S.%fZ'))
                # print(type(deadline))
                # print(type(user.created_at))

                if element.website_url != '' and element.bio != '':
                    # translator = Translator()
                    # translation = translator.translate(element.bio, dest='de')

                    if not element.id in projects_member_ids and not element.id in groups_member_ids:
                        print (element.bio)
                        print (element.last_sign_in_at)
                        # print(element.id)
                        print(element.website_url)
                        print(element.web_url)
                        # print(translation.text)

                        delete_answer = input("Delete (y/n)? ")
                        if delete_answer == "Y" or delete_answer == "y":
                            spam.write(element.bio + '\n')
                            spam.flush()
                            if not self.nono:
                                element.delete()

        spam.close()
        if os.stat('spam_out/' + timestr).st_size == 0:
            os.remove('spam_out/' + timestr)
