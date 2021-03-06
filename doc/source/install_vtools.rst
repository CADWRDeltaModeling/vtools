.. _install_vtools

Getting and Installing VTools
=============================


Prerequisites
-------------

If you want HEC-DSS functionality, you will need pydss, our Python bindings for the HEC-DSS storage format. The package
is currently only available for Windows and in binaries, linked to the binary library with permission from the Hydrologic Engineering Center. Our portion of the code is offered using an MIT license. Linux will be supported.

`pydss installer (Python 2.7, Windows 64 bit) <https://msb.water.ca.gov/documents/86683/266737/pydss_0.8_py2.7_amd64.exe>`_

VTools makes extensive use of numpy, scipy as well as interfaces to data sources. There is a trend now with python towards fully featured scientific distrubtions, and we don't particularly recommend trying to build up a full featured tool a la carte. To that end, we recommend the `Anaconda <https://store.continuum.io/cshop/anaconda/>`_ distribution. One of the main developers on our time has also used Python(x,y). 

VTools Install
--------------
VTools is installed via a python "egg". The vtools egg available here:
  
  - `vtools-1.1-py2.7.egg (Python 2.7, Windows 64 bit) <https://msb.water.ca.gov/documents/86683/266737/vtools-1.1-py2.7.egg>`_
  - `vtools-1.0-py2.7_win32.egg (Python 2.7, Windows 32 bit) <https://msb.water.ca.gov/documents/86683/266737/vtools-1.0-py2.7_win32.egg>`_

Use the command::

  $ easy_install vtools-1.1-py2.7.egg

Version 2.7 of Python is currently supported in 32 or 64 bit flavors. We will make the jump to 3.x when it is fully supported in ArcGIS.

VTools is offered under the MIT license. You should receive a copy of the license with the package.

PyDSS
-----
If you want to use VTools with HEC-DSS data, you will need PyDSS. PyDSS is also licensed under the MIT license.
We are redistributing the HEC-DSS library with permission from the Hydrologic Engineering Center and don't have explicit permission to distribute their source code. Currently we only have a Windows Build.

  - `pydss_0.8_py2.7_win32.exe <https://msb.water.ca.gov/documents/86683/266737/pydss_0.8_py2.7_win32.exe>`_
  - `pydss_0.8_py2.7_amd64.exe <https://msb.water.ca.gov/documents/86683/266737/pydss_0.8_py2.7_amd64.exe>`_
