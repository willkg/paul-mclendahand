#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from setuptools import find_packages, setup


def get_file(fn):
    with open(fn) as fp:
        return fp.read()


INSTALL_REQUIRES = [
    "click<9.0.0",
    "importlib_metadata",
    "rich",
]


setup(
    name="paul-mclendahand",
    version="3.0.0",
    description="Tool for combining GitHub pull requests.",
    long_description=(get_file("README.rst") + "\n\n" + get_file("HISTORY.rst")),
    long_description_content_type="text/x-rst",
    author="Will Kahn-Greene",
    author_email="willkg@mozilla.com",
    url="https://github.com/willkg/paul-mclendahanad",
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="MPLv2",
    zip_safe=False,
    keywords="github pr",
    entry_points="""
    [console_scripts]
    pmac=paul_mclendahand.cmd_pmac:pmac_cli
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
        "Programming Language :: Python :: 3.11",
    ],
)
