import gitlab
import json
import os
import re
import signal
import sys

import time

from datetime import datetime, timedelta
from googletrans import Translator
from pathlib import Path



# Potentielle Spam Accounts ermitteln

class Sac:
    def __init__(self, gitlab_instance=None, private_token=None, nocache=True, nono=False ):

        signal.signal(signal.SIGINT, self.signal_handler)

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
        self.nocache = nocache
        self.nono = nono

        self.whitelist_member_ids = set()
        self.spam_accounts = dict()

        try:
            self.gl = gitlab.Gitlab(
                self.gitlab_instance,
                private_token=self.private_token)
        except gitlab.config.GitlabConfigMissingError as err:
            print(err)

    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C!')

        with open('cache/whitelist.json', 'w+') as handle:
            json.dump(list(self.whitelist_member_ids), handle)

        with open('spam/spam.json', 'w+') as handle:
            json.dump(self.spam_accounts, handle)

        sys.exit(0)

    def print_info(self, element):
        # translator = Translator()
        # translation = translator.translate(element.bio, dest='de')

        print ('name: ' + element.name)
        print ('bio: ' + element.bio)
        # print(element.id)
        print('website_url: ' + element.website_url)
        print('web_url: ' + element.web_url)
        print ('last_sign_in_at: ' + element.last_sign_in_at)
        # print(translation.text)

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



        if Path("cache/whitelist.json").is_file() and os.stat('cache/whitelist.json').st_size > 0:
            with open('cache/whitelist.json', 'r') as handle:
                self.whitelist_member_ids = json.loads(handle.read())

        if Path("spam/spam.json").is_file() and os.stat('spam/spam.json').st_size > 0:
            with open('spam/spam.json', 'r') as handle:
                self.spam_accounts = json.loads(handle.read())

        for element in self.fetch_all():
            if element.state == 'active' and not element.id in self.whitelist_member_ids and element.username != 'ghost' and element.external:
                # print(user.created_at)
                # print(datetime.strptime(user.created_at, '%Y-%m-%dT%H:%M:%S.%fZ'))
                # print(type(deadline))
                # print(type(user.created_at))

                if element.website_url != '' and element.bio != '' and not element.id in projects_member_ids and not element.id in groups_member_ids:
                    self.print_info(element)

                    delete_block = input("Delete/Block (d/b/n)? ")
                    if delete_block == "d":
                        self.spam_accounts[element.id] = element.attributes
                        if not self.nono:
                            element.delete()
                    elif delete_block == "b":
                        self.spam_accounts[element.id] = element.attributes
                        if not self.nono:
                            element.block()
                    elif input("Whitelist? (y/n)? ") == "y":
                        self.whitelist_member_ids.add(element.id)

                elif element.website_url != '' and (not re.match( r'\s', element.name, re.M|re.I) or element.name.islower()):
                    self.print_info(element)

                    delete_block = input("Delete/Block (d/b/n)? ")
                    if delete_block == "d":
                        self.spam_accounts[element.id] = element.attributes
                        if not self.nono:
                            element.delete()
                    elif delete_block == "b":
                        self.spam_accounts[element.id] = element.attributes
                        if not self.nono:
                            element.block()
                    elif input("Whitelist? (y/n)? ") == "y":
                        self.whitelist_member_ids.add(element.id)

        with open('cache/whitelist.json', 'w+') as handle:
            json.dump(list(self.whitelist_member_ids), handle)

        with open('spam/spam.json', 'w+') as handle:
            json.dump(self.spam_accounts, handle)
