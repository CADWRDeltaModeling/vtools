""" The entry point for an Envisage application. """


# Standard library imports.
import sys,pdb


# Enthought library imports.
from enthought.envisage.workbench.api import WorkbenchApplication
from enthought.pyface.api import GUI, ImageResource, SplashScreen


# Local imports.
from plugin_definitions import PLUGIN_DEFINITIONS

def run(argv=sys.argv):
    """ Runs the application. """

    # Create a GUI and put up the splash screen.
    gui = GUI(
        splash_screen = SplashScreen(
            image         = ImageResource('splash'),
            text_location = (5, 5),
            #text_color    =  'black'
        )
    )

    # Create the Envisage application.
    application = WorkbenchApplication(
        argv               = argv,
        gui                = gui,
        id                 = 'vtools.datasotre.test',
        plugin_definitions = PLUGIN_DEFINITIONS
    )

    # Run the application.
    #
    # This starts the application, starts the GUI event loop, and when that
    # terminates, stops the application.

    application.run()

    return


# Application entry point.
if __name__ == '__main__':
    run()

#### EOF ######################################################################
