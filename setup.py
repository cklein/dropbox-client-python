from setuptools import setup, find_packages
import sys

INSTALL_REQUIRES = ['oauth', 'simplejson']

if sys.version_info < (2,6):
    INSTALL_REQUIRES.append('ssl')  # This module is built in to Python 2.6+

#must be called dropbox-client so it overwrites the older dropbox SDK
setup(name='dropbox',
      version='1.3',
      description='Official Dropbox REST API Client',
      author='Dropbox, Inc.',
      author_email='support-api@dropbox.com',
      url='http://www.dropbox.com/',
      packages=['dropbox'],
      install_requires=INSTALL_REQUIRES,
      package_data={'dropbox': ['trusted-certs.crt']}
     )
