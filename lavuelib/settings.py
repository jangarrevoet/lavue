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
#     Christoph Rosemann <christoph.rosemann@desy.de>
#     Jan Kotanski <jan.kotanski@desy.de>
#


""" live viewer image display base it on a qt dialog """


import zmq


class Settings(object):

    """ lavue configuration settings """

    def __init__(self):
        """ constructor
        """

        #: (:obj:`bool`) sardana enabled
        self.sardana = True
        #: (:obj:`bool`) add rois to sardana
        self.addrois = True
        #: (:obj:`bool`) search for security stream port automatically
        self.secautoport = True
        #: (:obj:`bool`) show intensity hostogram
        self.showhisto = True
        #: (:obj:`bool`) show mask widget
        self.showmask = False
        #: (:obj:`bool`) show mask widget
        self.showstats = True
        #: (:obj:`bool`) show bakcground subtraction widget
        self.showsub = True
        #: (:obj:`bool`) show transformation widget
        self.showtrans = True
        #: (:obj:`bool`) show intensity scale widget
        self.showscale = True
        #: (:obj:`bool`) show intensity levels widget
        self.showlevels = True
        #: (:obj:`bool`) image aspect ratio locked
        self.aspectlocked = False
        #: (:obj:`bool`) auto down sample
        self.autodownsample = False
        #: (:obj:`str`) security stream port
        self.secport = "5657"
        #: (:obj:`str`) hidra data port
        self.hidraport = "50001"
        #: (:obj:`int`) image source timeout for connection
        self.timeout = 3000
        #: (:class:`zmq.Context`) zmq context
        self.seccontext = zmq.Context()
        #: (:class:`zmq.Socket`) zmq security stream socket
        self.secsocket = self.seccontext.socket(zmq.PUB)
        #: (:obj:`bool`) security stream enabled
        self.secstream = False
        #: (:obj:`bool`) security stream options
        self.secsockopt = ""
        #: (:obj:`float`) refresh rate
        self.refreshrate = 0.1
        #: (:obj:`bool`) interrupt on error
        self.interruptonerror = True
        #: (:obj:`str`) last image file name
        self.imagename = None
        #: (:obj:`bool`) statistics without scaling
        self.statswoscaling = False
        #: (:obj:`list` < :obj:`str` > ) zmq source topics
        self.zmqtopics = []
        #: (:obj:`bool`) automatic zmq source topics
        self.autozmqtopics = False
        #: (:obj:`str`) file name translation json dictionary
        self.dirtrans = '{"/ramdisk/": "/gpfs/"}'
        #: (:obj:`str`) JSON dictionary with {label: tango attribute}
        #  for Tango Attribute source
        self.tangoattrs = '{}'
        #: (:obj:`str`) JSON dictionary with {label: url}
        #  for HTTP responce source
        self.httpurls = '{}'
        #: (:obj:`str`) JSON dictionary with {label: <server:port>}
        #  for ZMQ source
        self.zmqservers = '{}'
        #: (:obj:`str`) door device name
        self.doorname = ""
        #: (:obj:`bool`) nexus file source keeps the file open
        self.nxsopen = False
        #: (:obj:`bool`) nexus file source starts from the last image
        self.nxslast = False
        #: (:obj:`list` < :obj:`str`>) hidra detector server list
        self.detservers = []
        #: (:obj:`bool`) store detector geometry
        self.storegeometry = False

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

    def load(self, settings):
        """ load settings

        :param settings: QSettings object
        :type settings: :class:`PyQt4.QtCore.QSettings`
        :returns: error messages list
        :rtype: :obj:`list` < (:obj:`str`, :obj:`str`) >
        """
        status = []
        qstval = str(settings.value("Configuration/Sardana", type=str))
        if qstval.lower() == "false":
            self.sardana = False
        else:
            self.sardana = True
        qstval = str(settings.value("Configuration/AddROIs", type=str))
        if qstval.lower() == "false":
            self.addrois = False
        qstval = str(settings.value("Configuration/SecAutoPort", type=str))
        if qstval.lower() == "false":
            self.secautoport = False
        qstval = str(settings.value(
            "Configuration/ShowSubtraction", type=str))
        if qstval.lower() == "false":
            self.showsub = False
        qstval = str(settings.value(
            "Configuration/ShowTransformations", type=str))
        if qstval.lower() == "false":
            self.showtrans = False
        qstval = str(settings.value(
            "Configuration/ShowIntensityScaling", type=str))
        if qstval.lower() == "false":
            self.showscale = False
        qstval = str(settings.value(
            "Configuration/ShowIntensityLevels", type=str))
        if qstval.lower() == "false":
            self.showlevels = False
        qstval = str(settings.value("Configuration/ShowHistogram", type=str))
        if qstval.lower() == "false":
            self.showhisto = False
        qstval = str(settings.value("Configuration/ShowMaskWidget", type=str))
        if qstval.lower() == "true":
            self.showmask = True
        qstval = str(settings.value("Configuration/ShowStatistics", type=str))
        if qstval.lower() == "false":
            self.showstats = False
        qstval = str(settings.value("Configuration/AspectLocked", type=str))
        if qstval.lower() == "true":
            self.aspectlocked = True
        qstval = str(settings.value("Configuration/AutoDownSample", type=str))
        if qstval.lower() == "true":
            self.autodownsample = True
        qstval = str(settings.value("Configuration/NXSFileOpen", type=str))
        if qstval.lower() == "true":
            self.nxsopen = True
        qstval = str(settings.value("Configuration/NXSLastImage", type=str))
        if qstval.lower() == "true":
            self.nxslast = True
        qstval = str(settings.value("Configuration/SecPort", type=str))
        try:
            int(qstval)
            self.secport = str(qstval)
        except:
            pass
        qstval = str(settings.value("Configuration/HidraDataPort", type=str))
        try:
            int(qstval)
            self.hidraport = str(qstval)
        except:
            pass
        qstval = str(settings.value("Configuration/SourceTimeout", type=str))
        try:
            int(qstval)
            self.timeout = int(qstval)
        except:
            pass
        qstval = str(settings.value("Configuration/SecStream", type=str))
        if qstval.lower() == "true":
            try:
                if self.secautoport:
                    self.secsockopt = "tcp://*:*"
                    self.secsocket.bind(self.secsockopt)
                    self.secport = self.secsocket.getsockopt(
                        zmq.LAST_ENDPOINT).split(":")[-1]
                else:
                    self.secsockopt = "tcp://*:%s" % self.secport
                    self.secsocket.bind(self.secsockopt)
                self.secstream = True
            except:
                self.secstream = False
                import traceback
                value = traceback.format_exc()
                text = "lavue: Cannot connect to: %s" % self.secsockopt
                status = [(text, value)]

        try:
            self.refreshrate = float(
                settings.value("Configuration/RefreshRate", type=str))
        except:
            pass

        qstval = str(
            settings.value("Configuration/InterruptOnError", type=str))
        if qstval.lower() == "false":
            self.interruptonerror = False
        elif qstval.lower() == "true":
            self.interruptonerror = True
        qstval = str(
            settings.value("Configuration/LastImageFileName", type=str))
        if qstval:
            self.imagename = qstval
        qstval = str(
            settings.value(
                "Configuration/StatisticsWithoutScaling", type=str))
        if qstval.lower() == "true":
            self.statswoscaling = True

        qstval = \
            settings.value(
                "Configuration/ZMQStreamTopics", type=list)
        if qstval:
            self.zmqtopics = [str(tp) for tp in qstval]

        qstval = \
            settings.value(
                "Configuration/HidraDetectorServers", type=list)
        if qstval:
            self.detservers = [str(tp) for tp in qstval]

        qstval = str(settings.value(
            "Configuration/AutoZMQStreamTopics", type=str))
        if qstval.lower() == "true":
            self.autozmqtopics = True
        qstval = str(
            settings.value("Configuration/DirectoryTranslation", type=str))
        if qstval:
            self.dirtrans = qstval

        qstval = str(
            settings.value("Configuration/TangoAttributes", type=str))
        if qstval:
            self.tangoattrs = qstval

        qstval = str(
            settings.value("Configuration/HTTPURLs", type=str))
        if qstval:
            self.httpurls = qstval

        qstval = str(
            settings.value("Configuration/ZMQServers", type=str))
        if qstval:
            self.zmqservers = qstval

        qstval = str(
            settings.value("Configuration/StoreGeometry", type=str))
        if qstval.lower() == "true":
            self.storegeometry = True

        try:
            self.centerx = float(
                settings.value("Tools/CenterX", type=str))
        except:
            pass
        try:
            self.centery = float(
                settings.value("Tools/CenterY", type=str))
        except:
            pass
        try:
            self.energy = float(
                settings.value("Tools/Energy", type=str))
        except:
            pass

        try:
            self.pixelsizex = float(
                settings.value("Tools/PixelSizeX", type=str))
        except:
            pass
        try:
            self.pixelsizey = float(
                settings.value("Tools/PixelSizeY", type=str))
        except:
            pass
        try:
            self.detdistance = float(
                settings.value("Tools/DetectorDistance", type=str))
        except:
            pass
        return status

    def store(self, settings):
        """ Stores settings in QSettings object

        :param settings: QSettings object
        :type settings: :class:`PyQt4.QtCore.QSettings`
        """
        settings.setValue(
            "Configuration/AddROIs",
            self.addrois)
        settings.setValue(
            "Configuration/ShowSubtraction",
            self.showsub)
        settings.setValue(
            "Configuration/ShowTransformations",
            self.showtrans)
        settings.setValue(
            "Configuration/ShowIntensityScaling",
            self.showscale)
        settings.setValue(
            "Configuration/ShowIntensityLevels",
            self.showlevels)
        settings.setValue(
            "Configuration/ShowHistogram",
            self.showhisto)
        settings.setValue(
            "Configuration/ShowMaskWidget",
            self.showmask)
        settings.setValue(
            "Configuration/ShowStatistics",
            self.showstats)
        settings.setValue(
            "Configuration/RefreshRate",
            self.refreshrate)
        settings.setValue(
            "Configuration/SecPort",
            self.secport)
        settings.setValue(
            "Configuration/HidraDataPort",
            self.hidraport)
        settings.setValue(
            "Configuration/SecAutoPort",
            self.secautoport)
        settings.setValue(
            "Configuration/SecStream",
            self.secstream)
        settings.setValue(
            "Configuration/Sardana",
            self.sardana)
        settings.setValue(
            "Configuration/InterruptOnError",
            self.interruptonerror)
        settings.setValue(
            "Configuration/SourceTimeout",
            self.timeout)
        settings.setValue(
            "Configuration/AspectLocked",
            self.aspectlocked)
        settings.setValue(
            "Configuration/AutoDownSample",
            self.autodownsample)
        settings.setValue(
            "Configuration/LastImageFileName",
            self.imagename)
        settings.setValue(
            "Configuration/StatisticsWithoutScaling",
            self.statswoscaling)
        settings.setValue(
            "Configuration/ZMQStreamTopics",
            self.zmqtopics)
        settings.setValue(
            "Configuration/HidraDetectorServers",
            self.detservers)
        settings.setValue(
            "Configuration/AutoZMQStreamTopics",
            self.autozmqtopics)
        settings.setValue(
            "Configuration/DirectoryTranslation",
            self.dirtrans)
        settings.setValue(
            "Configuration/TangoAttributes",
            self.tangoattrs)
        settings.setValue(
            "Configuration/ZMQServers",
            self.zmqservers)
        settings.setValue(
            "Configuration/HTTPURLs",
            self.httpurls)
        settings.setValue(
            "Configuration/NXSLastImage",
            self.nxslast)
        settings.setValue(
            "Configuration/NXSFileOpen",
            self.nxsopen)
        settings.setValue(
            "Configuration/StoreGeometry",
            self.storegeometry)

        if not self.storegeometry:
            self.centerx = 0.0
            self.centery = 0.0
            self.energy = 0.0
            self.pixelsizex = 0.0
            self.pixelsizey = 0.0
            self.detdistance = 0.0

        settings.setValue(
            "Tools/CenterX",
            self.centerx)
        settings.setValue(
            "Tools/CenterY",
            self.centery)
        settings.setValue(
            "Tools/Energy",
            self.energy)
        settings.setValue(
            "Tools/PixelSizeX",
            self.pixelsizex)
        settings.setValue(
            "Tools/PixelSizeY",
            self.pixelsizey)
        settings.setValue(
            "Tools/DetectorDistance",
            self.detdistance)
