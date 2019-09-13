from setuptools import find_packages, setup

setup(
    name='code',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'coderun = code.main:main',
        ],
    },
    include_package_data=True,
)
