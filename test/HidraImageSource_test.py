# Copyright (C) 2017  DESY, Notkestr. 85, D-22607 Hamburg
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
#     Jan Kotanski <jan.kotanski@desy.de>
#
import unittest
import os
import sys
import random
import struct
import binascii
import time
import logging
import numpy as np
import fabio

try:
    from . import hidra
except Exception:
    import hidra
try:
    from . import hidrafake
except Exception:
    import hidrafake

import argparse
import lavuelib
import lavuelib.liveViewer
from pyqtgraph import QtCore
from pyqtgraph.Qt import QtTest

try:
    from pyqtgraph import QtWidgets
except Exception:
    from pyqtgraph import QtGui as QtWidgets

from qtchecker.qtChecker import (
    QtChecker, CmdCheck, ExtCmdCheck, WrapAttrCheck)

#  Qt-application
app = None

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

if sys.version_info > (3,):
    long = int
    unicode = str


# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

#: python3 running
PY3 = (sys.version_info > (3,))


def tostr(x):
    """ decode bytes to str

    :param x: string
    :type x: :obj:`bytes`
    :returns:  decode string in byte array
    :rtype: :obj:`str`
    """
    if isinstance(x, str):
        return x
    if sys.version_info > (3,):
        return str(x, "utf8")
    else:
        return str(x)


# test fixture
class HidraImageSourceTest(unittest.TestCase):

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)
        global app
        if app is None:
            app = QtWidgets.QApplication([])
        app.setOrganizationName("DESY")
        app.setApplicationName("LaVue: unittests")
        app.setOrganizationDomain("desy.de")
        app.setApplicationVersion(lavuelib.__version__)

        try:
            self.__seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = long(time.time() * 256)
#        self.__seed = 332115341842367128541506422124286219441
        self.__rnd = random.Random(self.__seed)
        home = os.path.expanduser("~")
        self.__cfgfdir = "%s/%s" % (home, ".config/DESY")
        self.__cfgfname = "%s/%s" % (self.__cfgfdir, "LaVue: unittests.conf")
        self.__dialog = None
        self.__counter = 0
        self.__tangoimgcounter = 0
        self.__tangofilepattern = "%05d.tif"
        self.__tangofilepath = ""
        self.__tangoimgcounter2 = 0
        self.__tangofilepattern2 = "%05d.tif"
        self.__tangofilepath2 = ""
        print("Hidra faked: %s" % hidrafake.faked)

    def setUp(self):
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)
        home = os.path.expanduser("~")
        fname = "%s/%s" % (home, ".config/DESY/LaVue: unittests.conf")
        if os.path.exists(fname):
            print("removing '%s'" % fname)
            os.remove(fname)

    def tearDown(self):
        print("tearing down ...")

    def takeNewImage(self):
        global app
        self.__counter += 1

        self.__tangoimgcounter += 1
        ipath = self.__tangofilepath
        iname = \
            self.__tangofilepattern % self.__tangoimgcounter
        fname = os.path.join(ipath, iname)
        hidra.filename = fname
        print("SET: %s" % hidra.filename)
        try:
            image = fabio.open(fname)
            li = image.data
        except Exception:
            li = None
        app.sendPostedEvents()
        return li

    def takeNewImage2(self):
        global app
        self.__counter += 1

        # self.__tangoimgcounter2 += 1
        ipath = self.__tangofilepath2
        iname = \
            self.__tangofilepattern2 % self.__tangoimgcounter2
        fname = os.path.join(ipath, iname)
        hidra.filename2 = fname
        print("SET2: %s" % hidra.filename2)
        try:
            image = fabio.open(fname)
            li = image.data
        except Exception:
            li = None
        app.sendPostedEvents()
        return li

    def test_readimage_fromstart(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        lastimage = None
        hidra.filename = ""
        hidra.filename2 = ""
        self.__tangoimgcounter = 0
        self.__tangofilepath = "%s/%s" % (os.path.abspath(path), "test/images")
        self.__tangofilepattern = "%05d.tif"
        cfg = '[Configuration]\n' \
            'StoreGeometry=true\n' \
            'GeometryFromSource=true'

        if not os.path.exists(self.__cfgfdir):
            os.makedirs(self.__cfgfdir)
        with open(self.__cfgfname, "w+") as cf:
            cf.write(cfg)

        lastimage = None

        options = argparse.Namespace(
            mode='expert',
            source='hidra',
            # configuration='%s://entry/instrument/detector/data'
            # % self._fname,
            start=True,
            # levels="0,1000",
            tool='intensity',
            transformation='none',
            log='error',
            instance='unittests',
            scaling='linear',
            gradient='spectrum',
        )
        logging.basicConfig(
             format="%(levelname)s: %(message)s")
        logger = logging.getLogger("lavue")
        lavuelib.liveViewer.setLoggerLevel(logger, options.log)
        dialog = lavuelib.liveViewer.MainWindow(options=options)
        dialog.show()

        qtck1 = QtChecker(app, dialog, True, sleep=100)
        qtck2 = QtChecker(app, dialog, True, sleep=100)
        qtck3 = QtChecker(app, dialog, True, sleep=100)
        qtck1.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            ExtCmdCheck(self, "takeNewImage"),
        ])
        qtck2.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            ExtCmdCheck(self, "takeNewImage"),
        ])
        qtck3.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            WrapAttrCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg"
                "._SourceTabWidget__sourcetabs[],0._ui.pushButton",
                QtTest.QTest.mouseClick, [QtCore.Qt.LeftButton]),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
        ])

        qtck1.executeChecks(delay=3000)
        qtck2.executeChecks(delay=6000)
        status = qtck3.executeChecksAndClose(delay=9000)

        self.assertEqual(status, 0)

        qtck1.compareResults(
            self, [True, None, None, None], mask=[0, 1, 1, 1])
        qtck2.compareResults(
            self, [True, None, None, None], mask=[0, 1, 1, 1])
        qtck3.compareResults(
            self, [None, None, None, False], mask=[1, 1, 0, 0])

        res1 = qtck1.results()
        res2 = qtck2.results()
        res3 = qtck3.results()
        self.assertEqual(res1[1], None)
        self.assertEqual(res1[2], None)

        lastimage = res1[3].T
        if not np.allclose(res2[1], lastimage):
            print(res2[1])
            print(lastimage)
        self.assertTrue(np.allclose(res2[1], lastimage))
        self.assertTrue(np.allclose(res2[2], lastimage))

        lastimage = res2[3].T

        if not np.allclose(res3[0], lastimage):
            print(res3[0])
            print(lastimage)
        self.assertTrue(np.allclose(res3[0], lastimage))
        self.assertTrue(np.allclose(res3[1], lastimage))

    def test_readimage_fromstart_cbf(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        lastimage = None
        hidra.filename = ""
        hidra.filename2 = ""
        self.__tangoimgcounter = -1
        self.__tangofilepath = "%s/%s" % (os.path.abspath(path), "test/images")
        self.__tangofilepattern = "tst_05717_%05d.cbf"
        cfg = '[Configuration]\n' \
            'StoreGeometry=true\n' \
            'GeometryFromSource=true'

        if not os.path.exists(self.__cfgfdir):
            os.makedirs(self.__cfgfdir)
        with open(self.__cfgfname, "w+") as cf:
            cf.write(cfg)

        lastimage = None

        options = argparse.Namespace(
            mode='expert',
            source='hidra',
            # configuration='%s://entry/instrument/detector/data'
            # % self._fname,
            start=True,
            # levels="0,1000",
            tool='intensity',
            transformation='none',
            log='error',
            instance='unittests',
            scaling='linear',
            gradient='spectrum',
        )
        logging.basicConfig(
             format="%(levelname)s: %(message)s")
        logger = logging.getLogger("lavue")
        lavuelib.liveViewer.setLoggerLevel(logger, options.log)
        dialog = lavuelib.liveViewer.MainWindow(options=options)
        dialog.show()

        qtck1 = QtChecker(app, dialog, True, sleep=100)
        qtck2 = QtChecker(app, dialog, True, sleep=100)
        qtck1.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            ExtCmdCheck(self, "takeNewImage"),
        ])
        qtck2.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            WrapAttrCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg"
                "._SourceTabWidget__sourcetabs[],0._ui.pushButton",
                QtTest.QTest.mouseClick, [QtCore.Qt.LeftButton]),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
        ])

        qtck1.executeChecks(delay=1000)
        status = qtck2.executeChecksAndClose(delay=3000)

        self.assertEqual(status, 0)

        qtck1.compareResults(
            self, [True, None, None, None], mask=[0, 1, 1, 1])
        qtck2.compareResults(
            self, [None, None, None, False], mask=[1, 1, 0, 0])

        res1 = qtck1.results()
        res2 = qtck2.results()
        self.assertEqual(res1[1], None)
        self.assertEqual(res1[2], None)

        lastimage = res1[3].T
        if not np.allclose(res2[0], lastimage):
            print(res2[0])
            print(lastimage)
        self.assertTrue(np.allclose(res2[0], lastimage))
        self.assertTrue(np.allclose(res2[1], lastimage))

    def test_readimage_multi_fromstart(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        lastimage = None
        lastimage2 = None
        hidra.filename = ""
        hidra.filename2 = ""
        self.__tangoimgcounter = 0
        self.__tangofilepath = "%s/%s" % (
            os.path.abspath(path), "test/images")
        self.__tangofilepattern = "%05d.tif"
        self.__tangoimgcounter2 = 0
        self.__tangofilepath2 = "%s/%s" % (
            os.path.abspath(path), "test/images")
        self.__tangofilepattern2 = "tst_05717_%05d.cbf"
        cfg = '[Configuration]\n' \
            'StoreGeometry=true\n' \
            'GeometryFromSource=true'

        if not os.path.exists(self.__cfgfdir):
            os.makedirs(self.__cfgfdir)
        with open(self.__cfgfname, "w+") as cf:
            cf.write(cfg)

        lastimage = None
        lastimage2 = None

        options = argparse.Namespace(
            mode='expert',
            source='hidra;hidra',
            configuration='has1pilatus100k.desy.de;has2pilatus100k.desy.de',
            start=True,
            # levels="0,1000",
            tool='intensity',
            transformation='none',
            log='debug',
            instance='unittests',
            scaling='linear',
            gradient='spectrum',
        )
        logging.basicConfig(
             format="%(levelname)s: %(message)s")
        logger = logging.getLogger("lavue")
        lavuelib.liveViewer.setLoggerLevel(logger, options.log)
        dialog = lavuelib.liveViewer.MainWindow(options=options)
        dialog.show()

        qtck1 = QtChecker(app, dialog, True, sleep=100)
        qtck2 = QtChecker(app, dialog, True, sleep=100)
        qtck3 = QtChecker(app, dialog, True, sleep=100)
        qtck1.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            ExtCmdCheck(self, "takeNewImage"),
            ExtCmdCheck(self, "takeNewImage2"),
        ])
        qtck2.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            ExtCmdCheck(self, "takeNewImage"),
            ExtCmdCheck(self, "takeNewImage2"),
        ])
        qtck3.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            WrapAttrCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg"
                "._SourceTabWidget__sourcetabs[],0._ui.pushButton",
                QtTest.QTest.mouseClick, [QtCore.Qt.LeftButton]),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
        ])

        qtck1.executeChecks(delay=3000)
        qtck2.executeChecks(delay=6000)
        status = qtck3.executeChecksAndClose(delay=9000)

        self.assertEqual(status, 0)

        qtck1.compareResults(
            self, [True, None, None, None, None], mask=[0, 1, 1, 1, 1])
        qtck2.compareResults(
            self, [True, None, None, None, None], mask=[0, 1, 1, 1, 1])
        qtck3.compareResults(
            self, [None, None, None, False], mask=[1, 1, 0, 0])

        res1 = qtck1.results()
        res2 = qtck2.results()
        res3 = qtck3.results()
        self.assertEqual(res1[1], None)
        self.assertEqual(res1[2], None)

        lastimage1 = res1[3].T
        lastimage2 = res1[4].T
        lastimage = np.hstack((lastimage1, lastimage2))
        if not np.allclose(res2[1], lastimage):
            print(res2[1])
            print(lastimage)
        self.assertTrue(np.allclose(res2[1], lastimage))
        self.assertTrue(np.allclose(res2[2], lastimage))

        lastimage1 = res2[3].T
        lastimage2 = res1[4].T

        lastimage = np.hstack((lastimage1, lastimage2))
        if not np.allclose(res3[0], lastimage):
            print(res3[0])
            print(lastimage)
        self.assertTrue(np.allclose(res3[0], lastimage))
        self.assertTrue(np.allclose(res3[1], lastimage))

    def test_readimage_multi_hidraports(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        lastimage = None
        lastimage2 = None
        hidra.filename = ""
        hidra.filename2 = ""
        self.__tangoimgcounter = 0
        self.__tangofilepath = "%s/%s" % (
            os.path.abspath(path), "test/images")
        self.__tangofilepattern = "%05d.tif"
        self.__tangoimgcounter2 = 0
        self.__tangofilepath2 = "%s/%s" % (
            os.path.abspath(path), "test/images")
        self.__tangofilepattern2 = "tst_05717_%05d.cbf"
        cfg = '[Configuration]\n' \
            'StoreGeometry=true\n' \
            'HidraDataPort="[\"50201\", \"50001\"]"\n' \
            'GeometryFromSource=true'

        if not os.path.exists(self.__cfgfdir):
            os.makedirs(self.__cfgfdir)
        with open(self.__cfgfname, "w+") as cf:
            cf.write(cfg)

        lastimage = None
        lastimage2 = None

        options = argparse.Namespace(
            mode='expert',
            source='hidra;hidra',
            configuration='has1pilatus100k.desy.de;has2pilatus100k.desy.de',
            start=True,
            # levels="0,1000",
            tool='intensity',
            transformation='none',
            # log='debug',
            log='error',
            instance='unittests',
            scaling='linear',
            gradient='spectrum',
        )
        logging.basicConfig(
             format="%(levelname)s: %(message)s")
        logger = logging.getLogger("lavue")
        lavuelib.liveViewer.setLoggerLevel(logger, options.log)
        dialog = lavuelib.liveViewer.MainWindow(options=options)
        dialog.show()

        qtck1 = QtChecker(app, dialog, True, sleep=100)
        qtck2 = QtChecker(app, dialog, True, sleep=100)
        qtck3 = QtChecker(app, dialog, True, sleep=100)
        qtck1.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            ExtCmdCheck(self, "takeNewImage"),
            ExtCmdCheck(self, "takeNewImage2"),
        ])
        qtck2.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            ExtCmdCheck(self, "takeNewImage"),
            ExtCmdCheck(self, "takeNewImage2"),
        ])
        qtck3.setChecks([
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.rawData"),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__imagewg.currentData"),
            WrapAttrCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg"
                "._SourceTabWidget__sourcetabs[],0._ui.pushButton",
                QtTest.QTest.mouseClick, [QtCore.Qt.LeftButton]),
            CmdCheck(
                "_MainWindow__lavue._LiveViewer__sourcewg.isConnected"),
        ])

        qtck1.executeChecks(delay=6000)
        qtck2.executeChecks(delay=12000)
        status = qtck3.executeChecksAndClose(delay=18000)

        self.assertEqual(status, 0)

        qtck1.compareResults(
            self, [True, None, None, None, None], mask=[0, 1, 1, 1, 1])
        qtck2.compareResults(
            self, [True, None, None, None, None], mask=[0, 1, 1, 1, 1])
        qtck3.compareResults(
            self, [None, None, None, False], mask=[1, 1, 0, 0])

        res1 = qtck1.results()
        res2 = qtck2.results()
        res3 = qtck3.results()
        self.assertEqual(res1[1], None)
        self.assertEqual(res1[2], None)

        lastimage1 = res1[3].T
        lastimage2 = res1[4].T
        lastimage = np.hstack((lastimage2, lastimage1))
        if not np.allclose(res2[1], lastimage):
            print(res2[1])
            print(lastimage)
        self.assertTrue(np.allclose(res2[1], lastimage))
        self.assertTrue(np.allclose(res2[2], lastimage))

        lastimage1 = res2[3].T

        # image2 is not updated  - it does not exist
        lastimage2 = res1[4].T
        lastimage = np.hstack((lastimage2, lastimage1))

        if not np.allclose(res3[0], lastimage):
            print(res3[0][0])
            print(lastimage[0])

        self.assertTrue(np.allclose(res3[0], lastimage))
        self.assertTrue(np.allclose(res3[1], lastimage))


if __name__ == '__main__':
    if app is None:
        app = QtWidgets.QApplication([])
    unittest.main()
