"""Examples of cataloging a dss data source, view
   its entries, and item contains within a entry.
"""

## import necessary vtools lib.
from vtools.datastore.dss.dss_catalog import *

## giving a existing datasource.
source="mustexist.dss"

## call funcs to create a data catalog.
c=dss_catalog(source)


## use for loop to print string representation
## of each entry.
for e in c:
    print e
   ## to find out what items
   ##contained within a single 
   ## entry
    print e.item_names()
   ## to view a specific item
    print e.item('item_name')

## to print a string representation of
## whole catalog, use function catalog_string
from vtools.datastore.catalog import *
print catalog_string(c)


## comment: such example can be applied on
## hdf5 data source also, with except of
## changing function 'dss_catalog' to
## 'hdf_catalog' and changing import command
## at line 6 to 'from vtools.datastore.hdf5.api
## import *'
