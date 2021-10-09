#!/usr/bin/python3

import os
import setuptools
import pytcnz.meta


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name="pytcnz",
    use_scm_version=True,
    author=pytcnz.meta.author,
    author_email=pytcnz.meta.email,
    description=(
        "Support library for SquashNZ Tournament Control"
    ),
    license=pytcnz.meta.licence,
    keywords="TournamentControl squash mail-merge manage "
    "tournaments registrations draws grading list",
    url=pytcnz.meta.url,
    packages=setuptools.find_packages(),
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "pyexcel",
        "pyexcel-xls",
        "pyexcel-ods",
        "beautifulsoup4",
        "selenium",
        "phonenumbers",
        "python-dateutil",
        "requests",
    ],
    setup_requires=[
        "setuptools_scm",
    ],
)
