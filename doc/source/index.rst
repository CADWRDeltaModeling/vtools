.. vtools documentation master file, created by
   sphinx-quickstart on Fri Nov 15 21:20:59 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================
Introduction
=================
Welcome to the vtools documentation page. Vtools is a package we use to perform time-aligned operations on time series, as well as some specialty analyses encountered in hydrology and hydrodynamic work and modeling. It provides some of the index-aligned power of `pandas <http://pandas.sourceforge.net/>`_ as ways to transfer data around between formats. 

There are other projects much larger than vtools that are important in this problem domain. We think these are great and our goal is mostly to stay out of their way and interface well with tools like `pandas <http://pandas.sourceforge.net/>`_ and the non-python `R <http://www.r-project.org/>`_. Most of our dimension concepts are migrating towards netcdf model in `netcdf4-python <http://code.google.com/p/netcdf4-python/>`_. We also owe a lot to the legacy format HEC-DSS from the Hydrologic Engineering Center of the Army Corps of Engineers. HEC-DSS is antiquated, hardwired to univariate data and uses odd conventions for time, but DSS has been relevent for decades and `HEC-DSSVUE <http://www.hec.usace.army.mil/software/hec-dssvue/>`_ is still the free graphical time series manipulation tool most familiar to people in our community (and it has some scripting tools for jython).

OK, so if you are still wondering what vtools would be good at doing, here are some examples:
  * Tabulate and create a bar chart of the climatology of a river (calendar or seasonal average flow).
  * Extract two time series from DSS, tidally filter them with a Butterworth-squared filter, and plot them against a time series of gate openings using recipes for matplotlib.
  * Write a command on the windows command line that extracts every series from one datasource, performs a transformation and writes it all to a new data store mapping the attributes in a simple way.
  * Extract model and observed data and plot the two in a multi-plot (tidal and filtered, say) figure using matplotlib. Mostly we provide the ability to do the extraction and analysis plus a number of recipes for matplotlib.

====================
Documentation 
====================
Learning vtools is something you can mostly learn by example, so most of the topics below are coding examples with a few explanations. There is some traditional api documentation as well.


Contents
--------

.. toctree::
   :maxdepth: 2

   Installing vtools <install_vtools>
   Time and time series concepts <timeseries>
   Functions <vtools_functions>
   Getting data in and out of vtools <datastore>
   Plotting recipes <plotting>


Test of inline class doc
------------------------
See :class:`~vtools.data.timeseries.TimeSeries`

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

