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

#----------------------------------------------------------------------------
# These are the commands I use to create a virtual environment in mint12.
# Your mileage may vary.
#----------------------------------------------------------------------------
# sudo apt-get install -y build-essential python-virtualenv uuid-dev python-dev
# virtualenv -p python2.7 vseptic_tank
# source ./vseptic_tank/bin/activate
# pip install -r requirements.txt
