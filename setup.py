import setuptools

from src.gitlab_cli.helpers import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "gitlab-cli",
    version = __version__,
    author = "Andreas Böttger, Axel Duerkop",
    author_email = "andreas.boettger@tuhh.de, axel.duerkop@tuhh.de",
    description = "",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "",
    packages = setuptools.find_packages(where = 'src'),
    python_requires = ">=3.6",
    py_modules = ['api'],
    package_dir = {
        '': 'src'
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'gitlab-cli=gitlab_cli.api:main',
        ],
    },
    install_requires = [
        'python-gitlab>=1.7.0'
    ]
)