# Django App Project

[![Build Status](https://img.shields.io/github/actions/workflow/status/StuartMacKay/django-app-template/ci.yml?branch=master)](https://github.com/StuartMacKay/django-app-template/actions/workflows/ci.yml?query=branch%3Amaster)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Features

* Development with [black](https://github.com/psf/black) so everybody gets the code formatting rules they deserve
* Development with [flake8](https://flake8.pycqa.org/en/latest/) so people using ed get syntax checking
* Development with [isort](https://pycqa.github.io/isort/) for automatically sorting imports
* Development with [mypy](https://mypy-lang.org/) for type-hinting to catch errors
* Testing with [pytest](https://docs.pytest.org/), [FactoryBoy](https://factoryboy.readthedocs.io/en/stable/) and [tox](https://tox.wiki/en/latest/)
* Manage versions with [bump2version](https://pypi.org/project/bump2version/) - for semantic version numbers
* Manage dependency versions with [pip-tools](https://github.com/jazzband/pip-tools)
* Manage dependency upgrades with [pip-upgrade](https://github.com/simion/pip-upgrader)

## Quick start

First, download and unzip the project files in the directory of your choice.
Then rename the project to something more useful:
```shell
mv django-app-template django-myapp
```

Change to the project directory and start setting things up:
```shell
cd django-myapp
```

First, build the virtualenv and install all the dependencies. This will 
also build the library:
```shell
make install
```

Now run the demo site:
```shell
make demo
```


Run the database migrations:
```shell
./manage.py migrate
```

Run the tests:
```shell
make tests
```

Run the django server:
```shell
./manage.py runserver
```

Open a browser and visit http://localhost:8000 and, voila, we have a working
site. Well cover the deployment later.

Almost all steps used the project Makefile. That's great if you're running 
Linux with GNU Make and not much fun if you're not. All is not lost, however. 
All the Makefile's targets contain only one or two commands, so even if you 
are running Windows you should still be able to get the site running without 
too much effort.
