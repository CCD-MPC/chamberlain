from setuptools import setup

setup(
    name             = 'WebConclave',
    version          = '0.0.0.1',
    install_requires = ['gunicorn','flask','pystache'],
    license          = 'MIT',
    url              = 'https://github.com/multiparty/WebConclave',
    description      = 'Web API for OpenShift deployment of Conclave.'
)
