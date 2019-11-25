import email.message
import json
import re
import signal
import smtplib
import sys
from pathlib import Path

from gitlab import Gitlab, config, exceptions


# Potentielle Spam Accounts ermitteln und blocken

class Bsa:
    def __init__(self, gitlab_instance=None, private_token=None, nocache=True, nono=False, cron=False):

        signal.signal(signal.SIGINT, self.signal_handler)

        self.path_whitelist = str(Path.home()) + '/.gitlab_admin/cache/whitelist.json'
        self.path_groups_member_ids = str(Path.home()) + '/.gitlab_admin/cache/groups_member_ids.json'
        self.path_projects_member_ids = str(Path.home()) + '/.gitlab_admin/cache/projects_member_ids.json'

        Path(str(Path.home()) + '/.gitlab_admin/cache').mkdir(parents=True, exist_ok=True)

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
        self.nocache = nocache
        self.nono = nono
        self.cron = cron

        self.whitelist_member_ids = set()

        try:
            self.gl = Gitlab(
                self.gitlab_instance,
                private_token=self.private_token)
        except config.GitlabConfigMissingError as err:
            print(err)

    def signal_handler(self):
        print('You pressed Ctrl+C!')

        with open(self.path_whitelist, 'w+') as handle:
            json.dump(list(self.whitelist_member_ids), handle)

        sys.exit(0)

    @staticmethod
    def print_short_info(element):
        if element.name:
            print('name: ' + element.name)

    @staticmethod
    def print_info(element):
        # translator = Translator()
        # translation = translator.translate(element.bio, dest='de')

        if element.name:
            print('name: ' + element.name)
        if element.bio:
            print('bio: ' + element.bio)
        # print(element.id)
        if element.website_url:
            print('website_url: ' + element.website_url)
        if element.web_url:
            print('web_url: ' + element.web_url)
        if element.last_sign_in_at:
            print('last_sign_in_at: ' + element.last_sign_in_at)
        # print(translation.text)

    @staticmethod
    def block_account(element):
        element.block()

        msg = email.message.EmailMessage()
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

        try:
            s = smtplib.SMTP('localhost')
            s.send_message(msg)
            s.quit()
        except ConnectionRefusedError:
            pass

    def fetch_all(self):
        users = self.gl.users.list(as_list=False)
        return users

    def fetch(self, user_id):
        try:
            user = self.gl.users.get(user_id)
            return user
        except exceptions.GitlabGetError as err:
            print(err)

    def fire(self, element):
        if self.cron:
            self.print_info(element)
            block_account = "b"
        else:
            self.print_info(element)
            block_account = input("Block/Nothing (b/n)? ")

        if block_account == "b":
            if not self.nono:
                self.block_account(element)
        elif input("Whitelist? (y/n)? ") == "y":
            self.whitelist_member_ids.add(element.id)
        print()

    def main(self):
        if self.nono and not self.cron:
            print('No changes will be made.')

        if not self.cron:
            print("Reading group members …")

        if not self.nocache and Path(self.path_groups_member_ids).is_file():
            if not self.cron:
                print("… using cache")
            with open(self.path_groups_member_ids) as handle:
                groups_member_ids = json.loads(handle.read())
        else:
            # Auch Subgroups erscheinen hier
            # Mir ist es egal, in welcher Gruppe ein User ist.
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

        if not self.cron:
            print("Reading project members …")

        if not self.nocache and Path(self.path_projects_member_ids).is_file():
            if not self.cron:
                print("… using cache")
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

        if Path(self.path_whitelist).is_file() and Path(self.path_whitelist).stat().st_size > 0:
            with open(self.path_whitelist, 'r') as handle:
                self.whitelist_member_ids = set(json.loads(handle.read()))

        for element in self.fetch_all():
            if element.state == 'active' and element.id not in self.whitelist_member_ids and element.username != 'ghost' and element.external:
                was_cached = False

                if not was_cached:
                    print("website_url " + element.website_url)
                    print("bio " + element.bio)
                    if (element.website_url != '' or element.bio != '') and element.id not in projects_member_ids and element.id not in groups_member_ids:
                        # Website oder Bio eingetragen und kein Mitglied in Gruppe und Projekt
                        self.fire(element)
                    elif (element.website_url != '' or element.bio != '') and (not re.match(r'.*\s.*', element.name) or element.name.islower()):
                        # Website oder Bio eingetragen und Name komplett klein und ohne Leerzeichen
                        self.fire(element)

        with open(self.path_whitelist, 'w+') as handle:
            json.dump(list(self.whitelist_member_ids), handle)
