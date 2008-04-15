
## local import
from zoom_overlay import ZoomOverlay
## chaco import
from enthought.chaco2.tools.api import RangeSelection

def zoom_connect(p1,p2,source_name,dest_name):
    
    p1.plots[source_name][0].controller=RangeSelection(p1.plots[source_name][0])
    zoom_overlay = ZoomOverlay(source=p1.plots[source_name][0], \
                               destination=p2.plots[dest_name][0])        
    return zoom_overlay