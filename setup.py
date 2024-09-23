from setuptools import setup

setup(
    name='tile_padder',
    py_modules=['tile_padder'],
    entry_points={
        'console_scripts': ['tile_padder = tile_padder:main', ],
    },
)
