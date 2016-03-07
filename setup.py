from setuptools import setup

setup(
    name='vk-requests',
    version='0.9.5',
    packages=['vk_requests'],
    url='https://github.com/prawn-cake/vk-requests',
    license='MIT',
    author='Maksim Ekimovskii',
    author_email='ekimovsky.maksim@gmail.com',
    description='vk.com requests for humans. API library for vk.com',
    install_requires=[
        'six',
        'requests==2.8.1',
        'beautifulsoup4==4.4.1'
    ],
    classifiers=[
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ]
)
