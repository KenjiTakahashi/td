# -*- coding: utf-8 -*-
# This is a part of td @ http://github.com/KenjiTakahashi/td
# Karol "Kenji Takahashi" Woźniak © 2012 - 2013
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup
from td.main import __version__


setup(
    name='td',
    version=__version__,
    description='A non-offensive, per project ToDo manager.',
    long_description=open('README.md').read(),
    author='Karol "Kenji Takahashi" Woźniak',
    author_email='wozniakk@gmail.com',
    license='GPL3',
    url='http://github.com/KenjiTakahashi/td',
    packages=[
        'td'
    ],
    scripts=['scripts/td'],
    install_requires=['colorama'],
    classifiers=[f.strip() for f in """
    Development Status :: 4 - Beta
    Environment :: Console
    Intended Audience :: Developers
    Intended Audience :: End Users/Desktop
    License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
    Natural Language :: English
    Operating System :: OS Independent
    Programming Language :: Python :: 3
    Topic :: Utilities
    """.splitlines() if f.strip()]
)
