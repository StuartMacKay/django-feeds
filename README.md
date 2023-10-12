# Django Feeds

Django Feeds is an aggregator for entries from RSS and Atom feeds.

## Quick Start

Download and install the app:

```pip istall django-rss-feeds```

Add the app to Django:

```python
INSTALLED_APPS = [
    ...,
    "tagulous",
    "feeds.apps.Config",
]
```

Run the migrations:

```python manage.py migrate```

## Demo

The project contains demonstration Django application, with celery, that 
lets you see how it all works. The demo site aggregates the feeds and 
publishes the Articles, grouped by date, with each page showing the Articles 
for the past 7 days. Links on each entry allow you navigate to ListViews 
for each Source, Author or Tag.

```shell
git clone git@github.com:StuartMacKay/django-feeds.git
docker-compose up
```

Next run a shell on the web service, so you can create an admin account, 
log in and add a Source and a Feed.

```shell
docker-compose exec web bash
./manage.py createsuperuser
```

Now log into the Django Admin. In the Feeds section, add a Source and a Feed 
for that Source, for example, https://news.ycombinator.com/rss. Now in the 
Feed changelist, select the Feed you just added and run the 'Load selected 
feeds' action. Voila, you now have a set of Articles created from the feed.

## Settings

`FEEDS_TASK_SCHEDULE`, default "0 * * * *". A crontab string that 
set when a Celery task runs to check whether any Feeds are scheduled
to load.

`FEEDS_LOAD_SCHEDULE`, default "0 * * * *". A crontab string that sets 
when Feeds is scheduled to be loaded. This can be overridden on Feeds 
individually.

`FEEDS_USER_AGENT`, the User-Agent string that identifies who is requesting 
the feed. Some sites won't work without this set. In any case it's always 
good manners to identify yourself.

`FEEDS_FILTER_TITLE`, default None. Python path to a function that will be 
dynamically imported to process the title of an entry before it is used to 
create or update an Article.

`FEEDS_FILTER_AUTHORS`, default None. Python path to a function that will be 
dynamically imported to process the list of authors for an entry before it is 
used to create or update an Article.

`FEEDS_FILTER_TAGS`, default None. Python path to a function that will be 
dynamically imported to process the list of tags for an entry before it is 
used to create or update an Article.

## Contributing

This app was written with a single use-case - republishing a list of links 
to posts from other blogs. It performs that function well, but, as usual,
there is always room for improvement. Feedback, feature requests, bug 
reports, improvements to the documentation are all welcome. Read the TODO
list for things that need work and the HowTos in the docs directory to 
get started.
