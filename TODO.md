# TODO

The code runs and runs well. It has been in production for almost two
years, so it is rather polished. It was factored out of the 
[Voices for Independence](https://www.voices.scot) web site with s small
number of changes and is now being repackaged to make it reusable in other
projects we have in mind. 

* replace the original bootstrap css classes with semantic names, so it 
  can be restyled easily.

* move 'business logic' out of the views and out of the querysets into a  
  services layer - an internal API. That way you're not forced
  to subclass the views, and you can easily write your own.

* Add more blocks to the templates and create more snippets so again you
  can easily replace what is provided in the app.

* Also load the feeds using cron, so you are not forced to use celery.

* Add a REST API - at some point.
