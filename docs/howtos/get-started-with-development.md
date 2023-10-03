# Get Started With Development

This How-To shows you to install everything for development, run the tests
and make sure the demo site is working. 

The assumption is that you are working in a Linux environment with PostgreSQL 
and RabbitMQ installed natively. If you would rather not install these, then 
see below, where various options are listed.

If you encounter any problems, please check the Troubleshooting section below,
for a solution.

Create a database account:

```shell
sudo -u postgres psql
```

```shell
postgres=# create database feeds;
postgres=# create user feeds with createdb encrypted password 'feeds';
postgres=# grant all privileges on database feeds to feeds;
postgres=# \q
```

If you want to use another account, be sure to change the DATABASES setting
in `demo/settings.py` to match.

Create a message broker account:

```shell
sudo rabbitmqctl add_user feeds feeds
sudo rabbitmqctl add_vhost feeds
sudo rabbitmqctl set_permissions -p feeds feeds ".*" ".*" ".*"
```

Checkout the repository:

```shell
git clone git@github.com:StuartMacKay/django-feeds.git
cd django-feeds
```

If you want to contribute to the project and submit a Pull Request, then fork
the project first and checkout your version of the repository instead.

Create the virtual environment:

```shell
python -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install pip-tools
pip-sync requirements/dev.txt
```

Set environment variables used by Django:

```shell
source .env
```

Run the tests:

```shell
pytest src/feeds/tests
pytest demo/tests
```

Run the demo:

```shell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Using direnv

If you install [direnv](https://direnv.net/), then whenever you cd to the project
directory you can automatically activate the virtualenv and set the environment 
variables needed by the project.

The project contains a `.envrc` configuration file so once direnv is installed all 
you have to do is whitelist the project directory:

```shell
cd django-feeds
direnv allow .
```

## Using Make 

The project includes a Makefile which includes targets to make development 
easier. All the steps described above that are needed to create the virtualenv 
and install the dependencies is performed by running:

```shell
make install
```

## Using Sqlite

If you just want to kick the tyres and not go to all the trouble of installing 
PostgreSQL, then everything works just fine with SQLite. Change the Django
DATABASES setting to the following, run the migrations, etc.

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(ROOT_DIR, "db.sqlite3"),
    }
}
```

## Using Docker

The `docker-compose.yml` file in the project root directory defines services for
all the components: db, celery, web, etc. That way you can use a mix of services
running natively or in containers:

```shell
docker-compose up db broker
```

If you use an IDE that supports docker then just run everything in containers:

```shell
docker-compose up
```
