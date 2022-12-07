# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from click.testing import CliRunner

from paul_mclendahand.cmd_pmac import pmac_cli


def test_pmac_cli():
    runner = CliRunner()

    runner.invoke(pmac_cli, ["--help"])

    runner.invoke(pmac_cli, ["add", "--help"])

    runner.invoke(pmac_cli, ["listprs", "--help"])

    runner.invoke(pmac_cli, ["prmsg", "--help"])
