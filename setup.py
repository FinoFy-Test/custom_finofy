from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in custom_finofy/__init__.py
from custom_finofy import __version__ as version

setup(
	name="custom_finofy",
	version=version,
	description="HashI",
	author="Ashish Bankar",
	author_email="ashish.bankar@capitalvia.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
