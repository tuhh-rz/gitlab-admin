import setuptools

from src.gitlab_admin import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "gitlab-admin",
    version = __version__,
    author = "Andreas Böttger, Axel Duerkop",
    author_email = "andreas.boettger@tuhh.de, axel.duerkop@tuhh.de",
    description = "",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "",
    packages = setuptools.find_packages(where = 'src'),
    python_requires = ">=3.7",
    py_modules = ['gitlab_admin.api'],
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
            'gitlab-admin=gitlab_admin.api:main',
        ],
    },
    install_requires = [
        'python-gitlab >= 1.8.0',
        'googletrans',
        'simplejson',
        'pathlib',
    ],
)