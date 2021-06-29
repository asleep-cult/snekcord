import setuptools


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
    package_data={'snekcord-stubs': ['*.pyi', '**/*.pyi']},
    url='https://github.com/asleep-cult/snekcord',
    install_requires=[
        'httpx',
        'wsaio',
        'snekcord-emojis',
    ],
)
