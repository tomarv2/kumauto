import os
#from setuptools import setup, find_packages

from setuptools import find_packages, setup
from setuptools.command.develop import develop as DevelopCommand
from setuptools.command.sdist import sdist as SDistCommand

#base_dir = os.path.dirname(__file__)

VERSION = "0.0.1.dev0"

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


def get_requirements(env):

    with open("requirements-{}.txt".format(env)) as fp:
        # print([x.strip() for x in fp.read().split("\n") if not x.startswith("#")])
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


install_requires = get_requirements("base")

setup(
    name='automation',
    version=VERSION,
    description='automating deployment of monitoring tools',
    author='demo',
    author_email='demo@demo.com',
    python_requires=">=3.7",
    package_dir={"": "src"},
    packages=find_packages("src"),
    #zip_save=False,
    include_package_data=True,
    classifiers=[  # Optional
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts': ['automation = automation.cli:entrypoint']}
)
