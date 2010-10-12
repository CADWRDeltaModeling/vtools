
"""vtools setup file"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup,find_packages

# Metadata
PACKAGE_NAME = "vtools.test"
PACKAGE_VERSION = "0.1.5"
PACKAGES = ['vtools']

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    url = "http://bdo.water.ca.gov",
    description='module handling dss file',
    #long_description = get_description(),
    author="Eli Ateljevich, Qiang Shu",
    author_email="eli@water.ca.gov",
    license="PSF or ZPL",
    install_requires = ['setuptools','Traits>=3.4','vtools>=0.1.5'],
    packages = find_packages(),
    namespace_packages=['vtools','vtools.datastore'],
    test_suite = "nose.collector",
    tests_require = "nose",  
    package_data={
                  "vtools.test":["backup/*.dss","backup/*.h5","*.txt"],                  
                 },
    exclude_package_data = { '': ['*.pyc','*.pyo'] }
)

