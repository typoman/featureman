#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name="featureMan",
    version="0.0.1",
    description="A python library to generate Open type features based on the infotmation stored in a UFO font tile.",
    author="Bahman Eslami",
    author_email="contact@bahman.design",
    url="http://bahman.design",
    license="MIT",
    platforms=["Any"],
    package_dir={'': 'Lib'},
    packages=find_packages('Lib'),
)
