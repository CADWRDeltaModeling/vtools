.. _install_vtools

Installing vtools
=================

VTools can be installed from the vtools egg available from the `Delta Modeling Section  Tools`_ website. 

.. _Delta Modeling Section Tools: http://baydeltaoffice.water.ca.gov/modeling/deltamodeling/deltaevaluation.cfm

Only version 2.7 of Python is currently supported in 32 or 64 bit flavors. We will make the jump to 3.x when it is fully supported in ArcGIS.


Prerequisites
-------------
VTools makes extensive use of numpy, scipy as well as interfaces to data sources. There is a trend now with python towards fully featured scientific distrubtions, and we don't particularly recommend trying to build up a full featured tool a la carte. To that end, we recommend the `Anaconda <https://store.continuum.io/cshop/anaconda/>`_ distribution. One of the main developers on our time has also used Python(x,y). 


Building from source
--------------------
The source code is available from GitHub. VTools is offered under the BSD license. PyDSS is also included and is fully tested with several versions of the DSS library. Note, however, that we are redistributing the HEC-DSS license with permission from the Hydrologic Engineering Center and don't have explicit permission to distribute their source code.

VTools relies on native code for provision of the DSS interface.

