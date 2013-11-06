""" Sample script for creating and using datetimes and time intervals
"""
# Imports
#from vtools.data import *
from vtools.data.vtime import *

# Creating a datetime
t0=datetime(1994,1,1,14,0) # 01JAN1994 14:00

# Parsing a datetime
t1=parse_time("01Jan1990 00:00")
t1=parse_time("01Jan1990")
t1=parse_time("01-01-1990 14:30")


# Formatting a datetime
t0.strftime("Time=%d%b%Y %H:%M") # 'Time=01Jan1994 14:00'
t0.strftime("%c")                # '01/01/94 14:00:00' %c=full representation'
t0.strftime("Time=%d%b%Y %H:%M") # 'Time=01Jan1994 14:00'
t0.strftime("%m/%d/%y")          # '01/01/94'


# Some useful calendar ops
import calendar
t0=datetime(1994,1,1,14,0)
calendar.isleap(t0.year)     # test is 1994 a leap year (True/False)
calendar.leapdays(1994,2008) # number of leapdays in range
                             # (be careful of range convention)
calendar.mdays[3]            # days per month: a list not a function 


# Creating a time interval using helper functions
# This is easiest when you know what you have to create
intvl=seconds(15)
intvl=minutes(15)
intvl=hours(12)
intvl=days(1)
intvl=months(1)
intvl=years(4)

# Creating a time interval using the time_interval function
# time_interval(years=0,months=0,days=0,hours=0,minutes=0,seconds=0)
intvl=time_interval(months=1)
intvl=time_interval(0,0,1)      # 1 day

# Creating a time interval using a string
intvl=parse_interval("1sec")
intvl=parse_interval("1SEC")
intvl=parse_interval("1min")
intvl=parse_interval("1hour")
intvl=parse_interval("1day")
intvl=parse_interval("1mon")
intvl=parse_interval("1year")

# Time interval arithmetic
t=datetime(1994,1,1)
t=t+days(1) # or equivalently t+=days(1)
intvl=months(1)
#t=t+2*intvl  # this case is a known bug - causes exception

# Test if an object is an interval
# Returns true if the object is of the correct class
# for VTools (which you shouldn't test directly).
obj=minutes(15)
isintvl=is_interval(obj)

# Test if an interval is calendar dependent
cd = is_calendar_dependent(intvl)

# Convert between datetime and a numerical value used, say,
# in a time series. You won't use this much.
t=datetime(1994,1,1)
tk=ticks(t)

# Aligning an interval to make it "neat"
t=datetime(1994,1,1,1,17) # 01JAN1994 01:17
t=align(t,minutes(15),-1) # 01JAN1994 01:15
t=align(t,minutes(15),1)  # 01JAN1994 01:30
t=align(t,days(1),-1)     # 01JAN1994 00:00









