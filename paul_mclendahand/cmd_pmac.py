# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import configparser
import json
import os
import subprocess
import sys
from urllib.request import urlopen


GITHUB_API = "https://api.github.com/"

DEFAULT_CONFIG = {"github_user": "", "github_project": ""}

COMMIT_MESSAGE_FILE = "CMTMSG"


def get_config():
    """Generates configuration.

    This tries to pull from the ``[tool:paul-mclendahand]`` section of a
    ``setup.cfg`` in the working directory. If that doesn't exist, then it uses
    defaults.

    :returns: configuration dict

    """
    my_config = dict(DEFAULT_CONFIG)

    if os.path.exists("setup.cfg"):
        config = configparser.ConfigParser()
        config.read("setup.cfg")

        if "tool:paul-mclendahand" in config:
            config = config["tool:paul-mclendahand"]
            for key in my_config.keys():
                my_config[key] = config.get(key, "")

    for key in my_config.keys():
        if "PMAC_%s" % key.upper() in os.environ:
            my_config[key] = os.environ["PMAC_%s" % key.upper()]

    return my_config


def get_remote_name(github_user):
    ret = run_cmd(["git", "remote", "-v"])

    for line in ret.stdout.decode("utf-8").strip().splitlines():
        line = line.split("\t")
        if f":{github_user}/" in line[1]:
            return line[0]

    raise Exception(f"Can't figure out remote name for {github_user}.")


def run_cmd(args, check=True):
    return subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check
    )


def subcommand_add(config, args):
    prs = args.pr
    remote = get_remote_name(config["github_user"])

    for pr in prs:
        print(">>> Working on pr %s ..." % pr)
        ret = run_cmd(["git", "log", "--oneline", "master..%s/pr/%s" % (remote, pr)])
        commits = [
            line.strip().split(" ")[0]
            for line in ret.stdout.decode("utf-8").splitlines()
        ]
        for commit in reversed(commits):
            print(">>> Cherry-picking %s ..." % commit)
            ret = run_cmd(["git", "log", "--format=%B", "-n", "1", commit])
            data = ret.stdout.decode("utf-8")

            ret = run_cmd(["git", "cherry-pick", commit], check=False)
            if ret.stdout.decode("utf-8").strip():
                print(ret.stdout.decode("utf-8").strip())
            if ret.stderr.decode("utf-8").strip():
                print(ret.stderr.decode("utf-8").strip())

            if ret.returncode != 0:
                print(">>> Something happened when cherry-picking.")
                print(
                    ">>> Please fix it in another shell and then hit ENTER to contine."
                )
                input()

            data = data.splitlines()
            data[0] = data[0].strip() + " (from PR #%s)" % pr
            try:
                with open(COMMIT_MESSAGE_FILE, "w") as fp:
                    fp.write("\n".join(data))

                run_cmd(["git", "commit", "--amend", "--file=%s" % COMMIT_MESSAGE_FILE])
            finally:
                # Delete the file if it's there
                if os.path.exists(COMMIT_MESSAGE_FILE):
                    os.remove(COMMIT_MESSAGE_FILE)

    print(">>> Done.")
    print(">>> Log since master ...")
    ret = run_cmd(["git", "log", "--oneline", "master..HEAD"])
    print(ret.stdout.decode("utf-8").strip())


def subcommand_prmsg(config, args):
    ret = run_cmd(["git", "log", "--oneline", "master..HEAD"])

    stdout = ret.stdout.decode("utf-8").splitlines()

    if stdout:
        print("Update dependencies. This covers:")
        print("")
        print(
            "\n".join(
                ["* %s" % line.strip().split(" ", 1)[1] for line in stdout]
            )
        )
    else:
        print("There are no new commits in this branch. Use \"pmac add\" to add some.")


def fetch(url, is_json=True):
    """Fetch data from a url

    This raises URLError on HTTP request errors. It also raises JSONDecode
    errors if it's not valid JSON.

    """
    fp = urlopen(url)
    data = fp.read()
    if is_json:
        return json.loads(data)
    return data


def fetch_prs_from_github(owner, repo):
    url = f"{GITHUB_API}repos/{owner}/{repo}/pulls?base=master"
    return fetch(url)


def subcommand_listprs(config, args):
    github_user = config["github_user"]
    github_project = config["github_project"]

    resp = fetch_prs_from_github(github_user, github_project)
    for pr in resp:
        print("%s %s" % (pr["number"], pr["title"]))


def main(argv=None):
    argv = argv or sys.argv[1:]

    parser = argparse.ArgumentParser(description="GitHub pull request combiner tool.")
    subparsers = parser.add_subparsers(dest="cmd", help="Sub-command")
    subparsers.required = True

    # Create parser for "add" command
    parser_add = subparsers.add_parser("add", help="combine specified PRs into this branch")
    parser_add.add_argument("pr", nargs="+", help="PR to combine")

    # Create parser for "prmsg" command
    subparsers.add_parser("prmsg", help="print out a PR summary")

    # Create parser for "list" command
    subparsers.add_parser("listprs", help="list available PRs for project")

    config = get_config()
    parsed = parser.parse_args(argv)

    if parsed.cmd == "add":
        return(subcommand_add(config, parsed))
    elif parsed.cmd == "prmsg":
        return(subcommand_prmsg(config, parsed))
    elif parsed.cmd == "listprs":
        return(subcommand_listprs(config, parsed))
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
