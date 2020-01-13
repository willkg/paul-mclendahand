# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import configparser
import os
import subprocess
import sys


HELP = """\
Usage: pmac COMMAND

add PR [PR...]  add PRs to this set
prmsg           build a PR summary
"""


DEFAULT_CONFIG = {"github_user": "", "github_project": ""}

COMMIT_MESSAGE_FILE = "CMTMSG"


def get_config():
    """Generates configuration.

    This tries to pull from the [tool:release] section of a setup.cfg in the
    working directory. If that doesn't exist, then it uses defaults.

    :returns: configuration dict

    """
    my_config = dict(DEFAULT_CONFIG)

    if os.path.exists("setup.cfg"):
        config = configparser.ConfigParser()
        config.read("setup.cfg")

        if "tool:pmac" in config:
            config = config["tool:pmac"]
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


def subcommand_add(config, prs):
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


def subcommand_prmsg(config):
    ret = run_cmd(["git", "log", "--oneline", "master..HEAD"])

    print("Update dependencies. This covers:")
    print("")
    print(
        "\n".join(
            [
                "* %s" % line.strip().split(" ", 1)[1]
                for line in ret.stdout.decode("utf-8").splitlines()
            ]
        )
    )


def main(argv=None):
    argv = argv or sys.argv[1:]

    if not argv:
        print(HELP)
        return

    config = get_config()

    subcommand = argv.pop(0)
    if subcommand == "add":
        if not argv:
            print(">>> Nothing to do. Exiting.")
            return 0
        return subcommand_add(config, argv)

    if subcommand == "prmsg":
        return subcommand_prmsg(config)

    print("Unknown command.")
    print(HELP)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
