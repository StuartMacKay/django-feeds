# TODO

* Improve type hints.

* Django is currently pinned to 3.2 as the autocomplete in the Admin does not 
  work with the latest version, 4.1.7 (Sept 2023). It is not clear whether this
  is an error in Django or whether it is a side-effect of using django-tagulous.

* The categories template filter, which returns a list of Categories on an Article
  with a given prefix should either be more robust or intolerant if used incorrectly,
  i.e. return an empty list or raise an exception. It currently works with Feeds
  but there is probably no need for it to do.

* Read through https://news.ycombinator.com/item?id=35684220 and fix any incompetence
  on the models.

* Allow the path to functions to used process titles and filter to be defined 
  in the settings.
