from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(name='howto',
      scripts=['howto.py', 'vihowto'],
      install_requires=['distribute'],
      )
