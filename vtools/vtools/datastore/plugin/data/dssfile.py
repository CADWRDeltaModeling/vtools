

from enthought.traits import HasTraits, Str, Int
from enthought.traits.ui import View, Item, Group
    
class DssFile(HasTraits):
    name = Str
    
    
    my_view = View(
        Item('name', width=300)
        )
    