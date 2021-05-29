import setuptools

setuptools.setup(
    name='snekcord',
    version='0.2.3',
    url='https://github.com/asleep-cult/snekcord',
    packages=setuptools.find_packages(),
    install_requires=[
        'httpx',
        'wsaio',
        'snekcord-emojis',
    ],
)
