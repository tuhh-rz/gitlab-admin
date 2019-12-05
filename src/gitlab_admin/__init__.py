import getpass

from gitlab import exceptions

name = "gitlab-admin"  # type: str
__version__ = '0.8.1'


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
        print(err)
