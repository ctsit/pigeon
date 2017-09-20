from setuptools import setup, find_packages

setup(name='pigeon',
      version='1.0.0',
      description='Pigeon brings your records to redcap.',
      url='http://github.com/pfwhite/pigeon',
      author='Patrick White',
      author_email='pfwhite9@gmail.com',
      license='Apache 2.0',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'pigeon = pigeon.__main__:cli_run',
          ],
      },
      install_requires=[
          'cappy==1.1.1',
          'docopt==0.6.2',
          'pyyaml==3.12'],
      dependency_links=["git+https://github.com/ctsit/cappy@1.1.1#egg=cappy-1.1.1"],
      zip_safe=False)
