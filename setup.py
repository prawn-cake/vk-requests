from setuptools import setup

import sys


PY_VERSION = sys.version_info.major, sys.version_info.minor

install_requires = [
    'python-rucaptcha',
    'six',
    'requests>=2.8.1',
    'beautifulsoup4>=4.4.1']


with open('README.md') as f:
    readme = f.read()


setup(
    name='vk-requests',
    version='1.2.0',
    packages=['vk_requests'],
    url='https://github.com/prawn-cake/vk-requests',
    license='MIT',
    author='Maksim Ekimovskii',
    author_email='ekimovsky.maksim@gmail.com',
    description='vk.com requests for humans. API library for vk.com',
    long_description=readme,
    install_requires=install_requires,
    extras_require={
        'streaming:python_version>="3.4"': ['websockets']
    },
    classifiers=[
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
