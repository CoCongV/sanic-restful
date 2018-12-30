import re
from os import path
from setuptools import setup, find_packages


requirements = [
    'aniso8601>=0.82',
    'Sanic',
    'pytz',
    'werkzeug',
]


version_file = path.join(
    path.dirname(__file__),
    'sanic_restful',
    '__version__.py'
)
with open(version_file, 'r') as fp:
    m = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        fp.read(),
        re.M
    )
    version = m.groups(1)[0]


setup(
    name='sanic-restful',
    version=version,
    license='BSD',
    url='https://github.com/moonlitlaputa/sanic-restful',
    author='Twilio API Team',
    author_email='help@twilio.com',
    description='Simple framework for creating REST APIs',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: BSD License',
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite='nose.collector',
    install_requires=requirements,
    tests_require=['Sanic-RESTful[paging]', 'mock>=0.8', 'blinker'],
    # Install these with "pip install -e '.[paging]'" or '.[docs]'
    extras_require={
        'paging': 'pycrypto>=2.6',
        'docs': 'sphinx',
    }
)
