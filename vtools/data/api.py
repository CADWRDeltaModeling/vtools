"""As with all the vtools packages, the api module doesn't have original data or functions. 
   The purpose of this module is so that you can import key variables in :mod:`vtools.data` all at once:
::
    from vtools.data.api import * # all the "public" items in vtime and timeseries.

"""

from .vtime import *
from .timeseries import *
from .sample_series import *

