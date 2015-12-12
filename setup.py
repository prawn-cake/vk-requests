from distutils.core import setup

setup(
    name='vk-requests',
    version='0.9.0',
    packages=['vk_requests', 'vk_requests.tests'],
    url='https://github.com/prawn-cake/vk-requests',
    license='MIT',
    author='Maksim Ekimovskii',
    author_email='ekimovsky.maksim@gmail.com',
    description='vk.com requests for humans. API library for vk.com',
    install_requires=[
        'six',
        'requests==2.8.1'
    ]
)
