import email.message
import json
import signal
import smtplib
import sys
from datetime import datetime, timedelta
from pathlib import Path

from gitlab import Gitlab, config, GitlabBlockError

import gitlab_admin


# Potentielle Spam Accounts ermitteln

class Bsa:
    def __init__(self, gitlab_instance=None, token_file=None, nocache=True, nono=True, cron=False):

        self.projects_member_ids = set()
        self.groups_member_ids = set()
        signal.signal(signal.SIGINT, self.signal_handler)

        self.path_whitelist = str(Path.home()) + '/.gitlab_admin/cache/whitelist.json'
        self.path_groups_member_ids = str(Path.home()) + '/.gitlab_admin/cache/groups_member_ids.json'
        self.path_projects_member_ids = str(Path.home()) + '/.gitlab_admin/cache/projects_member_ids.json'

        Path(str(Path.home()) + '/.gitlab_admin/cache').mkdir(parents=True, exist_ok=True)

        self.gitlab_instance = gitlab_instance
        self.nocache = nocache
        self.nono = nono
        self.cron = cron
        self.threshold = 0

        self.trusted_countries = "germany"

        self.deadline_days = 1
        self.deadline = datetime.today() - timedelta(self.deadline_days)

        self.whitelist_member_ids = set()

        private_token = gitlab_admin.gettoken(token_file)

        try:
            self.gl = Gitlab(
                self.gitlab_instance,
                private_token)
        except config.GitlabConfigMissingError as err:
            print(err, file=sys.stderr)

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
    def block_account(element, score_results):

        if element.email == "":
            print("No email, no block :cP")
            print(element)
        else:
            try:
                element.block()
            except GitlabBlockError as err:
                print(err, file=sys.stderr)
                print(element, file=sys.stderr)

            msg = email.message.EmailMessage()

            msg['subject'] = "[TUHH GitLab] Ihr Account wurde blockiert / Your account has been blocked."
            msg['from'] = "nobody@tuhh.de"
            msg['to'] = element.email
            msg['bcc'] = "rzt+container@rz.tu-harburg.de"

            msg.set_content("""\
Hallo """ + element.name + """,\


Ihr GitLab Account der TUHH (https://collaborating.tuhh.de/) wurde als verwaist eingestuft und aus diesem Grund 
blockiert. Wenn Sie der Meinung sind, dass das eine falsche Entscheidung ist, dann setzen Sie sich bitte mit dem 
Servicedesk des Rechenzentrums der TUHH in Verbindung. Die Kontaktdaten finden Sie auf der Seite der TUHH (
https://www.tuhh.de/). Alternativ können sie sich auch an einen Mitarbeiter oder eine Mitarbeiterin der Projekte 
wenden, in denen sie mitarbeiten. 


""" + score_results + """


Mit freundlichen Grüßen,
Ihr GitLab Administrator


https://www.tuhh.de/
https://collaborating.tuhh.de/

---

Hello """ + element.name + """,\


Your GitLab account at TUHH (https://collaborating.tuhh.de/) has been blocked due to orphan status. If you think this 
is a wrong decision, please contact the TUHH Data Center Service Desk. The contact details can be found on the TUHH 
website (https://www.tuhh.de/). Alternatively, you can also contact a member of staff of the projects in which you 
are involved. 


""" + score_results + """


Sincerely yours,
Your GitLab Administrator


https://www.tuhh.de/
https://collaborating.tuhh.de/

""" + gitlab_admin.__version__ + """

""")

            s = smtplib.SMTP('localhost')
            s.send_message(msg)
            s.quit()

    def fire(self, element, score_results):
        if self.cron:
            self.print_info(element)
            block_account = "b"
        else:
            self.print_info(element)
            block_account = input("Block/Nothing (b/n)? ")

        if block_account == "b":
            if not self.nono:
                self.block_account(element, score_results)
        elif input("Whitelist? (y/n)? ") == "y":
            self.whitelist_member_ids.add(element.id)
        print()

    def print_full_info(self, element):
        print("location\t" + str(element.location))
        print("linkedin\t" + str(element.linkedin))
        print("twitter\t" + str(element.twitter))
        print("current_sign_in_at\t" + str(element.current_sign_in_at))
        print("username\t" + str(element.username))
        # print("highest_role\t" + str(element.highest_role))
        print("avatar_url\t" + str(element.avatar_url))
        print("projects_limit\t" + str(element.projects_limit))
        print("last_sign_in_at\t" + str(element.last_sign_in_at))
        print("name\t" + str(element.name))
        print("bio\t" + str(element.bio))
        print("last_activity_on\t" + str(element.last_activity_on))
        print("id\t" + str(element.id))
        print("identities\t" + str(element.identities))
        print("color_scheme_id\t" + str(element.color_scheme_id))
        print("web_url\t" + str(element.web_url))
        print("website_url\t" + str(element.website_url))
        print("email\t" + str(element.email))
        print("confirmed_at\t" + str(element.confirmed_at))
        print("external\t" + str(element.external))
        print("theme_id\t" + str(element.theme_id))
        print("private_profile\t" + str(element.private_profile))
        print("is_admin\t" + str(element.is_admin))
        print("skype\t" + str(element.skype))
        print("organization\t" + str(element.organization))
        print("created_at\t" + str(element.created_at))
        print("can_create_group\t" + str(element.can_create_group))
        print("two_factor_enabled\t" + str(element.two_factor_enabled))
        print("public_email\t" + str(element.public_email))
        print("can_create_project\t" + str(element.can_create_project))
        print("state\t" + str(element.state))
        if element.id in self.projects_member_ids:
            print("project member\t" + "True")
        else:
            print("project member\t" + "False")
        if element.id in self.groups_member_ids:
            print("group member\t" + "True")
        else:
            print("group member\t" + "False")

    def main(self):
        if self.nono and not self.cron:
            print('No changes will be made.')

        if not self.cron:
            print("Reading group members …")

        if not self.nocache and Path(self.path_groups_member_ids).is_file():
            if not self.cron:
                print("… using cache")
            with open(self.path_groups_member_ids) as handle:
                self.groups_member_ids = json.loads(handle.read())
        else:
            # Auch Subgroups erscheinen hier
            # Mir ist es egal, in welcher Gruppe ein User ist.
            # Deshalb interessiert mich nur, wer Mitglied in einer Gruppe ist
            groups = self.gl.groups.list(as_list=False)

            for group in groups:
                try:
                    group_members = group.members.list(as_list=False)
                    for group_member in group_members:
                        self.groups_member_ids.add(group_member.id)
                except Exception as err:
                    print(err, file=sys.stderr)
                    pass
            with open(self.path_groups_member_ids, 'w') as handle:
                json.dump(list(self.groups_member_ids), handle)

        if not self.cron:
            print("Reading project members …")

        if not self.nocache and Path(self.path_projects_member_ids).is_file():
            if not self.cron:
                print("… using cache")
            with open(self.path_projects_member_ids) as handle:
                self.projects_member_ids = json.loads(handle.read())
        else:
            projects = self.gl.projects.list(as_list=False)

            for project in projects:
                try:
                    project_members = project.members.list(as_list=False)

                    for project_member in project_members:
                        self.projects_member_ids.add(project_member.id)
                except Exception as err:
                    print(err, file=sys.stderr)
                    pass
            with open(self.path_projects_member_ids, 'w') as handle:
                json.dump(list(self.projects_member_ids), handle)

        if Path(self.path_whitelist).is_file() and Path(self.path_whitelist).stat().st_size > 0:
            with open(self.path_whitelist, 'r') as handle:
                self.whitelist_member_ids = set(json.loads(handle.read()))

        score_defs = {"location": ({"yes": -10, "no": 0, "description": "Trusted country?"}),
                      "projects_limit": ({"yes": -10, "no": 0, "description": "Project limit not 0?"}),
                      "bio": ({"yes": -0, "no": 5, "description": "Unused bio?"}),
                      "identities": ({"yes": -10, "no": 0, "description": "Additional identities?"}),
                      "website_url": ({"yes": -0, "no": 5, "description": "Unused Website?"}),
                      "email": ({"yes": -10, "no": 0, "description": "Trusted mail domain?"}),
                      "private_profile": ({"yes": -10, "no": 0, "description": "Private profile?"}),
                      "is_admin": ({"yes": -100, "no": 0, "description": "Is Admin?"}),
                      "can_create_group": ({"yes": -10, "no": 0, "description": "Can create groups?"}),
                      "can_create_project": ({"yes": -10, "no": 0, "description": "Can create projects?"}),
                      "two_factor_enabled": (
                          {"yes": -10, "no": 0, "description": "Two factor authentication enabled?"}),
                      "projects_member_ids": ({"yes": -15, "no": 0, "description": "Is project member?"}),
                      "groups_member_ids": ({"yes": -15, "no": 0, "description": "Is group member?"}),
                      "last_activity_on": (
                          {"yes": -15, "no": 0,
                           "description": "Activity in the last " + str(self.deadline_days) + " day(s) ago?"})}

        for element in gitlab_admin.getallusers(self.gl):
            # if element.id == 3450:
            score = 0
            score_results = ""
            if element.external and element.state == 'active':
                if element.username != 'ghost' and \
                        element.username != 'migration-bot' and \
                        element.username != 'alert-bot' and \
                        element.username != 'support-bot':
                    # if element.state == 'blocked' and element.username != 'ghost':
                    # if element.state == 'active' and element.username != 'ghost':
                    # if element.username != 'ghost':
                    # self.printFullInfo(element, projects_member_ids, groups_member_ids)
                    # score_def = "location"
                    # yes_or_no = "yes" if  str(element.location).lower() in self.trusted_countries else "no"
                    # score_results += (score_defs[score_def]["description"] + " " + yes_or_no + " -> " + str(
                    #     score_defs[score_def][yes_or_no]))
                    # score += score_defs[score_def][yes_or_no]

                    score_def = "projects_limit"
                    yes_or_no = "yes" if element.projects_limit > 0 else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "bio"
                    yes_or_no = "yes" if str(element.bio) == 'None' or str(element.bio) == '' else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "identities"
                    yes_or_no = "yes" if len(element.identities) > 0 else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "website_url"
                    yes_or_no = "yes" if str(element.website_url) == 'None' or str(element.website_url) == '' else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "email"
                    yes_or_no = "yes" if element.email.split('@')[1] in gitlab_admin.trusted_domains else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "private_profile"
                    yes_or_no = "yes" if element.private_profile else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "is_admin"
                    yes_or_no = "yes" if element.is_admin else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "can_create_group"
                    yes_or_no = "yes" if element.can_create_group else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "two_factor_enabled"
                    yes_or_no = "yes" if element.two_factor_enabled else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "can_create_project"
                    yes_or_no = "yes" if element.can_create_project else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "projects_member_ids"
                    yes_or_no = "yes" if element.id in self.projects_member_ids else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "groups_member_ids"
                    yes_or_no = "yes" if element.id in self.groups_member_ids else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]

                    score_def = "last_activity_on"
                    # print(datetime.strptime(element.last_activity_on, '%Y-%m-%d'))
                    # print (self.deadline)
                    yes_or_no = "yes" if element.last_activity_on and self.deadline < datetime.strptime(
                        element.last_activity_on, '%Y-%m-%d') else "no"
                    score_results += (score_defs[score_def]["description"] + " " + yes_or_no.upper() + " -> " + str(
                        score_defs[score_def][yes_or_no]) + "\n")
                    score += score_defs[score_def][yes_or_no]
                    score_results += ("\nScore: " + str(
                        score) + " (A value of > " + str(
                        self.threshold) + " is required to be classified as orphaned.)\n\n")

                    score_results += ("ID: " + str(element.id) + "\n")
                    score_results += ("Name: " + element.name + "\n")
                    score_results += ("Username: " + element.username + "\n")
                    score_results += ("eMail: " + element.email + "\n")
                    score_results += ("URL: " + element.web_url + "\n")

                    if score > self.threshold:
                        print("================================================================================")
                        print("Account:")
                        print("================================================================================")
                        print("\nResults:\n" + score_results)

                        self.fire(element, score_results)

        with open(self.path_whitelist, 'w+') as handle:
            json.dump(list(self.whitelist_member_ids), handle)
