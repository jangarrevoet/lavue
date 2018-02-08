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

""" image display widget """

import pyqtgraph as _pg
import numpy as np
import math
from pyqtgraph.graphicsItems.ROI import ROI, LineROI
from PyQt4 import QtCore, QtGui

VMAJOR, VMINOR, VPATCH = _pg.__version__.split(".") \
    if _pg.__version__ else ("0", "9", "0")


class SimpleLineROI(LineROI):
    def __init__(self, pos1, pos2, **args):
        pos1 = _pg.Point(pos1)
        pos2 = _pg.Point(pos2)
        d = pos2 - pos1
        l = d.length()
        ang = _pg.Point(1, 0).angle(d)

        ROI.__init__(self, pos1, size=_pg.Point(l, 1), angle=ang, **args)
        self.addScaleRotateHandle([0, 0.5], [1, 0.5])
        self.addScaleRotateHandle([1, 0.5], [0, 0.5])

    def getCoordinates(self):
        ang = self.state['angle']
        pos1 = self.state['pos']
        size = self.state['size']
        ra = ang * np.pi / 180.
        pos2 = pos1 + _pg.Point(
            size.x() * math.cos(ra),
            size.x() * math.sin(ra))
        return [pos1.x(), pos1.y(), pos2.x(), pos2.y()]


class ImageDisplayWidget(_pg.GraphicsLayoutWidget):

    currentMousePosition = QtCore.pyqtSignal(QtCore.QString)
    centerAngleChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        _pg.GraphicsLayoutWidget.__init__(self, parent)
        self.__layout = self.ci

        #: (:obj:`tuple` <:obj:`float`, :obj:`float`> ) image scale (x,y)
        self.scale = None
        #: (:obj:`tuple` <:obj:`float`, :obj:`float`> )
        #    position of the first pixel
        self.position = None
        #: (:obj:`str`) label of x-axis
        self.xtext = None
        #: (:obj:`str`) label of y-axis
        self.ytext = None
        #: (:obj:`str`) units of x-axis
        self.xunits = None
        #: (:obj:`str`) units of y-axis
        self.yunits = None

        self.roienable = False
        self.currentroi = 0
        self.roicoords = [[10, 10, 60, 60]]

        self.cutenable = False
        self.currentcut = 0
        self.cutcoords = [[10, 10, 60, 10]]

        self.qenable = False
        #: (:obj:`float`) x-coordinates of the center of the image
        self.centerx = 0.0
        #: (:obj:`float`) y-coordinates of the center of the image
        self.centery = 0.0
        #: (:obj:`float`) energy in eV
        self.energy = 0.0
        #: (:obj:`float`) pixel x-size in um
        self.pixelsizex = 0.0
        #: (:obj:`float`) pixel y-size in um
        self.pixelsizey = 0.0
        #: (:obj:`float`) detector distance in mm
        self.detdistance = 0.0
        #: (:obj:`int`) geometry space index -> 0: angle, 1 q-space
        self.gspaceindex = 0

        self.dobkgsubtraction = False
        self.statswoscaling = False
        self.scaling = "sqrt"

        self.data = None
        self.rawdata = None

        self.image = _pg.ImageItem()

        self.__viewbox = self.__layout.addViewBox(row=0, col=1)
        self.__crosshairlocked = False
        self.__viewbox.addItem(self.image)
        self.__xdata = 0
        self.__ydata = 0
        self.__autodisplaylevels = True
        self.__displaylevels = [None, None]

        self.setaspectlocked = QtGui.QAction(
            "Set Aspect Locked", self.__viewbox.menu)
        self.setaspectlocked.setCheckable(True)
        if VMAJOR == '0' and int(VMINOR) < 10 and int(VPATCH) < 9:
            self.__viewbox.menu.axes.insert(0, self.setaspectlocked)
        self.__viewbox.menu.addAction(self.setaspectlocked)

        self.__viewonetoone = QtGui.QAction(
            "View 1:1 pixels", self.__viewbox.menu)
        self.__viewonetoone.triggered.connect(self.oneToOneRange)
        if VMAJOR == '0' and int(VMINOR) < 10 and int(VPATCH) < 9:
            self.__viewbox.menu.axes.insert(0, self.__viewonetoone)
        self.__viewbox.menu.addAction(self.__viewonetoone)

        self.__leftaxis = _pg.AxisItem('left')
        self.__leftaxis.linkToView(self.__viewbox)
        self.__layout.addItem(self.__leftaxis, row=0, col=0)

        self.__bottomAxis = _pg.AxisItem('bottom')
        self.__bottomAxis.linkToView(self.__viewbox)
        self.__layout.addItem(self.__bottomAxis, row=1, col=1)

        self.__layout.scene().sigMouseMoved.connect(self.mouse_position)
        self.__layout.scene().sigMouseClicked.connect(self.mouse_click)

        self.__vLine = _pg.InfiniteLine(
            angle=90, movable=False, pen=(255, 0, 0))
        self.__hLine = _pg.InfiniteLine(
            angle=0, movable=False, pen=(255, 0, 0))
        self.__viewbox.addItem(self.__vLine, ignoreBounds=True)
        self.__viewbox.addItem(self.__hLine, ignoreBounds=True)

        self.__roi = []
        self.__roi.append(ROI(0, _pg.Point(50, 50)))
        self.__roi[0].addScaleHandle([1, 1], [0, 0])
        self.__roi[0].addScaleHandle([0, 0], [1, 1])
        self.__viewbox.addItem(self.__roi[0])
        self.__roi[0].hide()

        self.__cut = []
        self.__cut.append(SimpleLineROI([10, 10], [60, 10], pen='r'))
        self.__viewbox.addItem(self.__cut[0])
        self.__cut[0].hide()

    def showLines(self, status):
        if status:
            self.__vLine.show()
            self.__hLine.show()
        else:
            self.__vLine.hide()
            self.__hLine.hide()

    def setAspectLocked(self, flag):
        if flag != self.setaspectlocked.isChecked():
            self.setaspectlocked.setChecked(flag)
        self.__viewbox.setAspectLocked(flag)

    def addItem(self, item, **args):
        self.image.additem(item)

    def addROI(self, coords=None):
        if not coords or not isinstance(coords, list) or len(coords) != 4:
            pnt = 10 * len(self.__roi)
            sz = 50
            coords = [pnt, pnt, pnt + sz, pnt + sz]
            spnt = _pg.Point(sz, sz)
        else:
            pnt = _pg.Point(coords[0], coords[1])
            spnt = _pg.Point(coords[2] - coords[0], coords[3] - coords[1])
        self.__roi.append(ROI(pnt, spnt))
        self.__roi[-1].addScaleHandle([1, 1], [0, 0])
        self.__roi[-1].addScaleHandle([0, 0], [1, 1])
        self.__viewbox.addItem(self.__roi[-1])

        self.roicoords.append(coords)

    def removeROI(self):
        roi = self.__roi.pop()
        roi.hide()
        self.__viewbox.removeItem(roi)
        self.roicoords.pop()

    def getROI(self, rid=-1):
        if self.__roi and len(self.__roi) > rid:
            return self.__roi[rid]
        else:
            return None

    def countROIs(self):
        return len(self.__roi)

    def showROIs(self, status):
        if status:
            for roi in self.__roi:
                roi.show()
        else:
            for roi in self.__roi:
                roi.hide()

    def addCut(self, coords=None):
        if not coords or not isinstance(coords, list) or len(coords) != 4:
            pnt = 10 * (len(self.__cut) + 1)
            sz = 50
            coords = [pnt, pnt, pnt + sz, pnt]
        self.__cut.append(SimpleLineROI(coords[:2], coords[2:], pen='r'))
        self.__viewbox.addItem(self.__cut[-1])
        self.cutcoords.append(coords)

    def removeCut(self):
        cut = self.__cut.pop()
        cut.hide()
        self.__viewbox.removeItem(cut)
        self.cutcoords.pop()

    def getCut(self, cid=-1):
        if self.__cut and len(self.__cut) > cid:
            return self.__cut[cid]
        else:
            return None

    def countCuts(self):
        return len(self.__cut)

    def showCuts(self, status):
        if status:
            for cut in self.__cut:
                cut.show()
        else:
            for cut in self.__cut:
                cut.hide()

    def oneToOneRange(self):
        ps = self.image.pixelSize()
        currange = self.__viewbox.viewRange()
        xrg = currange[0][1] - currange[0][0]
        yrg = currange[1][1] - currange[1][0]
        if self.position is not None and \
           not self.roienable and not self.cutenable and not self.qenable:
            self.__viewbox.setRange(
                QtCore.QRectF(self.position[0], self.position[1],
                              xrg * ps[0], yrg * ps[1]),
                padding=0)
        else:
            self.__viewbox.setRange(
                QtCore.QRectF(0, 0, xrg * ps[0], yrg * ps[1]),
                padding=0)
        if self.setaspectlocked.isChecked():
            self.setaspectlocked.setChecked(False)
            self.setaspectlocked.triggered.emit(False)

    def setScale(self, position=None, scale=None, update=True):
        if update:
            self.setLabels(self.xtext, self.ytext, self.xunits, self.yunits)
        if self.position == position and self.scale == scale and \
           position is None and scale is None:
            return
        self.position = position
        self.scale = scale
        self.image.resetTransform()
        if self.scale is not None and update:
            self.image.scale(*self.scale)
        else:
            self.image.scale(1, 1)
        if self.position is not None and update:
            self.image.setPos(*self.position)
        else:
            self.image.setPos(0, 0)
        if self.rawdata is not None and update:
            self.__viewbox.autoRange()

    def resetScale(self):
        if self.scale is not None or self.position is not None:
            self.image.resetTransform()
        if self.scale is not None:
            self.image.scale(1, 1)
        if self.position is not None:
            self.image.setPos(0, 0)
        if self.scale is not None or self.position is not None:
            if self.rawdata is not None:
                self.__viewbox.autoRange()
            self.setLabels()

    def updateImage(self, img=None, rawimg=None):
        if self.__autodisplaylevels:
            self.image.setImage(img, autoLevels=True)
        else:
            self.image.setImage(
                img, autoLevels=False, levels=self.__displaylevels)
        self.data = img
        self.rawdata = rawimg
        self.mouse_position()

    @QtCore.pyqtSlot(object)
    def mouse_position(self, event=None):
        try:
            if event is not None:
                mousePoint = self.image.mapFromScene(event)
                self.__xdata = math.floor(mousePoint.x())
                self.__ydata = math.floor(mousePoint.y())
            if not self.roienable and not self.cutenable:
                if not self.__crosshairlocked:
                    if self.scale is not None and self.position is not None:
                        self.__vLine.setPos((self.__xdata + .5) * self.scale[0]
                                            + self.position[0])
                        self.__hLine.setPos((self.__ydata + .5) * self.scale[1]
                                            + self.position[1])
                    else:
                        self.__vLine.setPos(self.__xdata + .5)
                        self.__hLine.setPos(self.__ydata + .5)

            if self.rawdata is not None:
                try:
                    xf = int(math.floor(self.__xdata))
                    yf = int(math.floor(self.__ydata))
                    if xf >= 0 and yf >= 0 and xf < self.rawdata.shape[0] \
                       and yf < self.rawdata.shape[1]:
                        intensity = self.rawdata[xf, yf]
                    else:
                        intensity = 0.
                except Exception:
                    intensity = 0.
            else:
                intensity = 0.
            scaling = self.scaling if not self.statswoscaling else "linear"
            ilabel = "intensity"
            if not self.roienable:
                if self.dobkgsubtraction:
                    ilabel = "%s(intensity-background)" % (
                        scaling if scaling != "linear" else "")
                else:
                    if scaling == "linear":
                        ilabel = "intensity"
                    else:
                        ilabel = "%s(intensity)" % scaling
            if not self.roienable and not self.cutenable and not self.qenable:
                if self.scale is not None:
                    txdata = self.__xdata * self.scale[0]
                    tydata = self.__ydata * self.scale[1]
                    if self.position is not None:
                        txdata = txdata + self.position[0]
                        tydata = tydata + self.position[1]
                    self.currentMousePosition.emit(
                        "x = %f%s, y = %f%s, %s = %.2f" % (
                            txdata,
                            (" %s" % self.xunits) if self.xunits else "",
                            tydata,
                            (" %s" % self.yunits) if self.yunits else "",
                            ilabel, intensity))
                elif self.position is not None:
                    txdata = self.__xdata + self.position[0]
                    tydata = self.__ydata + self.position[1]
                    self.currentMousePosition.emit(
                        "x = %f%s, y = %f%s, %s = %.2f" % (
                            txdata,
                            (" %s" % self.xunits) if self.xunits else "",
                            tydata,
                            (" %s" % self.yunits) if self.yunits else "",
                            ilabel, intensity))
                else:
                    self.currentMousePosition.emit(
                        "x = %i, y = %i, %s = %.2f" % (
                            self.__xdata, self.__ydata, ilabel,
                            intensity))
            elif self.roienable and self.currentroi > -1:
                if event:
                    self.currentMousePosition.emit(
                        "%s" % self.roicoords[self.currentroi])
            elif self.cutenable:
                if self.currentcut > -1:
                    crds = self.cutcoords[self.currentcut]
                    crds = "[[%.2f, %.2f], [%.2f, %.2f]]" % tuple(crds)
                else:
                    crds = "[[0, 0], [0, 0]]"
                self.currentMousePosition.emit(
                    "%s, x = %i, y = %i, %s = %.2f" % (
                        crds, self.__xdata, self.__ydata, ilabel,
                        intensity))
            elif self.qenable and self.energy > 0 and self.detdistance > 0:
                if self.gspaceindex == 0:
                    thetax, thetay, thetatotal = self.pixel2theta(
                        self.__xdata, self.__ydata)
                    self.currentMousePosition.emit(
                        "th_x = %f deg, th_y = %f deg,"
                        " th_tot = %f deg, %s = %.2f"
                        % (thetax, thetay, thetatotal, ilabel, intensity))
                else:
                    qx, qz, q = self.pixel2q(self.__xdata, self.__ydata)
                    self.currentMousePosition.emit(
                        u"q_x = %f 1/\u212B, q_z = %f 1/\u212B, "
                        u"q = %f 1/\u212B, %s = %.2f"
                        % (qx, qz, q, ilabel, intensity))

            else:
                self.currentMousePosition.emit("")

        except Exception:
            # print("Warning: %s" % str(e))
            pass

    def pixel2theta(self, xdata, ydata):
        xcentered = xdata - self.centerx
        ycentered = ydata - self.centery
        thetax = math.atan(
            xcentered * self.pixelsizex/1000. / self.detdistance)
        thetay = math.atan(
            ycentered * self.pixelsizey/1000. / self.detdistance)
        r = math.sqrt((xcentered * self.pixelsizex / 1000.) ** 2
                      + (ycentered * self.pixelsizex / 1000.) ** 2)
        thetatotal = math.atan(r/self.detdistance)*180/math.pi
        return thetax, thetay, thetatotal

    def pixel2q(self, xdata, ydata):
        thetax, thetay, thetatotal = self.pixel2theta(
            self.__xdata, self.__ydata)
        wavelength = 12400./self.energy
        qx = 4 * math.pi / wavelength * math.sin(thetax/2.)
        qz = 4 * math.pi / wavelength * math.sin(thetay/2.)
        q = 4 * math.pi / wavelength * math.sin(thetatotal/2.)
        return qx, qz, q

    def setLabels(self, xtext=None, ytext=None, xunits=None, yunits=None):
        # print "set", xtext, ytext, xunits, yunits
        self.__bottomAxis.autoSIPrefix = False
        self.__leftaxis.autoSIPrefix = False
        self.__bottomAxis.setLabel(text=xtext, units=xunits)
        self.__leftaxis.setLabel(text=ytext, units=yunits)
        if xunits is None:
            self.__bottomAxis.labelUnits = ''
        if yunits is None:
            self.__leftaxis.labelUnits = ''
        if xtext is None:
            self.__bottomAxis.label.setVisible(False)
        if ytext is None:
            self.__leftaxis.label.setVisible(False)

    @QtCore.pyqtSlot(object)
    def mouse_click(self, event):

        mousePoint = self.image.mapFromScene(event.scenePos())

        xdata = mousePoint.x()
        ydata = mousePoint.y()

        # if double click: fix mouse crosshair
        # another double click releases the crosshair again
        if event.double():
            if not self.roienable and not self.cutenable and not self.qenable:
                self.__crosshairlocked = not self.__crosshairlocked
                if not self.__crosshairlocked:
                    self.__vLine.setPos(xdata + .5)
                    self.__hLine.setPos(ydata + .5)
            if self.qenable:
                self.__crosshairlocked = False
                self.centerx = float(xdata)
                self.centery = float(ydata)
                self.centerAngleChanged.emit()

    def setAutoLevels(self, autoLvls):
        if autoLvls:
            self.__autodisplaylevels = True
        else:
            self.__autodisplaylevels = False

    def setDisplayMinLevel(self, level=None):
        if level is not None:
            self.__displaylevels[0] = level

    def setDisplayMaxLevel(self, level=None):
        if level is not None:
            self.__displaylevels[1] = level

    def setSubWidgets(self, parameters):
        """ set subwidget properties

        :param parameters: tool parameters
        :type parameters: :class:`lavuelib.toolWidget.ToolParameters`
        """

        if parameters.scale is False:
            doreset = not (self.cutenable or
                           self.roienable or
                           self.qenable)

        if parameters.lines is not None:
            self.showLines(parameters.lines)
        if parameters.rois is not None:
            self.showROIs(parameters.rois)
            self.roienable = parameters.rois
        if parameters.cuts is not None:
            self.showCuts(parameters.cuts)
            self.cutenable = parameters.cuts
        if parameters.qspace is not None:
            self.qenable = parameters.qspace

        if parameters.scale is False and doreset:
            self.resetScale()
        if parameters.scale is True:
            self.setScale(self.position, self.scale)

    def geometryMessage(self):
        return u"geometry:\n" \
            u"  center = (%s, %s) pixels\n" \
            u"  pixel_size = (%s, %s) \u00B5m\n" \
            u"  detector_distance = %s mm\n" \
            u"  energy = %s eV" % (
                self.centerx,
                self.centery,
                self.pixelsizex,
                self.pixelsizey,
                self.detdistance,
                self.energy
            )
