import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = []

setup(name='daemonchain',
      version='0.1',
      description='Python bitcoind blockchain parser. (i.e. Slow)',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python"
        ],
      author='Nicholas Long',
      author_email='adoc@webmob.net',
      url='https://github.com/adoc/',
      keywords='bitcoin',
      packages=find_packages(),
      scripts=['bin/chainworks.py'],
      include_package_data=True,
      zip_safe=False,
      test_suite='daemonchain.tests',
      install_requires=requires,
      test_requires=[]
      )
