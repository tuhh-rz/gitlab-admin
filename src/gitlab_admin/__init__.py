import getpass
import sys

from gitlab import exceptions

name = "gitlab-admin"  # type: str
__version__ = '0.11.4'

trusted_domains = (
    "tuhh.de", "tu-harburg.de", "uni-hamburg.de", "hcu-hamburg.de", "hsu-hh.de", "haw-hamburg.de", "tum.de",
    "hfbk-hamburg.de", "stifterverband.de", "uni-rostock.de", "mmkh.de", "uni-muenster.de", "ph-ludwigsburg.de",
    "fu-berlin.de", "bsb.hamburg.de", "hs-magdeburg.de", "fau.de", "ku.de", "h-ab.de", "th-ab.de", "hs-augsburg.de",
    "digll-hessen.de", "fh-swf.de", "gwdg.de",
    "uke.de", "umsicht.fraunhofer.de", "bsb.hamburg.de", "digll-hessen.de")


def gettoken(tokenfile=None):
    if not tokenfile:
        private_token = getpass.getpass("Enter your private token: ")
    else:
        with open(tokenfile) as f:
            private_token = f.readline().rstrip('\n')
        f.close()

    return private_token


def getallusers(gl):
    users = gl.users.list(as_list=False)
    return users


def getuser(gl, id):
    try:
        user = gl.users.get(id)
        return user
    except exceptions.GitlabGetError as err:
        print(err, file=sys.stderr)
