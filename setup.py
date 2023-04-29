from setuptools import setup

setup(
    name='watson2sf',
    version='0.1.0',
    py_modules=['watson2sf'],
    install_requires=[
        'Click',
        'tomli',
    ],
    entry_points={
        'console_scripts': [
            'watson2sf = watson2sf:cli',
        ],
    },
)
