import os

import setuptools


def get_all_files(directory):
    paths = []
    for path, _, filenames in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


setuptools.setup(
    name='snekcord',
    version='0.2.3',
    packages=[
        'snekcord-stubs',
        'snekcord',
        'snekcord.clients',
        'snekcord.objects',
        'snekcord.rest',
        'snekcord.states',
        'snekcord.utils',
        'snekcord.ws'
    ],
    package_data={'snekcord-stubs': get_all_files('./snekcord-stubs')},
    url='https://github.com/asleep-cult/snekcord',
    install_requires=[
        'httpx',
        'wsaio',
        'snekcord-emojis',
    ],
)
