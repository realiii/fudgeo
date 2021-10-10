# -*- coding: utf-8 -*-
"""
Setup
"""


from setuptools import setup
from os.path import join, dirname

with open(join(dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='fudgeo',
    version='0.1.0',
    author='Integrated Informatics Inc.',
    author_email='gis@integrated-informatics.com',
    description='GeoPackage support from Python.  fudgeo is a simple package '
                'for creating OGC GeoPackages, Feature Classes, Tables, and '
                'geometries (read and write).',
    long_description=README,
    long_description_content_type='text/markdown',
    include_package_data=True,
    package_data={'': ['*.sql']},
    url='https://github.com/realiii/fudgeo',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=['fudgeo'],
)
