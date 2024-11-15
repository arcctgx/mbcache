from setuptools import find_packages, setup

from mbcache.version import APPNAME, URL, VERSION

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

with open('LICENSE', encoding='utf-8') as f:
    license_ = f.read()

setup(name=APPNAME,
      version=VERSION,
      description='A simple cache for MusicBrainz data.',
      long_description=readme,
      author='arcctgx',
      author_email='arcctgx@o2.pl',
      url=URL,
      license=license_,
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'mb-release-lookup = mbcache.release_lookup:main',
              'mb-release-search = mbcache.release_search:main',
              'mb-recording-search = mbcache.recording_search:main'
          ]
      })
