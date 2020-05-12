import os

from setuptools import find_packages, setup

VERSION = "0.0.1.dev12"

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


def get_requirements(env):

    with open("requirements-{}.txt".format(env)) as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


install_requires = get_requirements("base")

with open("README.md") as f:
    long_description = f.read()

setup(
    name='mauto',
    version=VERSION,
    description='Automate deployment of monitoring tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Varun Tomar',
    author_email='varuntomar2019@gmail.com',
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=find_packages("src"),
    url="https://github.com/tomarv2/mauto",
    classifiers=[  # Optional
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        mauto = automation.cli:entrypoint
    '''
)

