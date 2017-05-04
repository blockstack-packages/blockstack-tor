#!/usr/bin/env python

from setuptools import setup, find_packages

# to set __version__
exec(open('blockstack_tor/version.py').read())

setup(
    name='blockstack-tor',
    version=__version__,
    url='https://github.com/blockstack/blockstack-tor',
    license='MIT',
    author='Blockstack.org',
    author_email='support@blockstack.org',
    description='Blockstack/Tor integration for doing .onion lookups with Blockstack'
    keywords='blockchain blockstack name key value naming dns tor onion',
    packages=find_packages(),
    scripts=[
        'bin/blockstack-tor'
    ],
    download_url='https://github.com/blockstack/blockstack-tor/archive/master.zip',
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'blockstack>=0.14.2',
        'stem>=1.5.4',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
