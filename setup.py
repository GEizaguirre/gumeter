from setuptools import setup, find_packages

setup(
    name='gumeter',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'matplotlib',
        'pandas',
        # Add other dependencies like torch if needed,
        # but consider making them optional or as extras
    ],
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
