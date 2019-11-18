#!/usr/bin/env python

from setuptools import setup


with open("README.md") as fh:
    long_description = fh.read()

setup(
    name='mpldock',
    version='0.0.2',
    description='Dock matplotlib figures and other widgets.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/peper0/mpldock',
    author='Tomasz Łakota',
    author_email='tomasz.lakota@gmail.com',
    install_requires=[
        'PyQt5',
        'matplotlib',
        'appdirs',
    ],
    tests_require=[
    ],
    extras_require={
        'pyqtgraph': ['pyqtgraph'],
    },
    packages=('mpldock',),
    keywords=[
        'matplotlib', 'qt5', 'backend', 'dock', 'docking', 'dockable', 'layout'
        ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    python_requires='>=3.6'
)
