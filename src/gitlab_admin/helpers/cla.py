import ldap
from gitlab import Gitlab, config, exceptions


class Cla:
    def __init__(self, gitlab_instance=None, private_token=None, cron=False):

        self.gitlab_instance = gitlab_instance
        self.private_token = private_token
        self.cron = cron

        try:
            self.gl = Gitlab(
                self.gitlab_instance,
                private_token=self.private_token)
        except config.GitlabConfigMissingError as err:
            print(err)

    def fetch_all(self):
        users = self.gl.users.list(as_list=False)
        return users

    def fetch(self, user_id):
        try:
            user = self.gl.users.get(user_id)
            return user
        except exceptions.GitlabGetError as err:
            print(err)

    def main(self):
        l = ldap.initialize('ldaps://ldap.rz.tu-harburg.de')

        for element in self.fetch_all():
            if element.state == 'active' and element.username != 'ghost' and not element.external:
                for identity in element.identities:
                    # print(identity['extern_uid'])
                    if identity["provider"] == "ldapmain":
                        uid_arg = identity['extern_uid'].split(',')[0]
                        try:
                            result = l.search_s('ou=People,dc=tu-harburg,dc=de', ldap.SCOPE_SUBTREE, '(' + uid_arg + ')',
                                                ['uid'])
                        except ldap.FILTER_ERROR:
                            print ("ldap.FILTER_ERROR for %s" % (identity))
                        else:
                            if len(result) <= 0:
                                print(identity)
