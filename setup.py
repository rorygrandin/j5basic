from setuptools import setup

setup(
    name='j5.Basic',
    version='1.0',
    packages=['j5', 'j5.Basic'],
    license='Apache Software License',
    description='A collection of utility methods and classes.',
    long_description=open('README.md').read(),
    url='http://www.j5int.com/',
    author='j5 Software',
    author_email='support@sjsoft.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires = ["pytz"],
    extras_require = {
        'CleanXHTML':  ["cssutils", "lxml"],
        'Colours':  ["numpy"],
        'Timer': ['virtualtime'],
        'tests': ['j5.Test'],
    }
)