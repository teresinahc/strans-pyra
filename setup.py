#!/usr/bin/python

from distutils.core import setup

setup(
    name='stranspyra',
    version='0.1.0',
    description='Inthegra API Python wrapper',
    author='Renato Alencar',
    author_email='renatoalencar.73@gmail.com',
    url='https://github.com/teresinahc/strans-pyra',
    packages=['stranspyra'],
    install_requires=[
        'requests',
        'geopy'
    ],
    long_description="""This is a Python wrapper for the Inthegra API,
designed to provides some features not implemented
in the Inthegra API."""
)
