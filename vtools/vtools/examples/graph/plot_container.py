""" Draws several line plots """
from vtools.graph.api import *
from vtools.data.api import *
from vtools.data.sample_series import create_sample_series
from ts_scatter import create_scatter_data
from enthought.chaco2.api import VPlotContainer,HPlotContainer

palette=get_palette("default")

# Obtain sample data
ts0,ts1,ts2,ts3 = create_sample_series()

# Create a vertical plot container
vcontainer=VPlotContainer(stack_order="top_to_bottom",padding=0)
vcontainer.bgcolor="lightslategrey"

# Create a time series plot and add it
p0 = ts_plot(ts0,"ts0",color=palette[0])
p0.padding_bottom=30
p0.bgcolor="transparent"
vcontainer.add(p0)

# Create another plot that has two plots
# (note this is OverlayPlotContainer working
# behind the scenes. Add it to the outer container
p1 = ts_plot(ts1,"ts1",color=palette[0])
p1 = ts_plot(ts2,"ts2",plot_area=p1,color=palette[5])
p1.padding_bottom=30
p1.padding_top=10
p1.bgcolor="transparent"
vcontainer.add(p1)

# We will put two plots side by side on the bottom
# Create a horizontal container
hcontainer=HPlotContainer(padding=0)

# Create a scatter plot and add them to the horizontal container
sd0,sd1=create_scatter_data()
s1=ts_scatter(sd0,sd1,["x_data","y_data"],
                    color=(.2,.44,.802),   # fractional RGB, see plot_format.py
                    marker="diamond",
                    marker_size=3)
s1.bgcolor="transparent"
hcontainer.add(s1)
s1.bgcolor="transparent"
s2 = ts_plot(ts3,"ts3",color=palette[0])
s2.x_axis.tick_label_formatter.date_format="%d%b%y"
s2.bgcolor="transparent"
#Change the date format on the x axis to eliminate time
p0.x_axis.tick_label_formatter.date_format="%d%b%Y"
hcontainer.add(s2)
hcontainer.bgcolor="transparent"

# Add the horizontal container at the bottom of the outer
# vertical container
vcontainer.add(hcontainer)

# Now save the layout to a file
save_image_file(vcontainer,"ts_line.gif")

# Now get a frame to display it live
fig=default_frame(vcontainer,size=(800,600))
display_frame(fig)




# EOF
