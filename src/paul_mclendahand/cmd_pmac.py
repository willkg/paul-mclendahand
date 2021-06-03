# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import configparser
import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen

from paul_mclendahand import __releasedate__, __version__

HELP_TEXT = """\
GitHub pull request combiner tool.

pmac uses a "[tool:paul-mclendahand]" section in setup.cfg to set configuration
variables. You can override these using PMAC_VARNAME environment variables.

Additionally, if you want to use a GitHub personal access token, you need to
provide the "PMAC_GITHUB_API_TOKEN" variable in the environment set to the
token.

See https://github.com/willkg/paul-mclendahand for details.
"""

EPILOG_TEXT = f"""\
For issues, see: https://github.com/willkg/paul-mclendahand/issues

Version: {__version__} ({__releasedate__})
"""

GITHUB_API = "https://api.github.com/"

DEFAULT_CONFIG = {
    "github_user": "",
    "github_project": "",
    "main_branch": "",
    "github_api_token": "",
}

OPTIONAL_CONFIG = ["github_api_token"]

COMMIT_MESSAGE_FILE = "CMTMSG"


def get_config(args):
    """Generates configuration.

    This tries to pull from the ``[tool:paul-mclendahand]`` section of a
    ``setup.cfg`` in the working directory. If that doesn't exist, then it uses
    defaults.

    :returns: configuration dict

    """
    # Start with defaults
    my_config = dict(DEFAULT_CONFIG)

    # Override with values from config file
    if os.path.exists("setup.cfg"):
        config = configparser.ConfigParser()
        config.read("setup.cfg")

        if "tool:paul-mclendahand" in config:
            config = config["tool:paul-mclendahand"]
            for key in my_config.keys():
                if key == "github_api_token":
                    # We don't let people set the api token in the setup.cfg
                    # file which gets checked in
                    continue
                my_config[key] = config.get(key, "")

    # Override with environment variables
    for key in my_config.keys():
        if "PMAC_%s" % key.upper() in os.environ:
            my_config[key] = os.environ["PMAC_%s" % key.upper()]

    # Override with command line arguments
    for key in my_config.keys():
        if getattr(args, key, ""):
            my_config[key] = getattr(args, key)

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


def subcommand_add(config, args):
    prs = args.pr

    github_user = config["github_user"]
    github_project = config["github_project"]
    main_branch = config["main_branch"]
    api_token = config["github_api_token"]

    for pr_index, pr in enumerate(prs):
        print(">>> Working on pr %s (%s/%s)..." % (pr, pr_index + 1, len(prs)))

        # Get the commits for that PR
        url = f"{GITHUB_API}repos/{github_user}/{github_project}/pulls/{pr}/commits"
        # This returns a list of commit objects
        resp = fetch(url, api_token=api_token)
        num_commits = len(resp)

        for commit_index, commit in enumerate(resp):
            commit_sha = commit["sha"]
            commit_html_url = commit["html_url"]

            print(
                f">>> Applying {commit_sha} from {pr} ({commit_index + 1}/{num_commits}) ..."
            )

            # Get the patch and apply with "git am"
            patch = fetch(commit_html_url + ".patch", is_json=False)
            proc = run_cmd(["git", "am"], stdin=patch)
            stdout = proc.stdout.decode("utf-8").strip()
            stderr = proc.stderr.decode("utf-8").strip()

            if stdout:
                print(stdout)
            if stderr:
                print(stderr)

            if proc.returncode != 0:
                print(f">>> Conflict hit when applying {commit_sha} from {pr}.")
                ret = run_cmd(["git", "status"])
                print(ret.stdout.decode("utf-8"))
                print(
                    ">>> Please fix the above issue in another shell. When you are done, hit ENTER "
                    "to continue."
                )
                input()

    print(">>> Done.")
    print(">>> Log since %s tip ..." % main_branch)
    ret = run_cmd(["git", "log", "--oneline", "%s..HEAD" % main_branch])
    print(ret.stdout.decode("utf-8").strip())


def subcommand_prmsg(config, args):
    main_branch = config["main_branch"]
    ret = run_cmd(["git", "log", "--oneline", "%s..HEAD" % main_branch])

    stdout = ret.stdout.decode("utf-8").splitlines()

    if stdout:
        print("Update dependencies. This covers:")
        print("")
        print("\n".join(["* %s" % line.strip().split(" ", 1)[1] for line in stdout]))
    else:
        print('There are no new commits in this branch. Use "pmac add" to add some.')


def subcommand_listprs(config, args):
    github_user = config["github_user"]
    github_project = config["github_project"]
    main_branch = config["main_branch"]
    api_token = config["github_api_token"]

    url = f"{GITHUB_API}repos/{github_user}/{github_project}/pulls?base={main_branch}"
    resp = fetch(url, api_token=api_token)
    for pr in resp:
        print("%s %s" % (pr["number"], pr["title"]))


def main(argv=None):
    argv = argv or sys.argv[1:]

    parser = argparse.ArgumentParser(
        description=HELP_TEXT,
        epilog=EPILOG_TEXT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="cmd", help="Sub-command")
    subparsers.required = True

    # Create parser for "add" command
    parser_add = subparsers.add_parser(
        "add", help="combine specified PRs into this branch"
    )
    parser_add.add_argument("pr", nargs="+", help="PR to combine")

    # Create parser for "prmsg" command
    subparsers.add_parser("prmsg", help="print out a PR summary")

    # Create parser for "list" command
    subparsers.add_parser("listprs", help="list available PRs for project")

    parsed = parser.parse_args(argv)
    config = get_config(args=parsed)

    # Assert configuration
    for key, val in config.items():
        if key not in OPTIONAL_CONFIG and not val:
            raise Exception(f"Configuration '{key}' not set.")

    if parsed.cmd == "add":
        return subcommand_add(config, parsed)
    elif parsed.cmd == "prmsg":
        return subcommand_prmsg(config, parsed)
    elif parsed.cmd == "listprs":
        return subcommand_listprs(config, parsed)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
