# coding=utf-8
from setuptools import setup

from gcode_cflow import __version__ as version

setup(name='gcode_cflow',
      version=version,
      description='Gcode filter to demonstrate feed rate dependent flow compensation',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          "Operating System :: OS Independent",
      ],

      url='https://github.com/gluap/pyess',
      author='Paul Görgen',
      author_email='pypi@pgoergen.de',
      license='MIT',

      packages=['gcode_cflow','gcode_cflow.scripts'],

      install_requires=[
          'typer', 'scipy', 'pydantic', 'pyyaml'
      ],

      zip_safe=False,
      include_package_data=False,

      tests_require=[
          'pytest'
      ],

      entry_points={'console_scripts': ['cflow=gcode_cflow.scripts.cflow:main']},
      long_description=open('README.rst', 'r').read()
      )