
"""vtools setup file"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup,find_packages

# Metadata
PACKAGE_NAME = "vtools.datastore.hdf5"
PACKAGE_VERSION = "0.1.5"
PACKAGES = ['vtools','vtools.datastore']

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    url = "http://bdo.water.ca.gov",
    description='excel module handling time sereies ',
    #long_description = get_description(),
    author="Eli Ateljevich, Qiang Shu",
    author_email="eli@water.ca.gov",
    license="PSF or ZPL",
    install_requires = ['Traits>3.0','vtools'],
    test_suite = 'test',
    packages = find_packages(),
    namespace_packages = find_packages(),
 
    package_data={
                  "vtools.datastore.hdf5.test":["backup/*.h5"],
                  "vtools.datastore.hdf5":["examples/*.py"]
                 },
    exclude_package_data = { '': ['*.pyc','*.pyo'] },
    entry_points="""
            [vtools.datastore]
            HDF5Service=vtools.datastore.hdf5.api:HDF5Service
        """
)

