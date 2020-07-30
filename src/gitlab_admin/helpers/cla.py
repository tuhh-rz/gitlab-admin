import sys

import ldap
from gitlab import Gitlab, config

import gitlab_admin


class Cla:
    def __init__(self, gitlab_instance=None, token_file=None, nono=True, cron=False):

        self.gitlab_instance = gitlab_instance
        self.nono = nono
        self.cron = cron

        private_token = gitlab_admin.gettoken(token_file)

        try:
            self.gl = Gitlab(
                self.gitlab_instance,
                private_token)
        except config.GitlabConfigMissingError as err:
            print(err, file=sys.stderr)

    def main(self):
        if self.nono:
            print('No changes will be made.')
        tuhh_ldap = ldap.initialize('ldaps://ldap.rz.tu-harburg.de')

        for element in gitlab_admin.getallusers(self.gl):
            if element.state == 'active' and element.username != 'ghost' and not element.external:
                for identity in element.identities:
                    # print(identity['extern_uid'])
                    if identity["provider"] == "ldapmain":
                        uid_arg = identity['extern_uid'].split(',')[0]
                        try:
                            result = tuhh_ldap.search_s('ou=People,dc=tu-harburg,dc=de', ldap.SCOPE_SUBTREE,
                                                        '(' + uid_arg + ')',
                                                        ['uid'])
                        except ldap.FILTER_ERROR:
                            print("ldap.FILTER_ERROR for %s" % identity)
                        else:
                            if len(result) <= 0:
                                if not self.cron:
                                    print(identity)
                                    print(element.web_url)
                                if not self.nono:
                                    element.delete()
