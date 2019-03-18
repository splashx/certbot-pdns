#! /usr/bin/env python
from os import path
from setuptools import setup
from setuptools import find_packages

install_requires = [
    'acme>=0.21.1',
    'certbot>=0.21.1',
    'dnspython',
    'mock',
    'setuptools',
    'zope.interface',
    'requests'
]

here = path.abspath(path.dirname(__file__))

setup(
    name='certbot-dns-powerdns',
    version="1.0.0",

    description="PowerDNS DNS Authenticator plugin for Certbot",

    url='https://github.com/pan-net-security/certbot-powerdns',
    author="DT Pan-Net s.r.o",
    author_email='pannet.security@pan-net.eu',
    license='MIT',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: Name Service (DNS)',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],

    packages=find_packages(),
    install_requires=install_requires,

    # extras_require={
    #     'docs': docs_extras,
    # },

    entry_points={
        'certbot.plugins': [
            'dns-powerdns = certbot_dns_powerdns.dns_powerdns:Authenticator',
        ],
    },
    test_suite='certbot_dns_powerdns',
)
