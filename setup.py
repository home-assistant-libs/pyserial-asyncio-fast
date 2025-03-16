# setup.py for pySerial-asyncio
#
# For Python 3.x use the corresponding Python executable,
# e.g. "python3 setup.py ..."
#
# (C) 2015-2017 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import os
import re
import sys

if sys.version_info < (3, 5):
    raise RuntimeError("pyserial-asyncio requires at least Python 3.5")

from setuptools import setup

def find_version(file_path):
    """
    Search the file for a version string.

    file_path contain string path components.

    Reads the supplied Python module as text without importing it.
    """
    with open(file_path, "r") as version_file:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                version_file.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


version = find_version(os.path.join('serial_asyncio_fast', '__init__.py'))


setup(
    name="pyserial-asyncio-fast",
    description="Python Serial Port Extension - Asynchronous I/O support",
    version=version,
    author="pySerial-team",
    url="https://github.com/home-assistant-libs/pyserial-asyncio-fast",
    packages=['serial_asyncio_fast'],
    install_requires=[
        'pyserial',
    ],
    license="BSD",
    long_description="""\
Async I/O extension package for the Python Serial Port Extension for OSX, Linux, BSD

- Documentation: http://pyserial-asyncio.readthedocs.io
- Project Homepage: https://github.com/home-assistant-libs/pyserial-asyncio-fast
""",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals :: Serial',
    ],
    platforms='any',
)
