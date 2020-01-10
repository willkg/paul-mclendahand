================
paul-mclendahand
================

paul-mclendahand combines pull requests into a single branch.

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
