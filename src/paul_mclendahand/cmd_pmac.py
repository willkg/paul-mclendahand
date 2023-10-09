# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import configparser
import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen

import click
from rich import box
from rich.console import Console
from rich.table import Table

from paul_mclendahand import __version__


GITHUB_API = "https://api.github.com/"

DEFAULT_CONFIG = {
    "github_user": "",
    "github_project": "",
    "main_branch": "",
    "github_api_token": "",
}

OPTIONAL_CONFIG = ["github_api_token"]

COMMIT_MESSAGE_FILE = "CMTMSG"


def get_config():
    """Generates configuration.

    This tries to pull configuration from:

    1. the ``[tool.paul-mclendahand]`` table from a ``pyproject.toml`` file, OR
    2. the ``[tool:paul-mclendahand]`` section from a ``setup.cfg`` file

    If neither exist, then it uses defaults.

    :returns: configuration dict

    """
    # Start with defaults
    my_config = dict(DEFAULT_CONFIG)

    # Override with values from pyproject.toml OR setup.cfg
    if os.path.exists("pyproject.toml"):
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib

        with open("pyproject.toml", "rb") as fp:
            data = tomllib.load(fp)

        config_data = data.get("tool", {}).get("paul-mclendahand", {})
        if config_data:
            for key in my_config.keys():
                if key in config_data:
                    if key == "github_api_token":
                        # We don't let people set the api token in the setup.cfg
                        # file which gets checked in
                        raise click.ClickException(
                            f"You shouldn't set {key} in pyproject.toml."
                        )

                    my_config[key] = config_data[key]

    elif os.path.exists("setup.cfg"):
        config = configparser.ConfigParser()
        config.read("setup.cfg")

        if "tool:paul-mclendahand" in config:
            config = config["tool:paul-mclendahand"]
            for key in my_config.keys():
                if key in config:
                    if key == "github_api_token":
                        # We don't let people set the api token in the setup.cfg
                        # file which gets checked in
                        raise click.ClickException(
                            f"You shouldn't set {key} in setup.cfg."
                        )
                    my_config[key] = config[key]

    # Override with environment variables
    for key in my_config.keys():
        if "PMAC_%s" % key.upper() in os.environ:
            my_config[key] = os.environ["PMAC_%s" % key.upper()]

    # Check for missing configuration
    for key, val in my_config.items():
        if key not in OPTIONAL_CONFIG and not val:
            raise click.ClickException(f"Configuration '{key}' not set.")

    return my_config


def fetch(url, is_json=True, api_token=None):
    """Fetch data from a url

    This raises URLError on HTTP request errors. It also raises JSONDecode
    errors if it's not valid JSON.

    """
    headers = {}
    if api_token:
        headers["Authorization"] = f"token {api_token}"
    req = Request(url=url, headers=headers)
    fp = urlopen(req)
    data = fp.read()
    if is_json:
        return json.loads(data)
    return data


def run_cmd(args, stdin=None, check=True):
    params = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "check": check}

    if stdin is not None:
        params["input"] = stdin

    return subprocess.run(args, **params)


def is_am_in_progress():
    """Returns whether or not we're in an am session

    :returns: True if in "git am" session; False otherwise

    """
    # Get the path for rebase-apply directory
    ret = run_cmd(["git", "rev-parse", "--git-path", "rebase-apply"])
    path = ret.stdout.decode("utf-8").strip()
    return os.path.exists(path)


@click.group(name="pmac")
@click.version_option(version=__version__)
def pmac_cli():
    """GitHub pull request combiner tool.

    pmac uses a "[tool:paul-mclendahand]" section in setup.cfg to set configuration
    variables. You can override these using PMAC_VARNAME environment variables.

    Additionally, if you want to use a GitHub personal access token, you need to
    provide the "PMAC_GITHUB_API_TOKEN" variable in the environment set to the
    token.

    For issues, see: https://github.com/willkg/paul-mclendahand/issues

    """
    pass


@pmac_cli.command(name="add")
@click.argument("pr", required=True, nargs=-1)
@click.pass_context
def pmac_add(ctx, pr):
    """Combine specified PRs into this branch."""
    console = Console()

    config = get_config()

    github_user = config["github_user"]
    github_project = config["github_project"]
    main_branch = config["main_branch"]
    api_token = config["github_api_token"]

    for pr_index, this_pr in enumerate(pr):
        console.print(
            f"[green]pmac: Working on pr {this_pr} ({pr_index+1}/{len(pr)})[/green]"
        )

        # Get the commits for that PR
        url = (
            f"{GITHUB_API}repos/{github_user}/{github_project}/pulls/{this_pr}/commits"
        )
        # This returns a list of commit objects
        resp = fetch(url, api_token=api_token)
        num_commits = len(resp)

        for commit_index, commit in enumerate(resp):
            commit_sha = commit["sha"]
            commit_html_url = commit["html_url"]

            console.print(
                f"[green]pmac: Applying {commit_sha} from {this_pr} "
                + f"({commit_index + 1}/{num_commits}) ...[/green]"
            )

            # Get the patch and apply with "git am"
            patch = fetch(commit_html_url + ".patch", is_json=False)
            proc = run_cmd(["git", "am", "--3way"], stdin=patch, check=False)
            stdout = proc.stdout.decode("utf-8").strip()
            stderr = proc.stderr.decode("utf-8").strip()

            if stdout:
                for line in stdout.splitlines():
                    console.print(f"git am (out): {line}")
            if stderr:
                for line in stderr.splitlines():
                    console.print(f"git am (err): {line}")

            # FIXME(willkg): This only works for when the commit didn't make
            # any changes. It doesn't work when there are two commits that do
            # conflicting things and the user ends up doing "git am --skip" for
            # one of them. In that scenario, the commit was not applied, but
            # pmac doesn't know, so it then adds a from PR thing.
            if "No changes" in stdout:
                console.print(
                    f"[green]pmac: PR {this_pr} looks like it's already been applied. "
                    + "Skipping...[/green]"
                )
                console.print()
                continue

            if proc.returncode != 0:
                unresolved = True

                while unresolved:
                    console.print(
                        f"[red]pmac: Conflict hit when applying {commit_sha} from {this_pr}.[/red]"
                    )
                    ret = run_cmd(["git", "status"])
                    console.print(ret.stdout.decode("utf-8"))
                    console.print(
                        "[red]pmac: Please fix the above issue in another shell. When you are done, hit "
                        + "ENTER to continue.[/red]"
                    )
                    input()

                    if not is_am_in_progress():
                        unresolved = False

            # Grab the commit message for that last commit
            ret = run_cmd(["git", "log", "--format=%B", "-n", "1", "HEAD"])
            data = ret.stdout.decode("utf-8")

            data = data.splitlines()

            # If this line already has a "{from PR #xyz)" at the end, then the
            # user probably did "git am --skip" and we don't want to add another one.
            firstline = data[0].strip()
            if "(from PR #" in firstline:
                console.print(
                    '[green]pmac: Looks like you might have done "git am --skip", so I won\'t '
                    + "adjust the commit summary.[/green]"
                )
                continue

            data[0] = f"{firstline} (from PR #{this_pr})"
            try:
                with open(COMMIT_MESSAGE_FILE, "w") as fp:
                    fp.write("\n".join(data))

                run_cmd(["git", "commit", "--amend", "--file=%s" % COMMIT_MESSAGE_FILE])
            finally:
                # Delete the file if it's there
                if os.path.exists(COMMIT_MESSAGE_FILE):
                    os.remove(COMMIT_MESSAGE_FILE)

            console.print("")

    ret = run_cmd(["git", "log", "--oneline", "%s..HEAD" % main_branch])
    stdout = ret.stdout.decode("utf-8").strip()
    if stdout:
        console.print(f"[green]pmac: Log since {main_branch} tip ...[/green]")
        console.print(ret.stdout.decode("utf-8").strip())
    else:
        console.print("[green]pmac: No changes.[/green]")

    console.print("[green]pmac: Done.[/green]")


@pmac_cli.command(name="prmsg")
@click.pass_context
def pmac_prmsg(ctx):
    """Print out summary of commits suitable for a PR msg."""
    console = Console()

    config = get_config()

    main_branch = config["main_branch"]
    ret = run_cmd(["git", "log", "--oneline", "%s..HEAD" % main_branch])

    stdout = ret.stdout.decode("utf-8").splitlines()

    if not stdout:
        console.print(
            'There are no new commits in this branch. Use "pmac add" to add some.'
        )
        ctx.exit(1)

    console.print(
        "[green]pmac: Copy and paste this text and use it as the PR "
        + "description.[/green]"
    )
    console.print()
    console.print("Update dependencies. This covers:")
    console.print()
    for line in stdout:
        # Remove any whitespace and drop the commit sha at the beginning
        line = line.strip().split(" ", 1)[1]
        console.print(f"* {line}")


COLOR_TO_NAME = {
    "B60205": "white on red",
    "E99695": "white on red",
    "D93F0B": "white on red",
    "F9D0C4": "white on red",
    "FBCA04": "black on yellow",
    "FEF2C0": "black on bright_yellow",
    "0E8A16": "white on green",
    "C2E0C6": "white on green",
    "168700": "white on green",
    "006B75": "white on cyan",
    "BFDADC": "black on bright_cyan",
    "21CEFF": "black on bright_cyan",
    "1D76DB": "white on blue",
    "C5DEF5": "black on bright_blue",
    "0052CC": "white on blue",
    "0366D6": "white on blue",
    "2B67C6": "white on blue",
    "BFD4F2": "black on bright_blue",
    "5319E7": "white on magenta",
    # FIXME(willkg): there are probably other colors
}


def style_label(label_data):
    label_color = label_data.get("color", "").upper()
    style = COLOR_TO_NAME.get(label_color, "bold")
    return f"[{style}]{label_data['name']}[/{style}]"


@pmac_cli.command(name="listprs")
@click.option("--labels/--no-labels", "show_labels", default=False, help="List labels")
@click.option(
    "--format", "format_", default="table", type=click.Choice(["table", "tab"])
)
@click.pass_context
def pmac_listprs(ctx, show_labels, format_):
    """List available PRs for the project."""
    console = Console()

    if not console.is_terminal:
        # If stdout is not a terminal, then use tab by default. This is
        # more script-friendly.
        format_ = "tab"

    config = get_config()

    github_user = config["github_user"]
    github_project = config["github_project"]
    main_branch = config["main_branch"]
    api_token = config["github_api_token"]

    url = f"{GITHUB_API}repos/{github_user}/{github_project}/pulls?base={main_branch}"
    resp = fetch(url, api_token=api_token)

    if format_ == "table":
        table = Table(box=box.MARKDOWN)
        table.add_column("pr", justify="left")
        table.add_column("title", justify="left")
        if show_labels:
            table.add_column("labels", justify="left")

        for pr in resp:
            row = [str(pr["number"]), pr["title"]]
            if show_labels:
                labels = sorted(pr["labels"], key=lambda label: label["name"])
                row.append(" ".join([style_label(label) for label in labels]))

            table.add_row(*row)

        console.print(table)

    elif format_ == "tab":
        for pr in resp:
            row = [str(pr["number"]), pr["title"]]
            if show_labels:
                labels = sorted(pr["labels"], key=lambda label: label["name"])
                row.append(" ".join([style_label(label) for label in labels]))
            console.print("\t".join(row))
