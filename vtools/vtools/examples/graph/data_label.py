""" Draws several line plots """
from vtools.graph.api import *
from vtools.data.api import *
from vtools.data.sample_series import create_sample_series
from enthought.chaco2.api import DataLabel

# Obtain sample data
ts0,ts1,ts2,ts3 = create_sample_series()

# Simple time series plot. Note you don't really have to put
# plot_area=None. This is the default, and it means that the output
# will be a new plot area.
p0 = ts_plot(ts0,"ts0",plot_area=None,color="red",line_style="long dash")


# Now we are reusing the plot area and plotting another time series on
# top of the first.
p0 = ts_plot(ts1,"ts1",plot_area=p0,color="blue")

# Now lets place a label on t0 corresponding to eight months
# after the start of ts1
index=ts1.index_before(ts1.start+months(8))
xloc=ts1[index].ticks
yloc=ts1[index].value

# Create the label. Only the first three lines are required.
label=DataLabel(lines=["Here is a label","pointing to text"],
                data_point=(xloc,yloc),
                component=p0,
                label_position="top right",
                padding=40,
                bgcolor = "antiquewhite",
                border_visible=True,
                border_padding=6,
                line_spacing=4,
                draw_arrow=True)

# You can also change the label after it is created
label.marker_size=3
label.marker_line_width=2.0
label.marker_color="lightblue"
label.arrow_size = 5 # arrow head
label.arrow_color="red"
label.arrow_root = "auto" # position of base of arrow. "top left", "bottom right"
                          # auto just uses label_position to decide this

p0.overlays.append(label)              
p0.legend.visible = True

# Now save the plot to a file
#save_image_file(p0,"ts_line.gif")

# Now get a frame to display it live
fig=default_frame(p0,size=(600,400))
display_frame(fig)



# EOF
