# Odoo helper scripts collection

| Master        | [![pipeline status](https://gitlab.com/katyukha/odoo-helper-scripts/badges/master/pipeline.svg)](https://gitlab.com/katyukha/odoo-helper-scripts/commits/master) |  [![coverage report](https://gitlab.com/katyukha/odoo-helper-scripts/badges/master/coverage.svg)](https://gitlab.com/katyukha/odoo-helper-scripts/commits/master)| [![CHANGELOG](https://img.shields.io/badge/CHANGELOG-master-brightgreen.svg)](https://gitlab.com/katyukha/odoo-helper-scripts/blob/master/CHANGELOG.md)              |
| ------------- |:---------------|:--------------|:------------|
| Dev           | [![pipeline status](https://gitlab.com/katyukha/odoo-helper-scripts/badges/dev/pipeline.svg)](https://gitlab.com/katyukha/odoo-helper-scripts/commits/dev) | [![coverage report](https://gitlab.com/katyukha/odoo-helper-scripts/badges/dev/coverage.svg)](https://gitlab.com/katyukha/odoo-helper-scripts/commits/dev) | [![CHANGELOG](https://img.shields.io/badge/CHANGELOG-dev-yellow.svg)](https://gitlab.com/katyukha/odoo-helper-scripts/blob/dev/CHANGELOG.md) |

## Canonical source

The canonical source of odoo-helper-scripts is hosted [GitLab](https://gitlab.com/katyukha/odoo-helper-scripts).

## Features

- Easily manage few instances of odoo that ran on same machine
- High usage of [virtualenv](https://virtualenv.pypa.io/en/stable/) for isolation purpose
- Use [nodeenv](https://pypi.python.org/pypi/nodeenv) to install [node.js](https://nodejs.org/en/), [phantom.js](http://phantomjs.org/), etc in isolated [virtualenv](https://virtualenv.pypa.io/en/stable/)
- Powerful testing capabilities, including support for:
    - python and js code check via [pylint\_odoo](https://pypi.python.org/pypi/pylint-odoo) (which uses [ESLint](https://eslint.org/) to check JS files)
    - python code check via [flake8](https://pypi.python.org/pypi/flake8)
    - styles (*.css*, *.scss*, *.less* files) check via [stylelint](https://stylelint.io/)  (**experimental**)
    - compute test code coverage via [coverage.py](https://coverage.readthedocs.io)
    - Test web tours via [phantom.js](http://phantomjs.org/)
- Easy addons installation
    - Automatiacly resolve and fetch dependencies
        - oca\_dependencies.txt ([sample](https://github.com/OCA/maintainer-quality-tools/blob/master/sample_files/oca_dependencies.txt), [mqt tool code](https://github.com/OCA/maintainer-quality-tools/blob/master/sample_files/oca_dependencies.txt))
        - [requirements.txt](https://pip.readthedocs.io/en/stable/user_guide/#requirements-files)
    - Specific file format to track addon dependencies: [odoo\_requirements.txt](https://katyukha.gitlab.io/odoo-helper-scripts/odoo-requirements-txt/)
    - installation from *git* repositories
    - installation from *Mercurial* repositories (**experimental**)
    - installation of python dependencies from [PyPI](pypi.python.org/pypi) or any [vcs supported by setuptools](https://setuptools.readthedocs.io/en/latest/setuptools.html?highlight=develop%20mode#dependencies-that-aren-t-in-pypi) (automatically process *requirements.txt* files in repository and anddon directories.
    - shortcuts that simplifies fetching addons from [OCA](https://github.com/OCA) or [github](https://github.com)
    - works good with long recursive dependencies.
      One of the reasons for this script collection development was,
      ability to automaticaly install more that 50 addons,
      that depend on each other, and where each addon have it's own git repo.
- Supported odoo versions:
    - *7.0* (some functionality may not work),
    - *8.0*
    - *9.0*
    - *10.0*
    - *11.0*
- OS support:
    - On *Ubuntu* should work nice
    - Also should work on *Debian* based systems, but some troubles may happen with installation of system dependencies.
    - Other linux systems - in most cases should work, but system dependecies must be installed manualy.
- Missed feature? [Fill an issue](https://gitlab.com/katyukha/odoo-helper-scripts/issues/new)


## Documentation

***Note*** Documentaion in this readme, or in other sources, may not be up to date!!!
So use ``--help`` option, which is available for most of commands.

- [Documentation](https://katyukha.gitlab.io/odoo-helper-scripts/)
- [Installation](https://katyukha.gitlab.io/odoo-helper-scripts/installation/)
- [Frequently used commands](https://katyukha.gitlab.io/odoo-helper-scripts/frequently-used-commands/)


## Usage note

This script collection is designed to simplify life of addons developer.
This project ***is not*** designed, to install and configure production ready Odoo instances!
To install Odoo in production read [Odoo official installation doc](https://www.odoo.com/documentation/10.0/setup/install.html) first.
Also, it is possible to manage almost any Odoo intance with this project, if it will be configured right.


## Installation

For full list of installation options look at [installation documentation](https://katyukha.gitlab.io/odoo-helper-scripts/installation/)

*Starting from 0.1.7 release odoo-helper-scripts could be installed as* [.deb packages](https://katyukha.gitlab.io/odoo-helper-scripts/installation#install-as-deb-package)*,
but this feature is still experimental*

To install *odoo-helper-scripts* system-wide do folowing:

```bash
# Install odoo-helper-scripts
wget -O - https://gitlab.com/katyukha/odoo-helper-scripts/raw/master/install-system.bash | sudo bash -s

# Install system dependencies required for odoo-helper-scripts
# NOTE: Works only on debian-based systems
odoo-helper install pre-requirements
```

or more explicit way:

```bash
# Download installation script
wget -O /tmp/odoo-helper-install.bash https://gitlab.com/katyukha/odoo-helper-scripts/raw/master/install-system.bash;

# Install odoo-helper-scripts
sudo bash /tmp/odoo-helper-install.bash;

#  Intall system pre-requirements for odoo-helper-scripts
# NOTE: Works only on debian-based systems
odoo-helper install pre-requirements
```

## Test your OS support

It is possible to run basic tests via docker.
For this task, odoo-helper-scripts repo contains script `scripts/run_docker_test.bash`.
Run `bash scripts/run_docker_test.bash --help` to see all available options for that script.

For example to test, how odoo-helper-scripts will work on debian:stretch, do following:

```bash
cd $ODOO_HELPER_ROOT
bash scripts/run_docker_test.bash --docker-ti --docker-image debian:stretch
```


## Usage

And after install you will have available folowing scripts in your path:

- odoo-install
- odoo-helper

Each script have `-h` or `--help` option which display most relevant information
about script and all possible options and subcommands of script

Also there are some aliases for common commands:

- odoo-helper-addons
- odoo-helper-db
- odoo-helper-fetch
- odoo-helper-log
- odoo-helper-restart
- odoo-helper-server
- odoo-helper-test

For more info look at [documentation](https://katyukha.gitlab.io/odoo-helper-scripts/). (currently documentation status is *work-in-progress*).
Also look at [Frequently used commands](https://katyukha.gitlab.io/odoo-helper-scripts/frequently-used-commands/)

Also look at [odoo-helper-scripts tests](./tests/test.bash) to get complete usage example (look for *Start test* comment).

## Support

Have you any quetions? Just [fill an issue](https://gitlab.com/katyukha/odoo-helper-scripts/issues/new) or [send email](mailto:incoming+katyukha/odoo-helper-scripts@incoming.gitlab.com)
