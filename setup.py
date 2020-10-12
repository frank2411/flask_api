import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="worklife",
    version="0.1",
    author="Francesco Perna",
    description="Python API to provide data to sample holiday application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    python_requires=">=3.6",
    package_dir={"worklife": "work_api"},
    packages=setuptools.find_packages(exclude=["tests", "migrations"]),
    install_requires=requirements,
)
