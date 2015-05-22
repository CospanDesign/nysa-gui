#! /usr/bin/env python

import os
import glob

from setuptools import setup, find_packages
from distutils.command.install import install as DistutilsInstall


long_desc="",

try:
    #Try and convert the readme from markdown to pandoc
    from pypandoc import convert
    long_desc = convert("README.md", 'rst')
except:
    long_desc="Graphical FPGA Development Interaction Environment"


setup(
    name='nysa-gui',
    version='0.0.1',
    description='Graphical FPGA Development and Interaction Environment',
    author='Cospan Design',
    author_email='dave.mccoy@cospandesign.com',
    packages=find_packages('.'),
    url="http://nysa.cospandesign.com",
    package_data={'' : ["*.json", "*.txt, *.md"]},
    data_files=[
    ],
    include_package_data = True,
    long_description=long_desc,
    entry_points = {
        'console_scripts': ['nui=NysaGui.nysa_gui.nysa_gui:main'],
    },
    install_requires=[
        'nysa >= 0.8.6',
        'networkx >= 1.9.1',
        'pyYAML >= 3.11',
        'numpy >= 1.8.2',
        'pyqtgraph >= 0.9.10'
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: MIT License",
        "Environment :: X11 Applications :: Qt"
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
    ],
    keywords="FPGA",
    license="GPL"
)
