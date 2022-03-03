# -*- coding: utf-8 -*-

VERSION = (0, 0, 1)
PRERELEASE = "alpha"  # alpha, beta or rc
REVISION = None


def generate_version(version, prerelease=None, revision=None):
    version_parts = [".".join(map(str, version))]
    if prerelease is not None:
        version_parts.append(f"-{prerelease}")
    if revision is not None:
        version_parts.append(f".{revision}")
    return "".join(version_parts)


__title__ = "xtable"
__description__ = "Table Extraction for Documents."
__url__ = "http://camelot-py.readthedocs.io/"
__version__ = generate_version(VERSION, prerelease=PRERELEASE, revision=REVISION)
__author__ = "Duc Tuyen TA"
__author_email__ = "tuyentd86@gmail.com"
__license__ = "MIT License"
