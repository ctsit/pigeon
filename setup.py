from setuptools import setup, find_packages

setup(name='pigeon',
      version='0.0.1',
      description='Pigeon brings your records to redcap.',
      url='http://github.com/pfwhite/pigeon',
      author='Patrick White',
      author_email='pfwhite9@gmail.com',
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'pigeon = pigeon.__main__:cli_run',
          ],
      },
      install_requires=['cappy', 'docopt', 'pyyaml'],
      zip_safe=False)
