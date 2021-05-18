import setuptools

setuptools.setup(
    name='snakecord',
    version='0.2.3',
    url='https://github.com/asleep-cult/snakecord',
    packages=setuptools.find_packages(),
    install_requires=[
        'wsaio',
        'snakecord-emojis',
    ],
)
