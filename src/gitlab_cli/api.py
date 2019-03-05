#!/usr/bin/env python

from . helpers import __version__

from . helpers.user import User

import argparse
import gitlab


def user(args):

    user = User(args)
    user.main()


def main():
    parser = argparse.ArgumentParser(
        prog="gitlab-cli", description="ToDo: Add description")
    parser.add_argument(
        "gitlab_instance", help="URL of your GitLab instance, e.g. https://gitlab.com/")
    parser.add_argument(
        "private_token", help="Access token for the API. You can generate one at Profile -> Settings")
    parser.add_argument("--version", action='version',
                        help='Print the version of this program.', version='%(prog)s {}'.format(__version__))
    subparsers = parser.add_subparsers(help="Available subcommands")

    parser_user = subparsers.add_parser('user', help="ToDo: Add help")
    parser_user.add_argument('id', type=int, help='The ID of a GitLab user.')
    parser_user.set_defaults(func=user)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
