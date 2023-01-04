History
=======

3.0.0 (January 4th, 2023)
-------------------------

NEW FEATURES:

* Add support for Python 3.11. (#32)

* Add ``--labels`` flag to ``listprs`` to show pull request labels. (#29)


OTHER THINGS:

* Rewrote command line interface using `click
  <https://pypi.org/project/click/>`__ and `rich
  <https://pypi.org/project/rich/>`__. Output is a lot nicer. Instructions for
  handling conflicts when combining PRs are clearer. (#36)

* Add command-line help to README. (#35)


2.1.0 (February 7th, 2022)
--------------------------

OTHER THINGS:

* Better handling for ``git am`` conflicts. (#22)

* Better handling for when no changes were applied. ``pmac add`` won't adjust
  the top-most commit. (#24)


2.0.0 (July 15th, 2021)
-----------------------

NEW FEATURES:

* Rewrote how ``pmac add`` works. It no longer needs you to edit your
  ``.git/config`` file. It now uses the GitHub API to fetch the commits for the
  PRs being added.

  You can remove ``git_remote`` related configuration. It's no longer used.

  You should use GitHub to create an API token and then use that as the value
  for the ``PMAC_GITHUB_API_TOKEN``. This will fix issues with rate-limiting.

  (#14)

OTHER THINGS:

* Switched to a ``src/`` based project layout and moved requirements into
  ``setup.py`` file.


1.2.0 (June 12th, 2020)
-----------------------

NEW FEATURES:

* Added a ``PMAC_MAIN_BRANCH`` environment variable and ``main_branch`` configuration
  option which specify the name of the main branch. (#12)


1.1.0 (April 7th, 2020)
-----------------------

NEW FEATURES:

* Added a ``--git_remote`` argument, ``PMAC_GIT_REMOTE`` environment variable,
  and ``git_remote`` configuration option which, when specified, will cause
  pmac to use that as the remote name and not guess. (#10)


OTHER THINGS:

* Added a Makefile because that's how I roll.

* Tweaked ``pmac --help`` so it shows the version and release date and link to
  issue tracker.

* Cleaned up README.

* Made a peanut butter pie and ate it.


1.0.0 (January 14, 2020)
------------------------

* Initial writing.
