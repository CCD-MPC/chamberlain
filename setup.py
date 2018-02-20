from setuptools import setup

setup(
    name             = 'conclave',
    version          = '0.0.0.1',
    packages         = ['conclave',],
    install_requires = ['pystache', 'flask'],
    license          = 'MIT',
    url              = 'https://github.com/multiparty/WebConclave',
    description      = 'Web API for OpenShift deployment of Conclave.',
    long_description = open('README.rst').read()
)