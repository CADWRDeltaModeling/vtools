
from enthought.chaco2.api import PlotGraphicsContext

def save_image_file(component, filename,size=None):

    """ Save plot component to an image file
        Saves a plot component (e.g. Plot produced by ts_plot 
        or ts_scatter, or a VPlotContainer, it must have attribute
        outer_bounds and outer_location.) to an
        image file inferred from the extension in filename
    """
    if not size:
        if hasattr(component,"bounds") and component.bounds[0] > 0:
            size=component.bounds
        else:
            size=(600,400)
    component.bounds=list(size)
    component.outer_bounds=component.bounds
    component.do_layout(force=True)
    plot_gc = PlotGraphicsContext((size[0]+1,size[1]+1))
    plot_gc.render_component(component)
    plot_gc.save(filename)
    return
    

