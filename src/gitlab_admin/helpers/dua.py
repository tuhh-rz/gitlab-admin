from datetime import datetime, timedelta

from gitlab import Gitlab, config

import gitlab_admin


class Dua:
    def __init__(self, gitlab_instance=None, token_file=None, nono=True, timedelta=None):

        self.nono = nono
        self.timedelta = timedelta

        private_token = gitlab_admin.gettoken(token_file)

        try:
            self.gl = Gitlab(
                gitlab_instance,
                private_token)
        except config.GitlabConfigMissingError as err:
            print(err)

    def main(self):
        if self.nono:
            print('No changes will be made.')

        deadline = datetime.today() - timedelta(days=self.timedelta)
        # print(deadline)

        for element in gitlab_admin.getallusers(self.gl):
            if not element.confirmed_at and element.external:
                if element.username != 'ghost' and element.username != 'migration-bot' and element.username != 'alert-bot':
                    # Am 01.06.2020 war wieder ein Z nötig
                    if deadline > datetime.strptime(element.created_at.split('+')[0], '%Y-%m-%dT%H:%M:%S.%fZ'):
                        print('{} {:24} {:>5} {} {}'.format('delete account', str(                   
                        # Am 01.06.2020 war wieder ein Z nötig
                            datetime.strptime(element.created_at.split('+')[0], '%Y-%m-%dT%H:%M:%S.%fZ')), element.id,
                                                            element.username, element.email))

                        if not self.nono:
                            element.delete()
