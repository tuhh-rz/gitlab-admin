import gitlab
import json
import re
import signal
import sys
import smtplib

import time

from datetime import datetime, timedelta
from googletrans import Translator
from pathlib import Path
from email.message import EmailMessage



# Potentielle Spam Accounts ermitteln

class Sac:
    def __init__(self, gitlab_instance=None, private_token=None, nocache=True, nono=False ):

        signal.signal(signal.SIGINT, self.signal_handler)

        self.path_spam = str(Path.home()) + '/.gitlab_admin/spam/spam.json'
        self.path_whitelist = str(Path.home()) + '/.gitlab_admin/cache/whitelist.json'
        self.path_groups_member_ids = str(Path.home()) + '/.gitlab_admin/cache/groups_member_ids.json'
        self.path_projects_member_ids = str(Path.home()) + '/.gitlab_admin/cache/projects_member_ids.json'

        Path(str(Path.home()) + '/.gitlab_admin/spam').mkdir(parents=True, exist_ok=True)
        Path(str(Path.home()) + '/.gitlab_admin/cache').mkdir(parents=True, exist_ok=True)

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

        with open(self.path_whitelist, 'w+') as handle:
            json.dump(list(self.whitelist_member_ids), handle)

        with open(self.path_spam, 'w+') as handle:
            json.dump(self.spam_accounts, handle)

        sys.exit(0)

    def print_info(self, element):
        # translator = Translator()
        # translation = translator.translate(element.bio, dest='de')

        if element.name: print ('name: ' + element.name)
        if element.bio: print ('bio: ' + element.bio)
        # print(element.id)
        if element.website_url: print('website_url: ' + element.website_url)
        if element.web_url: print('web_url: ' + element.web_url)
        if element.last_sign_in_at: print ('last_sign_in_at: ' + element.last_sign_in_at)
        # print(translation.text)

    def block_account(self, element):
        # ToDo: Mail versenden

        element.block()

        msg = EmailMessage()
        msg.set_content("""\
Hallo """ + element.name + """,\


ihr GitLab Account der TUHH (https://collaborating.tuhh.de/) wurde als Spam eingestuft und aus diesem Grund blokiert.
Wenn Sie der Meinung sind, dass das eine falsche Entscheidung war, dann setzen Sie sich bitte mit dem Servicedesk der TUHH in Verbindung.\


Mit freundlichen Grüßem,
Ihr GitLab Administrator


https://www.tuhh.de/
https://collaborating.tuhh.de/

---

Hello """ + element.name + """,\


Your TUHH GitLab account (https://collaborating.tuhh.de/) has been classified as spam and has been blocked for this reason.
If you think this was a wrong decision, please contact the TUHH Service Desk.\


Sincerely yours,
Your GitLab Administrator


https://www.tuhh.de/
https://collaborating.tuhh.de/
""")

        msg['Subject'] = 'Ihr Account wurde blockiert / Your account has been blocked.'
        msg['From'] = 'nobody@tuhh.de'
        msg['To'] = element.email

        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()

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

        if not self.nocache and Path(self.path_groups_member_ids).is_file():
            print ("… using cache")
            with open(self.path_groups_member_ids) as handle:
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
                except Exception:
                    pass
            with open(self.path_groups_member_ids, 'w') as handle:
                json.dump(list(groups_member_ids), handle)

        print ("Reading project members …")

        if not self.nocache and Path(self.path_projects_member_ids).is_file():
            print ("… using cache")
            with open(self.path_projects_member_ids) as handle:
                projects_member_ids = json.loads(handle.read())
        else:
            projects = self.gl.projects.list(as_list=False)
            projects_member_ids = set()
            for project in projects:
                try:
                    project_members = project.members.list(as_list=False)
                    for project_member in project_members:
                        projects_member_ids.add(project_member.id)
                except Exception:
                    pass
            with open(self.path_projects_member_ids, 'w') as handle:
                json.dump(list(projects_member_ids), handle)



        if Path(self.path_whitelist).is_file() and Path(self.path_spam).stat().st_size > 0:
            with open(self.path_whitelist, 'r') as handle:
                self.whitelist_member_ids = set(json.loads(handle.read()))

        if Path(self.path_spam).is_file() and Path(self.path_spam).stat().st_size > 0:
            with open(self.path_spam, 'r') as handle:
                self.spam_accounts = json.loads(handle.read())

        for element in self.fetch_all():
            if element.state == 'active' and not element.id in self.whitelist_member_ids and element.username != 'ghost' and element.external:
                # print(user.created_at)
                # print(datetime.strptime(user.created_at, '%Y-%m-%dT%H:%M:%S.%fZ'))
                # print(type(deadline))
                # print(type(user.created_at))

                for k, v in self.spam_accounts.items():
                    if element.website_url != '' and v['website_url'].lower() == element.website_url.lower():
                        print ('Cached SPAM URL: ' + element.website_url)
                        self.print_info(element)

                        delete_block = input("Delete/Block (d/b/n)? ")
                        if delete_block == "d":
                            if not self.nono:
                                 element.delete()
                        elif delete_block == "b":
                            if not self.nono:
                                self.block_account(element)
                        print()
                    elif element.bio != '' and v['bio'] == element.bio:
                        print ('Cached SPAM Bio: ' + element.bio)
                        self.print_info(element)

                        delete_block = input("Delete/Block (d/b/n)? ")
                        if delete_block == "d":
                            if not self.nono:
                                 element.delete()
                        elif delete_block == "b":
                            if not self.nono:
                                 self.block_account(element)
                        elif input("Whitelist? (y/n)? ") == "y":
                            self.whitelist_member_ids.add(element.id)
                        print()

                if element.website_url != '' and element.bio != '' and not element.id in projects_member_ids and not element.id in groups_member_ids:
                    self.print_info(element)

                    delete_block = input("Delete/Block (d/b/n)? ")
                    if delete_block == "d":
                        if not self.nono:
                            self.spam_accounts[element.id] = element.attributes
                            element.delete()
                    elif delete_block == "b":
                        if not self.nono:
                            self.spam_accounts[element.id] = element.attributes
                            self.block_account(element)
                    elif input("Whitelist? (y/n)? ") == "y":
                        self.whitelist_member_ids.add(element.id)
                    print()

                elif element.website_url != '' and (not re.match( r'.*\s.*', element.name) or element.name.islower()):
                    self.print_info(element)

                    delete_block = input("Delete/Block (d/b/n)? ")
                    if delete_block == "d":
                        if not self.nono:
                            self.spam_accounts[element.id] = element.attributes
                            element.delete()
                    elif delete_block == "b":
                        if not self.nono:
                            self.spam_accounts[element.id] = element.attributes
                            self.block_account(element)
                    elif input("Whitelist? (y/n)? ") == "y":
                        self.whitelist_member_ids.add(element.id)
                    print()

        with open(self.path_whitelist, 'w+') as handle:
            json.dump(list(self.whitelist_member_ids), handle)

        with open(self.path_spam, 'w+') as handle:
            json.dump(self.spam_accounts, handle)
