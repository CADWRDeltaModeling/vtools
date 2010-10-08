
"""vtools setup file"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup,find_packages

# Metadata
PACKAGE_NAME = "vtools"
PACKAGE_VERSION = "0.1.6"
PACKAGES = ['datastore','data','examples','functions','graph']

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    url = "http://bdo.water.ca.gov",
    description='time sereies data visulizing tools',
    #long_description = get_description(),
    author="Eli Ateljevich, Qiang Shu",
    author_email="eli@water.ca.gov",
    license="PSF or ZPL",
    install_requires = ['Traits>=3.0'],
    #test_suite = 'test_assembler',
    packages=find_packages(),
    namespace_packages=find_packages(),

    package_data={"":["doc/*.*","doc/html/*.*","*.pyd"],
                  "vtools.examples.graph":["*.txt"],
                  "vtools.graph":["formats/*.txt"]
                 },
    exclude_package_data = {'': ['*.pyc','*.pyo']},
    entry_points = {
        'console_scripts': [
            'transfer = vtools.datastore.transfer:main'
        ]}
)

print find_packages()