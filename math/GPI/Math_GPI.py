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


# Author: Ryan Robison
# Date: 2013jun28

import numpy as np
import gpi


class ExternalNode(gpi.NodeAPI):
    """Perform real or complex scalar operations on a per element basis.
       Three Modes of Operation:
        1) Standard - basic Arithmetic and exponential operations.
        2) Trigonometric - basic Trigonometric operations.
        3) Comparison - returns maximum, minimum, or bit mask based on
                        comparison between inputs or against Scalar.

       Operations which do not commute (e.g. divide) operate left to right, e.g.:
         output = (left port) / (right port)
    """

    def initUI(self):

        # Widgets
        self.inputs = 0
        self.addWidget('ExclusivePushButtons', 'Mode', buttons=[
                       'Standard', 'Trigonometric', 'Comparison'], val = 0)
        self.addWidget('ExclusiveRadioButtons', 'Operation', buttons=[
                       'Add', 'Subtract', 'Multiply', 'Divide', 'Power',
                       'Exponential', 'LogN', 'Log10', 'Reciprocal', 
                       'Conjugate', 'Magnitude', 'Sin', 'Cos', 'Tan', 'arcSin', 'arcCos',
                       'arcTan', 'arcTan2', 'Max', 'Min', '>', '<', '==',
                       '!=', '>=', '<='],
                       val=0)
        self.addWidget('DoubleSpinBox', 'Scalar', val=0.0, decimals = 5)
        self.addWidget('PushButton', 'compute', toggle=True, val=1)

        # IO Ports
        self.addInPort('inLeft', 'NPYarray', obligation=gpi.OPTIONAL)
        self.addInPort('inRight', 'NPYarray', obligation=gpi.OPTIONAL)
        self.addOutPort('out', 'NPYarray')

        # operations
        self.op = [np.add, np.subtract, np.multiply, np.divide, np.power,
                   np.exp, np.log, np.log10, np.reciprocal, np.conj, np.abs,
                   np.sin, np.cos, np.tan, np.arcsin, np.arccos, np.arctan,
                   np.arctan2, np.maximum, np.minimum, np.greater, np.less,
                   np.equal, np.not_equal, np.greater_equal, np.less_equal]

    def validate(self):
        '''update the widgets based on the input arrays
        '''

        data1 = self.getData('inLeft')
        data2 = self.getData('inRight')

        if (set(self.portEvents()).intersection(set(['inLeft','inRight'])) or
            'Mode' in self.widgetEvents()):
            self.func = self.getVal('Mode')
            if (data1 is None and data2 is None):
                self.inputs = 0
            elif (data1 is None or data2 is None):
                self.inputs = 1
            else:
                self.inputs = 2

        if self.inputs is 2:
            if self.func is 0:
                self.setAttr('Operation', buttons=['Add', 'Subtract',
                                  'Multiply', 'Divide', 'Power'])
                self.op = [np.add, np.subtract, np.multiply, np.divide,
                           np.power]
            elif self.func is 1:
                self.setAttr('Operation', buttons=['arcTan2'])
                self.op = [np.arctan2]
            else:
                self.setAttr('Operation', buttons=['Max', 'Min', '>',
                                  '<', '==', '!=', '>=', '<='])
                self.op = [np.maximum, np.minimum, np.greater, np.less,
                           np.equal, np.not_equal, np.greater_equal,
                           np.less_equal]
        elif self.inputs is 1:
            if self.func is 0:
                self.setAttr('Operation', buttons=['Add', 'Subtract',
                                  'Multiply', 'Divide', 'Power', 'Exponential',
                                  'LogN', 'Log10', 'Reciprocal', 'Conjugate',
                                  'Magnitude'])
                self.op = [np.add, np.subtract, np.multiply, np.divide, np.power,
                           np.exp, np.log, np.log10, np.reciprocal, np.conj,
                           np.abs]
            elif self.func is 1:
                self.setAttr('Operation', buttons=['Sin', 'Cos', 'Tan',
                                  'arcSin', 'arcCos', 'arcTan'])
                self.op = [np.sin, np.cos, np.tan, np.arcsin, np.arccos,
                           np.arctan]
            else:
                self.setAttr('Operation', buttons=['>', '<', '==', '!=',
                                  '>=', '<='])
                self.op = [np.greater, np.less, np.equal, np.not_equal,
                           np.greater_equal, np.less_equal]

        if self.getVal('Operation') > len(self.op):
            self.setAttr('Operation', val=0)
        operation = self.op[self.getVal('Operation')]
        if (self.inputs is 1 and
            operation in [np.add, np.subtract, np.multiply, np.divide,
                          np.power, np.greater, np.less, np.equal,
                          np.not_equal, np.greater_equal, np.less_equal]):
            self.setAttr('Scalar', visible=True)
        else:
            self.setAttr('Scalar', visible=False)
        return(0)

    def compute(self):

        import numpy as np

        data1 = self.getData('inLeft')
        data2 = self.getData('inRight')
        operation = self.op[self.getVal('Operation')]

        if self.getVal('compute'):
            if operation in [np.add, np.subtract, np.multiply, np.divide,
                             np.power, np.greater, np.less, np.equal,
                             np.not_equal, np.greater_equal, np.less_equal]:
                scalar = self.getVal('Scalar')
            else:
                scalar = None

            try:
                if self.inputs is 2:
                    out = operation(data1, data2)
                elif data1 is not None:
                    out = operation(data1, scalar)
                elif data2 is not None:
                    out = operation(data2, scalar)

                if self.inputs is not 0:
                    self.setData('out', out)
            except:
                return 1
        return(0)

    def execType(self):
        '''Could be GPI_THREAD, GPI_PROCESS, GPI_APPLOOP'''
        return gpi.GPI_PROCESS
