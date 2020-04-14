
from setuptools import setup, find_packages
import os
requirementPath = 'requirements.txt'

if os.path.isfile(requirementPath):
    with open('requirements.txt') as f:
        requires = f.readlines()

install_requires = [item.strip() for item in requires]

setup(name='Time_Matters_Query',
      version='1.0',
      description="",
      author='Jorge Alexandre Rocha Mendes',
      author_email='mendesjorge49@gmail.com',
      url='https://github.com/LIAAD/Time-Matters-Query.git',
      packages=find_packages(),
      install_requires=install_requires
      )

