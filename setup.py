#!/usr/bin/env python
import io
import os
from setuptools import setup, find_packages

# Package metadata
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='blackmirror_lite',
    version='0.1.0',
    description='BlackMirror Lite: a filesystem snapshot time machine without Git',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Dcamy/ADAPTiQ',
    author='ADAPTiQ',
    license='MIT',
    packages=find_packages(exclude=['tests', 'docs', 'env', 'build', 'dist']),
    python_requires='>=3.6',
    install_requires=[
        'watchdog',
    ],
    entry_points={
        'console_scripts': [
            'bml=blackmirror_lite.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)