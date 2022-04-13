#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Repometer: 
    setup.py sets up the command-line interface for the 
    Repometer package. 
    
    python setup.py install
    
    repometer [options]
"""

import os
from setuptools import setup, find_packages


def read(fname):
    """
    Reads the README functions are prints them into the long_description in
    the setup routine.

    Parameters
    ----------
    fname : README file name

    Returns
    -------
    Rendered README

    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Metrics",
    "Topic :: Usage",
    "Topic :: Impact",
    "Topic :: Popularity",
    "Topic :: Database",
]

requires = [
    'PyGithub == 1.55',
    'python-gitlab',
    'requests',
    'pytest>=4.6.0',
    'pytest-mock',
    'pytest_socket',
    'testing.mysqld',
    'mysql-connector-python',
    'pytest-cov'
]


def run_setup():
    """
    This functions holds the setup command. Rather than running setup directly,
    it is wrapped in a 'try-except' that will print out errors if they occur.
    """
    setup(
        name='Repometer',
        version='1.0.0',
        maintainer='Reed Milewicz and Miranda Mundt',
        maintainer_email='rmilewi@sandia.gov and mmundt@sandia.gov',
        url='github url',
        description='Repometer: Repository Traffic and Usage Collector',
        long_description=read('README.md'),
        long_description_content_type='text/markdown',
        classifiers=classifiers,
        packages=find_packages(),
        keywords=['metrics', 'usage', 'repometer',
                  'impact', 'data', 'collection'],
        install_requires=requires,
        python_requires='>=3.7, !=3.10',
        entry_points={'console_scripts': [
            'repometer = repometer.main.main:main',
            'backup_database = repometer.database.backup:main']}
    )


try:
    run_setup()
except SystemExit as e:
    print(e)
