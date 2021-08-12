# Licensed under the MIT License
# https://github.com/craigahobbs/schema-markdown/blob/main/LICENSE

# pylint: disable=missing-docstring

import os

from setuptools import setup


def main():
    # Read the readme for use as the long description
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as readme_file:
        long_description = readme_file.read()

    # Do the setup
    setup(
        name='schema-markdown',
        description='Human-friendly schema definition language and schema validator',
        long_description=long_description,
        long_description_content_type='text/x-rst',
        version='1.1.2',
        author='Craig A. Hobbs',
        author_email='craigahobbs@gmail.com',
        keywords='schema validation json',
        url='https://github.com/craigahobbs/schema-markdown',
        license='MIT',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Topic :: Utilities'
        ],
        package_dir={'': 'src'},
        packages=['schema_markdown'],
        entry_points={
            'console_scripts': [
                'schema-markdown = schema_markdown.main:main'
            ]
        }
    )


if __name__ == '__main__':
    main()
