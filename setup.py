from setuptools import setup, find_packages
import os

setup(
    name = "septic_tank",
    version = "0.1",
    packages = ['septic_tank',],
    author = "Cox Media Group",
    author_email = "opensource@coxinc.com",
    description = "A pipeline log parser",
    license = "MIT",
    url = "https://github.com/coxmediagroup/septic_tank",
)

# virtualenv -p python2.7 vseptic_tank
# source ./vseptic_tank/bin/activate
# pip install -r requirements.txt
