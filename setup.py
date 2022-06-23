import os
import re
import sys
from pathlib import Path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ytinsepctor',
    author='Jie Jenn',
    author_email='jiejenn@learndataanalysis.org',
    version='1.0.1',
    keywords=['YouTube', 'YouTube Scraper'],
    python_requires='>=3.6',
    install_requires=['google-auth>=1.12.0', 'google-auth-oauthlib>=0.4.1', 'google-api-python-client>=2.41.0',
                      'google-api-python-client>=2.41.0'],
    packages=['ytinsepctor'],
    license='MIT'
)    
