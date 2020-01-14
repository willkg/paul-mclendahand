================
paul-mclendahand
================

Tools for combining GitHub pull requests.

:Code:          https://github.com/willkg/paul-mclendahand
:Issues:        https://github.com/willkg/paul-mclendahand/issues
:License:       MPL v2
:Documentation: this README


Install
=======

Install from github::

    pip install https://github.com/willkg/paul-mclendahand/archive/master.zip

Install from PyPI:

    TBD
    
    
Quick start
===========

Configure git to fetch pull request references
----------------------------------------------

First, you need to have git configured to fetch pull request references. I have
an additional ``fetch`` line in my remote for github.com. For example,
this is what I have for socorro::

    [remote "upstream"]
        url = git@github.com:mozilla-services/socorro.git
        fetch = +refs/heads/*:refs/remotes/upstream/*
        fetch = +refs/pull/*/head:refs/remotes/upstream/pr/*

The line you need to add is the last one. Make sure to use the right remote::

        fetch = +refs/pull/*/head:refs/remotes/upstream/pr/*
                                               ^^^^^^^^
                                               use your remote name here

After adding that, when you do ``git pull``, it'll pull down all the references
for pull requests. They'll be available as ``upstream/pr/PRNUM``.


Configure pmac
--------------

pmac needs to know the GitHub user and GitHub project. You can do that using
environment variables::

   PMAC_GITHUB_USER=user
   PMAC_GITHUB_PROJECT=project

or by adding a section to the ``setup.cfg`` file::

   [tool:paul-mclendahand]
   github_user=user
   github_project=project


Using pmac
----------

After you've configured git, then you can use ``pmac`` like this:

1. Create a new branch::

       git checkout master
       git checkout -b update-prs

2. Combine some pull requests into it::

       pmac add 5100 5101 5102

   Use the same pull requests numbers as on GitHub.

   If you hit a cherry-pick conflict, ``pmac`` will tell you. You can edit
   the file in another terminal, then do::

       git add FILE
       git commit

   After that, you can continue with ``pmac``.

3. When you're done, push the branch to GitHub and then do::

       pmac prmsg

   to get a pull request message.


Why does this project exist?
============================

Two main reasons.

First, GitHub doesn't support combining pull requests. There is a forum post
about it here:
https://github.community/t5/How-to-use-Git-and-GitHub/Feature-Request-combine-pull-requests/td-p/27660

Second, dependabot (also owned by GitHub) doesn't support grouping dependency
updates into a single pull request. If you have 50 dependency updates, it
creates 50 pull requests. I have a lot of projects and that makes monthly
maintenance miserable. There's an issue for this:
https://github.com/dependabot/feedback/issues/5
