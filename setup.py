from setuptools import setup, find_packages


setup(
    name = 'calebcc',
    description = '''Implements my blog''',
    long_description=open("README.md").read(),
    version = '0.0.1',
    author = 'Caleb Brown',
    url = 'https://github.com/calebbrown/calebcc',
    packages=['blame', 'calebcc', 'feedgenerator'],
    include_package_data=True,
)
