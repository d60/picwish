import re

from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

with open('./picwish/__init__.py') as f:
    version = re.findall(r"__version__ = '(.+)'", f.read())[0]

setup(
    name='picwish',
    version=version,
    install_requires=[
        'httpx',
        'filetype'
    ],
    python_requires='>=3.10',
    description='Picwish Photo Enhancer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/d60/picwish',
)
