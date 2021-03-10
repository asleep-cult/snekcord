import gzip
import io
import atexit
import ctypes.util
import shutil
import platform
import tarfile
import urllib.request

from setuptools import setup, find_packages, Extension


ARCHITECTURE = 8 * ctypes.sizeof(ctypes.c_voidp)

if platform.system() == 'Windows':
    WINDOWS = True
else:
    WINDOWS = False

OPUS_RELEASE = 'https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz'
OPUS_HEADERS = ('opus.h', 'opus_custom.h', 'opus_defines.h', 'opus_multistream.h',
                'opus_projection.h', 'opus_types.h')

opus_include_dir = None

if WINDOWS:
    if ARCHITECTURE == 64:
        LIBRARIES = ['opus-win-x64']
    else:
        LIBRARIES = ['opus-win32']
else:
    lib = ctypes.util.find_library('opus')
    if lib is None:
        CAN_COMPILE = False
    else:
        LIBRARIES = [':' + lib]


def get_header(name):
    for header in OPUS_HEADERS:
        if name.endswith(header):
            return header


def get_opus_headers():
    global opus_include_dir

    buffer = io.BytesIO(urllib.request.urlopen(OPUS_RELEASE).read())

    with gzip.GzipFile(fileobj=buffer) as fp:
        tfile = tarfile.TarFile(fileobj=fp)

        for name in tfile.getnames():
            header = get_header(name)

            if header is not None:
                opus_include_dir = name[:-len(header)]
                tfile.extract(name)


def cleanup_opus_headers():
    try:
        shutil.rmtree(opus_include_dir.split('/')[0])
    except Exception:
        pass


try:
    get_opus_headers()
    CAN_COMPILE = True
except Exception:
    CAN_COMPILE = False

atexit.register(cleanup_opus_headers)


if CAN_COMPILE:
    ext_modules = [
        Extension(
            name='opus',
            sources=['./snakecord/audio/_opusmodule.c'],
            include_dirs=['./' + opus_include_dir],
            library_dirs=['./snakecord/.libs'],
            libraries=LIBRARIES
        )
    ]
else:
    ext_modules = None

setup(
    name='snakecord',
    version='0.2.1',
    url='https://github.com/blanketsucks/snakecord',
    packages=find_packages(),
    ext_modules=ext_modules,
)
