# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in pos_barcode_scanner/__init__.py
from pos_barcode_scanner import __version__ as version

setup(
	name='pos_barcode_scanner',
	version=version,
	description='App to customize POS to search only by barcode',
	author='Abdullah Zaqout',
	author_email='zaqoutabed@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
