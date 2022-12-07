# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# NOTE(willkg): we're using the backfill library until we can drop support for
# Python 3.7.
from importlib_metadata import (
    version as importlib_version,
    PackageNotFoundError,
)


try:
    __version__ = importlib_version("pmac-mclendahand")
except PackageNotFoundError:
    __version__ = "unknown"
