# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(HERE, 'qc4sd', '__init__.py'), encoding='utf-8') as fp:
    VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)

setup(
    name='QC4SD',
    version=VERSION,
    description='Quality Control Algorithm for Satellite Data',
    long_description=README,
    author='Xavier Corredor Llano, SMBYC-IDEAM',
    author_email='xcorredorl@ideam.gov.co, smbyc@ideam.gov.co',
    url='https://bitbucket.org/SMBYC/qc4sd',
    license='GPLv3',
    packages=find_packages(),
    install_requires=['gdal',
                      'numpy',
                      'matplotlib',
                      'joblib'],
    scripts=['bin/qc4sd'],
    platforms=['Any'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: GIS",
        "Intended Audience :: Science/Research",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
)
