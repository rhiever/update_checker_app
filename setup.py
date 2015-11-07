import os
import re
from setuptools import setup

PACKAGE_NAME = 'update_checker_app'

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.md')) as fp:
    README = fp.read()
with open(os.path.join(HERE, PACKAGE_NAME, '__init__.py')) as fp:
    VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)

setup(name=PACKAGE_NAME,
      author='Bryce Boe',
      author_email='bbzbryce@gmail.com',
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      description=('Flask Application that provides the interface to the '
                   'update_checker package.'),
      entry_points={'console_scripts':
                    ['{0}={0}:main'.format(PACKAGE_NAME)]},
      install_requires=['flask >=0.10.1, <1',
                        'flask_sqlalchemy >=2.1, <3',
                        'psycopg2 >=2.6.1, <3',
                        'requests >=2.8.1, <3'],
      keywords=['python packages', 'update check'],
      license='Simplified BSD License',
      long_description=README,
      packages=[PACKAGE_NAME],
      url = 'https://github.com/bboe/update_checker_app',
      version=VERSION)
