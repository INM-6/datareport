# -*- coding: utf-8 -*-

from setuptools import setup
import os
import sys
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

long_description = open("README.md").read()
install_requires = [
    'pandoc',
    'jinja2',
    'docopt',
    'ruamel-yaml',
]

setup(
    name="datareport",
    version='<automatically-added-by-packaging>',
    packages=['datareport'],
    package_data={
        '': [
            'LICENSE.txt'
        ],
    },

    install_requires=install_requires,

    author="Dennis Terhorst",
    author_email="d.terhorst@fz-juelich.de",
    description="Tool to combine YAML datasets with Jinja2-based templates.",
    long_description=long_description,

    entry_points = {
        'console_scripts': [
            'reporter = datareport.reporter:main',
        ],
    },

    # https://opensource.org/licenses/BSD-2-Clause
    license="BSD",

    url='https://github.com/INM-6/datareport',
    # https://pypi.org/pypi?:action=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering']
)
