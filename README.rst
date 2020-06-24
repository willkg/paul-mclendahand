================
paul-mclendahand
================

Tool for combining GitHub pull requests.

:Code:          https://github.com/willkg/paul-mclendahand
:Issues:        https://github.com/willkg/paul-mclendahand/issues
:License:       MPL v2
:Documentation: this README


Install
=======


With `pipx <https://pypi.org/project/pipx/>`_::

    pipx install paul-mclendahand

With pip from PyPI::

    pip install paul-mclendahand
    
With pip from GitHub main branch::

    pip install https://github.com/willkg/paul-mclendahand/archive/main.zip

    
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

pmac needs to know the GitHub user and GitHub project.

You can set configuration in the ``setup.cfg`` file::

   [tool:paul-mclendahand]
   github_user=user
   github_project=project
   git_remote=git-remote-name
   main_branch=git-main-branch-name

You can override the ``setup.cfg`` variables with environment variables::

   PMAC_GITHUB_USER=user
   PMAC_GITHUB_PROJECT=project
   PMAC_GIT_REMOTE=git-remote-name
   PMAC_MAIN_BRANCH=git-main-branch-name

You can also pass the git remote on the command line using the ``--git_remote``
argument.

If you don't specify a remote, then pmac will guess it using a highly
sophisticated deterministic stochastic rainbow chairs algorithm.


Using pmac
----------

After you've configured git, then you can use ``pmac`` like this:

1. Create a new branch::

       git checkout <MAIN-BRANCH>
       git checkout -b update-prs

2. List open PRs::

       pmac listprs

3. Combine some pull requests into it::

       pmac add 5100 5101 5102

   Use the same pull requests numbers as on GitHub.

   If you hit a cherry-pick conflict, ``pmac`` will tell you. You can edit
   the file in another terminal to manually resolve the conflict. Then do::

       git add FILE
       git commit

   After that, you can continue with ``pmac``.

4. When you're done, push the branch to GitHub and create a pull request.

   ``pmac`` can help with the PR description::

       pmac prmsg


Why does this project exist?
============================

Two main reasons.

First, GitHub doesn't support combining pull requests. There is a forum post
about it here:
https://github.community/t5/How-to-use-Git-and-GitHub/Feature-Request-combine-pull-requests/td-p/27660

Second, dependabot (also owned by GitHub) doesn't support grouping dependency
updates into a single pull request. If you have 50 dependency updates, it
creates 50 pull requests. I have a lot of projects and lack of grouping
updates makes monthly maintenance miserable. There's an issue for this:
https://github.com/dependabot/feedback/issues/5
