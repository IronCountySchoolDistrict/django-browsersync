"""Setup scrip of django-broswersync"""
from setuptools import setup
from setuptools import find_packages

setup(
    name='django-browsersync',
    version='0.0.1',

    description='browser-sync with gulpfile support and the Django development server',
    long_description=open('README.rst').read(),

    keywords=['django', 'server', 'runserver', 'browser-sync', 'gulp'],

    author='Iron County School District,
    author_email='tech@ironmail.org,
    url='https://irondistrict.org,

    packages=find_packages(),

    install_requires=[
        'ansicolors==1.1.8',
        'env-tools==2.1.0',
        'futures==3.1.1',
        'psutil==5.2.2',
    ],
    
    setup_requires=[
        'setuptools-markdown'
    ],

    classifiers=[
        'Framework :: Django',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    include_package_data=True,
)