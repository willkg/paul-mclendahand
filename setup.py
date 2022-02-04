#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import re
from setuptools import find_packages, setup


def get_version():
    fn = os.path.join("src", "paul_mclendahand", "__init__.py")
    vsre = r"""^__version__ = ['"]([^'"]*)['"]"""
    version_file = open(fn, "rt").read()
    return re.search(vsre, version_file, re.M).group(1)


def get_file(fn):
    with open(fn) as fp:
        return fp.read()


INSTALL_REQUIRES = []
EXTRAS_REQUIRE = {
    # NOTE(willkg): We pin these because we want to know what we're testing
    # and building with. Use "make checkrot" to figure out what to update.
    "dev": [
        "black==22.1.0",
        "check-manifest==0.47",
        "flake8==4.0.1",
        "tox==3.24.5",
        "tox-gh-actions==2.9.1",
        "twine==3.8.0",
    ]
}

setup(
    name="paul-mclendahand",
    version=get_version(),
    description="Tool for combining GitHub pull requests.",
    long_description=(get_file("README.rst") + "\n\n" + get_file("HISTORY.rst")),
    author="Will Kahn-Greene",
    author_email="willkg@mozilla.com",
    url="https://github.com/willkg/paul-mclendahanad",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="MPLv2",
    zip_safe=False,
    keywords="github pr",
    entry_points="""
    [console_scripts]
    pmac=paul_mclendahand.cmd_pmac:main
    """,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
