# Copyright (C) 2017  DESY, Christoph Rosemann, Notkestr. 85, D-22607 Hamburg
#
# lavue is an image viewing program for photon science imaging detectors.
# Its usual application is as a live viewer using hidra as data source.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 2
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
#
# Authors:
#     Christoph Rosemann <christoph.rosemann@desy.de>
#     Jan Kotanski <jan.kotanski@desy.de>
#

""" transformation widget """


from PyQt4 import QtCore, QtGui, uic
import os

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "TransformationsWidget.ui"))


class TransformationsWidget(QtGui.QWidget):
    """
    Select how an image should be transformed.
    """

    #: (:class:`PyQt4.QtCore.pyqtSignal`) transformation changed signal
    transformationChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`PyQt4.QtCore.QObject`
        """
        QtGui.QWidget.__init__(self, parent)

        #: (:class:`Ui_TransformationsWidget') ui_widget object from qtdesigner
        self.__ui = _formclass()
        self.__ui.setupUi(self)

        self.__ui.comboBox.currentIndexChanged.connect(
            self._onTransformationChanged)

    @QtCore.pyqtSlot(int)
    def _onTransformationChanged(self, index):
        """ updates transformation according to the index

        :param state: transformation index
        :type state: :obj:`int`
        """
        self.transformationChanged.emit(
            self.__ui.comboBox.itemText(index))

    def setEnable(self, flag):
        """ disables or enables the combobox

        :param flag: combobox to be enabled
        :type flag: :obj:`bool`
        """
        self.__ui.comboBox.setEnable(flag)
        if not flag:
            self.__ui.comboBox.setCurrentIndex(0)

    def setKeepCoordsLabel(self, flag):
        """ sets keep original coordinates label according to flag

        :param flag: keep original coordinates flag
        :type flag: :obj:`bool`
        """
        if flag:
            self.__ui.keepcoordsLabel.setText("Keep original cooridnates!")
        else:
            self.__ui.keepcoordsLabel.setText("Transform also coordinates!")
            
