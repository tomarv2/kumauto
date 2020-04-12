import os
from setuptools import setup, find_packages
base_dir = os.path.dirname(__file__)


setup(
    name='automation',
    version='0.0.3',
    description='automation',
    author='tomarv2',
    author_email='dev-ops@devlabs.com',
    setup_requires='setuptools',
    packages=find_packages(),
    # packages=['change_on_user_repo'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': ['main=change_on_user_repo:main']},
    install_requires=[
        'certifi==2018.4.16',
        'chardet==3.0.4',
        'gitdb2==2.0.3',
        'GitPython==2.1.10',
        'idna==2.7',
        'in-place==0.2.0',
        'PyYAML==3.12',
        'requests==2.19.1',
        'six==1.11.0',
        'smmap2==2.0.3',
        'urllib3==1.23',
        'yamllint==1.11.1'
    ]
)
