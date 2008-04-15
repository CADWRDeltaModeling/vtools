
"""vtools setup file"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup,find_packages

# Metadata
PACKAGE_NAME = "vtools.datastore.excel"
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
    install_requires = ['enthought.traits>=1.0','vtools'],
    test_suite = 'test',
    packages = find_packages(),
    namespace_packages = find_packages(),
 
    package_data={"":['*.py'],
                  "vtools.datastore.excel.test":["backup_excelfile/*.xls"],
                  "vtools.datastore.excel":["examples/*.py"]
                 },
    exclude_package_data = { '': ['*.pyc','*.pyo'] },
    
    entry_points="""
            [vtools.datastore]
            ExcelService=vtools.datastore.excel.api:ExcelService
        """
)

