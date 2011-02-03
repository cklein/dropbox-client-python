from setuptools import setup, find_packages

setup(name='dropbox-client',
      version='1.0',
      description='Dropbox REST API Client',
      author='Dropbox, Inc.',
      author_email='support@dropbox.com',
      url='http://www.dropbox.com/',
      packages=['dropbox'],
      install_requires = ['mechanize', 'nose', 'oauth', 'poster', 'simplejson'],
     )

