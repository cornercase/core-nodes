# Copyright (c) 2014, Dignity Health
# 
#     The GPI core node library is licensed under
# either the BSD 3-clause or the LGPL v. 3.
# 
#     Under either license, the following additional term applies:
# 
#         NO CLINICAL USE.  THE SOFTWARE IS NOT INTENDED FOR COMMERCIAL
# PURPOSES AND SHOULD BE USED ONLY FOR NON-COMMERCIAL RESEARCH PURPOSES.  THE
# SOFTWARE MAY NOT IN ANY EVENT BE USED FOR ANY CLINICAL OR DIAGNOSTIC
# PURPOSES.  YOU ACKNOWLEDGE AND AGREE THAT THE SOFTWARE IS NOT INTENDED FOR
# USE IN ANY HIGH RISK OR STRICT LIABILITY ACTIVITY, INCLUDING BUT NOT LIMITED
# TO LIFE SUPPORT OR EMERGENCY MEDICAL OPERATIONS OR USES.  LICENSOR MAKES NO
# WARRANTY AND HAS NOR LIABILITY ARISING FROM ANY USE OF THE SOFTWARE IN ANY
# HIGH RISK OR STRICT LIABILITY ACTIVITIES.
# 
#     If you elect to license the GPI core node library under the LGPL the
# following applies:
# 
#         This file is part of the GPI core node library.
# 
#         The GPI core node library is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version. GPI core node library is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
# 
#         You should have received a copy of the GNU Lesser General Public
# License along with the GPI core node library. If not, see
# <http://www.gnu.org/licenses/>.


# Author: Nick Zwart
# Date: 2013 Oct 30

import gpi
from gpi import QtCore, QtGui

import numpy as np
from matplotlib.figure import Figure
#from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)


class MatplotDisplay(gpi.GenericWidgetGroup):

    """Combines the BasicCWFCSliders with ExclusivePushButtons
    for a unique widget element useful for reduce dimensions.
    """
    valueChanged = gpi.Signal()

    def __init__(self, title, parent=None):
        super(MatplotDisplay, self).__init__(title, parent)

        #self.data = self.get_data2()
        self._data = None
        self.create_main_frame()
        self.on_draw()

    # setters
    def set_val(self, data):
        '''Takes a list of npy arrays.
        '''
        if isinstance(data, list):
            self._data = data
            self.on_draw()
        else:
            return

    # getters
    def get_val(self):
        return self._data

    # support
    def create_main_frame(self):

        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self)

        self.canvas.mpl_connect('key_press_event', self.on_key_press)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)  # the matplotlib canvas
        vbox.addWidget(self.mpl_toolbar)
        self.setLayout(vbox)

    #def get_data2(self):
    #    return np.arange(20).reshape([4, 5]).copy()

    def on_draw(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        # self.axes.plot(self.x, self.y, 'ro')
        # self.axes.imshow(self.data, interpolation='nearest')
        # self.axes.plot([1,2,3])

        if self._data is None:
            return

        self.fig.hold(True)

        # plot each set
        # print "--------------------plot the data"
        for data in self._data:

            # check for x, y data
            if data.shape[-1] == 2:
                self.axes.plot(data[..., 0], data[..., 1], alpha=0.8, lw=2.0)
            else:
                self.axes.plot(data, alpha=0.8, lw=2.0)

        self.canvas.draw()

    def on_key_press(self, event):
        # print 'Matplotlib-> you pressed:' + str(event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-
        # keyboard-shortcuts
        try:
            from matplotlib.backend_bases import key_press_handler
            key_press_handler(event, self.canvas, self.mpl_toolbar)
        except:
            print "key_press_handler import failed. -old matplotlib version."


class ExternalNode(gpi.NodeAPI):

    """A Qt embedded plot window using the code from: 
    http://matplotlib.org/examples/user_interfaces/embedding_in_qt4_wtoolbar.html
    keyboard shortcuts can be found here:
    http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts

    INPUTS
    Up to 8 data sets can be plotted simultaneously
      1D real-valued data are plotted as graph
      2D data where the 2nd dimension is 2 will be plotted as X-Y parametric plot, otherwise
      all other 2D data are plotted as series of 1D plots
    """

    def initUI(self):
        # Widgets
        self.addWidget('MatplotDisplay', 'Plot')

        # IO Ports
        self.inport_range = range(0, 8)
        for i in self.inport_range:
            self.addInPort('in' + str(i), 'NPYarray', obligation=gpi.OPTIONAL)

    def compute(self):

        # check input ports for data
        in_lst = [self.getData('in' + str(i))
                  for i in self.inport_range if self.getData('in' + str(i)) is not None]

        self.setAttr('Plot', val=in_lst)

        return 0

    def execType(self):
        '''Could be GPI_THREAD, GPI_PROCESS, GPI_APPLOOP'''
        return gpi.GPI_APPLOOP
