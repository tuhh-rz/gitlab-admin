import argparse

from gitlab_admin import __version__
from gitlab_admin.helpers.bsa import Bsa
from gitlab_admin.helpers.cla import Cla
from gitlab_admin.helpers.dba import Dba
from gitlab_admin.helpers.dua import Dua
from gitlab_admin.helpers.ffe import Ffe
from gitlab_admin.helpers.gfe import Gfe
from gitlab_admin.helpers.spl import Spl


def create_parser():
    parser = argparse.ArgumentParser(description="ToDo: Add description")

    parser.add_argument(
        "gitlab_instance", help="URL of your GitLab instance, e.g. https://gitlab.com/")
    parser.add_argument(
        "-f", "--tokenfile", type=str,
        help="A file with the access token for the API. You can generate one at Profile -> Settings", required=False)
    parser.add_argument("--version", action='version',
                        help='Print the version of this program.', version='%(prog)s {}'.format(__version__))

    subparsers = parser.add_subparsers(help="Available subcommands")

    parser_gfe = subparsers.add_parser(
        'gfe', help="Get former external accounts")
    parser_gfe.set_defaults(func=gfe)

    parser_ffe = subparsers.add_parser(
        'ffe', help="Fix false external")
    parser_ffe.add_argument('--nono', action='store_true',
                            help='Do not make any changes')
    parser_ffe.set_defaults(func=ffe)

    parser_dba = subparsers.add_parser(
        'dba', help="Delete blocked accounts")
    parser_dba.add_argument('--nono', action='store_true',
                            help='Do not make any changes')
    parser_dba.add_argument('-t', '--timedelta', type=int,
                            default=30, help='time delta')
    parser_dba.set_defaults(func=dba)

    parser_dua = subparsers.add_parser(
        'dua', help="Delete unconfirmed accounts")
    parser_dua.add_argument('--nono', action='store_true',
                            help='Do not make any changes')
    parser_dua.add_argument('-t', '--timedelta', type=int,
                            default=7, help='time delta')
    parser_dua.set_defaults(func=dua)

    parser_sac = subparsers.add_parser(
        'bsa', help="Block spam accounts")
    parser_sac.add_argument('--nocache', action='store_true',
                            help='Do not use cached files')
    parser_sac.add_argument('--nono', action='store_true',
                            help='Do not make any changes')
    parser_sac.add_argument('--cron', action='store_true',
                            help='Do not ask me')
    parser_sac.set_defaults(func=bsa)

    parser_cla = subparsers.add_parser(
        'cla', help="Check LDAP accounts")
    parser_cla.add_argument('--cron', action='store_true',
                            help='Do not ask me')
    parser_cla.set_defaults(func=cla)

    parser_spl = subparsers.add_parser(
        'spl', help="Set the project limit of all accounts to a concrete value if the current value is smaller.")
    parser_spl.add_argument('--nono', action='store_true',
                            help='Do not make any changes')
    parser_spl.add_argument('-l', '--limit', required=True,
                            type=int, help='set project limit')
    parser_spl.set_defaults(func=spl)

    return parser


def gfe(args):
    gfe = Gfe(args.gitlab_instance, args.tokenfile)
    gfe.main()


def ffe(args):
    ffe = Ffe(args.gitlab_instance, args.tokenfile, args.nono)
    ffe.main()


def bsa(args):
    bsa = Bsa(args.gitlab_instance, args.tokenfile, args.nocache, args.nono, args.cron)
    bsa.main()


def cla(args):
    cla = Cla(args.gitlab_instance, args.tokenfile, args.cron)
    cla.main()

def dua(args):
    dua = Dua(args.gitlab_instance, args.tokenfile, args.nono, args.timedelta)
    dua.main()


def dba(args):
    dba = Dba(args.gitlab_instance, args.tokenfile, args.nono, args.timedelta)
    dba.main()

def spl(args):
    spl = Spl(args.gitlab_instance, args.tokenfile, args.nono, args.limit)
    spl.main()

def main():
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
