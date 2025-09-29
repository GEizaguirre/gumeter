from setuptools import setup, find_packages

from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name='gumeter',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'gumeter=gumeter.cli:main',
        ],
    },
    author='Germán T. Eizaguirre',
    author_email='germantelmo.eizaguirre@urv.cat',
    description=(
        'Gumeter: A benchmarking suite for serverless platform elasticity.'
    ),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/GEizaguirre/gumeter.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
