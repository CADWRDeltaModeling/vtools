

class ExcelFormatEntry(Object):
    """ A helper class to store Excel stroing
        and retrieving format setting.
    """

    def __init__(self):
        self.ts_type=None
        self.time=None
        self.header=None
        self.write_times=None
        self.interval=None
        self.start=None

def ExcelFormat(ts_type="rts",time="auto",header=None,write_times=True,\
                interval=None,start=None,header_labels=None):
    
    result=ExcelFormatEntry()
    self.ts_type=ts_type
    self.time=time
    self.header=header
    self.header_labels=header_labels
    self.write_times=write_times
    self.interval=interval
    self.start=start
    