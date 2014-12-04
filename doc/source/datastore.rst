Getting data in and out of vtools
====================================

Data stores in vtools
---------------------
The datastore package defines a uniform API for listing entries to a data source and retrieving data. A data source is usually a file, but as we expand it could be a URL or database name. 

VTools was designed to avoid having a singe native database or storage system, although
its implementation continues to be the HEC-DSS storage system, a somewhat older univariate time series data storage library from the Hydraulic Engineering Center of the Army Corps of Engineers. A companion product, PyDSS, is a complete set of bindings for DSS that has been tested for Python 2.7 in Windows 32 and 64 bit flavors and is expected to come out for Linux in the next year.

In the past we offered Excel and DSM2 HDF5 tidefiles as add-on modules. We have not included them in the base release, but if we find there is demand we can restore them.

NetCDF has become more clearly pre-emininent and for storing
array data and it places greater emphasis on the need for differentiating
multivariate data from multiple instances (stations) of univariate time series.

Text file support such as CDEC, NOAA and USGS *.rdb format was developed as part of the Bay-Delta SELFE project. It uses VTools time series and will be moved to vtools once 
unit test coverage and handling of metadata is more complete.


Timestamps and Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^
Different data sources have different conventions with regard to how they annotate 
things like units and time stamps. These metadata are converted to a common standard on import and 
converted back on export.

A good example is period averaged data, which has to be marked as a period average and
also is associated with a timestamp convention, usually  at the beginning or end of period. Usage and convention is pretty fixed. For instance, HEC-DSS period averaged data is almost always "post-stamped". To the best of our knowledge HEC-DSS has no metadata to confirm this stamping convention or allow you to specify you have changed it, so convention is the best we can do and changing practice would exacerbate
confusion.

VTools has its own conventions. For instance, period averaged data is a assumed to be stamped at the beginning of the period which allows for intuitive labeling
and avoids some of the overhead defining what February 28 plus one month means. VTools re-stamps HEC-DSS data to the beginning of the period on import and restores it to the end of the period on export.


Loading and storing data using simple utility functions
---------------------------------------------------------

Data sources are supposed to also provide xxx_retrieve_ts and xxx_store_ts functions as
simple utilities for fetching data. The retrieval function takes the name of the
data source, the path/view of the data and a time window as its argument. The store 
function takes just the data plus a source and path.

Here is an example of how to get data from a HECDSS file::

    from vtools.datastore.dss.api import *
    from vtools.functions.api import *
    from vtools.data.api import *
    file = "hist19902014_droughtstudy.dss"
    ts = dss_retrieve_ts(file,selector="B=RSAC054 C=EC F=DWR-DMS-201402_CU5",unique=True)

and for storing::

    ts2=period_ave(ts,days(1))
    out = "out.dss"
    dss_store_ts(ts2,out,"/SAMPLE/DATA/EC//${INTERVAL}/FPART/") # interval will be filled in

Catalogs
--------
    
Catalogs and Catalog Items
^^^^^^^^^^^^^^^^^^^^^^^^^^
A :class:`~vtools.datastore.catalog.Catalog`  is essentially a container of :class:`~vtools.datastore.catalog.CatalogEntry`. It
provides for the retrieval, alteration or removal of catalog entries, inasmuch as those actions make sense on the service.

One usually gets a catalog using a catalog service which will track 
open files and guard against conflicting or redundant actions. The
actions are threadsafe inasmuch as the underlying system is threadsafe.

A catalog item combines a unique identifier with metadata and scale information. It is acceptable for that data to be retrieved lazily if
this speeds the implementation. For instance, some HEC-DSS metadata is
not really stored in the DSS Catalog, but rather with the series.

Data References
^^^^^^^^^^^^^^^
A data reference is a reference to both the data source, identifier of the data within
that source (path) and any slicing (e.g., time window).



