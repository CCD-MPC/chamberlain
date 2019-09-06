from setuptools import setup, find_packages

setup(
    name             = 'conclave-web',
    version          = '0.0.0.1',
    packages         = find_packages(),
    license          = 'MIT',
    url              = 'https://github.com/cici-conclave/chamberlain',
    description      = 'Runs Conclave jobs on the MOC',
    long_description = open('README.md').read()
)
