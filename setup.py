import os
from setuptools import setup, find_packages

# Setup version
VERSION = '0.1.0.dev0'

# Read description

with open('README.rst', 'r') as readme:
    README_TEXT = readme.read()


def write_version_py():
    filename = os.path.join(
        os.path.dirname(__file__),
        'tornado_rest_jsonapi',
        'version.py')
    ver = "__version__ = '{}'\n"
    with open(filename, 'w') as fh:
        fh.write("# Autogenerated by setup.py\n")
        fh.write(ver.format(VERSION))


write_version_py()

# main setup configuration class
setup(
    name='tornado_rest_jsonapi',
    version=VERSION,
    author='Force H2020 Project',
    license='BSD',
    description='Tornado-based REST+JSONAPI framework',
    install_requires=[
        "setuptools>=21.0",
        "tornado>=4.5",
        "marshmallow>=2.13",
        "marshmallow_jsonapi>=0.14",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
    )
