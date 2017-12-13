"""Setup scrip of django-broswersync"""
import browser_sync

from setuptools import setup
from setuptools import find_packages

setup(
    name='django-browsersync',
    version=browser_sync.__version__,

    description='browser-sync with gulp and the Django development server',
    long_description=open('README.rst').read(),

    keywords='django, server, runserver, browser-sync, gulp',

    author=browser_sync.__author__,
    author_email=browser_sync.__email__,
    url=browser_sync.__url__,

    packages=find_packages(),
    classifiers=[
        'Framework :: Django',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    license=browser_sync.__license__,
    include_package_data=True,
)