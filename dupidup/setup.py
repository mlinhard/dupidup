from setuptools import setup

setup(name='dupidup',
      version='0.1.0',
      description='File deduplication tool',
      url='https://github.com/mlinhard/dupidup',
      author='Michal Linhard',
      author_email='michal@linhard.sk',
      license='Apache 2.0',
      packages=['dupidup'],
      zip_safe=False,
      install_requires=[
          'docopt', 'magicur'
      ])
