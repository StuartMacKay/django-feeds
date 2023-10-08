# Get Started With Development

This How-To shows you to install everything for development, run the tests
and make sure the demo site is working. 

The assumption is that you are working in a Linux environment with PostgreSQL 
and RabbitMQ installed natively. If you would rather not install these, then 
see below, where various options are listed.

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

## Setting environment variables

Whether you create a virtualenv or use docker the demo site runs out of the 
box. If you need to change the configuration the `env.example` file contains 
a complete list of variables that are used to configure the docker containers
or are used for Django settings.

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
docker-compose up postgres rabbitmq
```

If you use an IDE that supports docker then just run everything in containers:

```shell
docker-compose up
```

## Using a different database

The configuration uses the default `postgres` database. If you want to keep 
the databases for different projects separate then run the following commands:

```shell
sudo -u postgres psql
```

```shell
postgres=# create database feeds;
postgres=# create user feeds with createdb encrypted password 'feeds';
postgres=# grant all privileges on database feeds to feeds;
postgres=# \q
```

There's no need to create another user, you could still use the default 
`postgres` account. You will also need to change the following environment
variables in an `.env` file:

```shell
POSTGRES_USER=feeds
POSTGRES_PASSWORD=feeds
POSTGRES_DB=feeds
```

If you use postgreSQL's command line tools for managing the database then 
remember to also change the following:

```shell
PGDATABASE=feeds
```

## Using a different RabbitMQ account and vhost

For the same reasons for keeping the project database separate you may 
also want to create a separate account and vhost for RabbitMQ.

```shell
sudo rabbitmqctl add_user feeds feeds
sudo rabbitmqctl add_vhost feeds
sudo rabbitmqctl set_permissions -p feeds feeds ".*" ".*" ".*"
```

You will need to set the environment variables in `.env` so celery
can connect to RabbitMQ:

```shell
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
```
