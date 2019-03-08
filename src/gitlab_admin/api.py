#!/usr/bin/env python

from . helpers import __version__

from . helpers.dua import Dua
from . helpers.spl import Spl

import argparse
import gitlab


def create_parser():
    parser = argparse.ArgumentParser(description="ToDo: Add description")

    parser.add_argument(
        "gitlab_instance", help="URL of your GitLab instance, e.g. https://gitlab.com/")
    parser.add_argument(
        "private_token", help="Access token for the API. You can generate one at Profile -> Settings")
    parser.add_argument("--version", action='version',
                        help='Print the version of this program.', version='%(prog)s {}'.format(__version__))

    subparsers = parser.add_subparsers(help="Available subcommands")

    parser_dua = subparsers.add_parser(
        'dua', help="Delete unconfirmed accounts")
    parser_dua.add_argument('--nono', action='store_true',
                            help='Do not make any changes')
    parser_dua.add_argument('-t', '--timedelta', type=int,
                            default=7, help='time delta')
    parser_dua.set_defaults(func=dua)

    parser_spl = subparsers.add_parser(
        'spl', help="Set the project limit of all accounts to a concrete value if the current value is smaller.")
    parser_spl.add_argument('--nono', action='store_true',
                            help='Do not make any changes')
    parser_spl.add_argument('-l', '--limit', required=True,
                            type=int, help='set project limit')
    parser_spl.set_defaults(func=spl)

    return parser


def dua(args):
    dua = Dua(args)
    dua.main()


def spl(args):
    spl = Spl(args)
    spl.main()


def main():
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
