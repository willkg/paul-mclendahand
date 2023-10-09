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

(Recommended) With `pipx <https://pypi.org/project/pipx/>`_::

    pipx install paul-mclendahand

With pip from PyPI::

    pip install paul-mclendahand
    
With pip from GitHub main branch::

    pip install https://github.com/willkg/paul-mclendahand/archive/main.zip

With pip from a clone of the repository with dev dependencies::

    pip install -r requirements-dev.txt

    
Quick start
===========

Configure pmac
--------------

pmac needs to know the GitHub user and GitHub project.

You can set configuration in the ``pyproject.toml`` file::

   [tool.paul-mclendahand]
   github_user = "user"
   github_project = "project"
   main_branch = "git-main-branch-name"

Or you can set configuration in the ``setup.cfg`` file::

   [tool:paul-mclendahand]
   github_user=user
   github_project=project
   main_branch=git-main-branch-name

You can override the configuration variables with environment variables::

   PMAC_GITHUB_USER=user
   PMAC_GITHUB_PROJECT=project
   PMAC_MAIN_BRANCH=git-main-branch-name

**Optional**

You can also use a GitHub personal access token. You set it in the
``PMAC_GITHUB_API_TOKEN`` environment variable.

For example::

    PMAC_GITHUB_API_TOKEN=abcdef0000000000000000000000000000000000 pmac listprs

.. Note::

   If you find pmac stops working because it's getting rate-limited by GitHub,
   you should use a personal access token.


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

   Internally, ``pmac`` uses ``git am`` to apply commits from pull requests. If
   you hit a ``git am`` conflict, ``pmac`` will tell you. You can edit the file
   in another terminal to manually resolve the conflict. Then do::

       git add FILE
       git commit
       git am --continue

   After that, you can continue with ``pmac``.

4. When you're done, push the branch to GitHub and create a pull request.

   ``pmac`` can help with the PR description::

       pmac prmsg


pmac
----

.. [[[cog
    from paul_mclendahand.cmd_pmac import pmac_cli
    from click.testing import CliRunner
    result = CliRunner().invoke(pmac_cli, ["--help"])
    cog.out("\n")
    cog.out("::\n\n")
    for line in result.output.splitlines():
        if line.strip():
            cog.out(f"   {line}\n")
        else:
            cog.out("\n")
    cog.out("\n")
   ]]]

::

   Usage: pmac [OPTIONS] COMMAND [ARGS]...

     GitHub pull request combiner tool.

     pmac uses a "[tool:paul-mclendahand]" section in setup.cfg to set
     configuration variables. You can override these using PMAC_VARNAME environment
     variables.

     Additionally, if you want to use a GitHub personal access token, you need to
     provide the "PMAC_GITHUB_API_TOKEN" variable in the environment set to the
     token.

     For issues, see: https://github.com/willkg/paul-mclendahand/issues

   Options:
     --version  Show the version and exit.
     --help     Show this message and exit.

   Commands:
     add      Combine specified PRs into this branch.
     listprs  List available PRs for the project.
     prmsg    Print out summary of commits suitable for a PR msg.

.. [[[end]]]


pmac listprs
------------

.. [[[cog
    from paul_mclendahand.cmd_pmac import pmac_cli
    from click.testing import CliRunner
    result = CliRunner().invoke(pmac_cli, ["listprs", "--help"])
    cog.out("\n")
    cog.out("::\n\n")
    for line in result.output.splitlines():
        if line.strip():
            cog.out(f"   {line}\n")
        else:
            cog.out("\n")
    cog.out("\n")
   ]]]

::

   Usage: pmac listprs [OPTIONS]

     List available PRs for the project.

   Options:
     --labels / --no-labels  List labels
     --format [table|tab]
     --help                  Show this message and exit.

.. [[[end]]]


pmac add
--------

.. [[[cog
    from paul_mclendahand.cmd_pmac import pmac_cli
    from click.testing import CliRunner
    result = CliRunner().invoke(pmac_cli, ["add", "--help"])
    cog.out("\n")
    cog.out("::\n\n")
    for line in result.output.splitlines():
        if line.strip():
            cog.out(f"   {line}\n")
        else:
            cog.out("\n")
    cog.out("\n")
   ]]]

::

   Usage: pmac add [OPTIONS] PR...

     Combine specified PRs into this branch.

   Options:
     --help  Show this message and exit.

.. [[[end]]]


pmac prmsg
----------

.. [[[cog
    from paul_mclendahand.cmd_pmac import pmac_cli
    from click.testing import CliRunner
    result = CliRunner().invoke(pmac_cli, ["prmsg", "--help"])
    cog.out("\n")
    cog.out("::\n\n")
    for line in result.output.splitlines():
        if line.strip():
            cog.out(f"   {line}\n")
        else:
            cog.out("\n")
    cog.out("\n")
   ]]]

::

   Usage: pmac prmsg [OPTIONS]

     Print out summary of commits suitable for a PR msg.

   Options:
     --help  Show this message and exit.

.. [[[end]]]


Why does this project exist?
============================

Two main reasons.

First, GitHub doesn't support combining pull requests. There is a forum post
about it here:
https://github.community/t/feature-request-combine-pull-requests/2250

Second, dependabot (also owned by GitHub) doesn't support grouping dependency
updates into a single pull request. If you have 50 dependency updates, it
creates 50 pull requests (sometimes more!). I have a lot of projects and lack
of grouping updates makes monthly maintenance miserable. There's an issue for
this:
https://github.com/dependabot/dependabot-core/issues/1190
