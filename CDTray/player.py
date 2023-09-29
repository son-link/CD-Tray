import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from os import path
from .config import Config
from .Cddb import CddbServer
from .sys_notify import Notification, init

Gst.init(None)
_translate = QCoreApplication.translate
LOCAL_DIR = path.dirname(path.realpath(__file__))


class Player():
    def __init__(self, parent):
        self.parent = parent
        self.total_tracks = 0
        self.actual_track = 1
        self.config = Config.loadConf()
        self.discTracks = []
        self.discTitle = ''

        self.player = Gst.Pipeline.new('player')
        self.source = Gst.ElementFactory.make("cdparanoiasrc", "cdda")
        self.conv = Gst.ElementFactory.make("audioconvert", "converter")
        self.volume = Gst.ElementFactory.make("volume", "volume")

        self.player.add(self.source)
        self.player.add(self.conv)
        self.player.add(self.volume)
        self.source.link(self.conv)
        self.conv.link(self.volume)

        self.player.get_by_name('cdda').set_property(
            'device', self.config['device']
        )

        self.sink = Gst.ElementFactory.make(
            '{}sink'.format(self.config['outputdevice'])
        )
        self.player.add(self.sink)
        self.volume.link(self.sink)

        init('cdtray')

        bus = self.player.get_bus()
        bus.add_signal_watch()
        # bus.connect("message", self.on_message)
        # bus.connect("message::info", self.bus_message_tag)
        bus.connect("message::tag", self.bus_message_tag)
        bus.connect("message::eos", self.next)

    def bus_message_tag(self, bus, message):
        """ Esta es la función encargada de recoger los datos del bus
            de Gstreamer, principalmente los tags de los ficheros de audio
        """
        self.file_tags = {}

        # Reload confif, necesary for some options
        self.config = Config.loadConf()
        taglist = message.parse_tag()

        def my_callback(list, tag, user_data):
            if tag == 'discid-full':
                self.file_tags['discid'] = list.get_string(tag)[1]
            elif tag == 'track-count' or tag == 'track-number':
                self.file_tags[tag] = list.get_uint(tag)[1]
            elif tag == 'duration':
                self.file_tags[tag] = list.get_uint64(tag)[1]

        taglist.foreach(my_callback, self)

        if (
            self.file_tags['discid'] and
            len(self.discTracks) == 0 and
            self.config['cddb'] == 1
        ):
            cddb = CddbServer()
            discInfo = cddb.getDiscs(self.file_tags['discid'])

            if discInfo:
                for disc in discInfo:
                    di = cddb.getDiscInfo(disc)

                    if di:
                        self.discTitle = f"{di.artist} - {di.title}"

                        i = 1
                        for t in di.tracks:
                            self.discTracks.append(t)
                            i = i + 1

                self.parent.updateMenu()

        if self.total_tracks != self.file_tags['track-count'] and len(self.discTracks) == 0:
            self.parent.updateMenu()
            self.total_tracks = self.file_tags['track-count']

        self.parent.nextBtn.setEnabled(True)
        self.parent.prevBtn.setEnabled(True)
        self.parent.stopBtn.setEnabled(True)
        if self.file_tags['track-number'] == 1:
            self.parent.prevBtn.setEnabled(False)

        if self.file_tags['track-number'] == self.total_tracks:
            self.parent.nextBtn.setEnabled(False)

        if self.discTitle and len(self.discTracks):
            trackTitle = f"{self.discTitle} - {self.discTracks[self.actual_track - 1]}"
            notifyText = _translate('MainApp', 'CD Tray: Playing {}').format(
                   trackTitle
            )
            self.parent.setToolTip(notifyText)
        else:
            notifyText = _translate(
                'MainApp',
                'CD Tray: Playing track {}').format(
                    self.file_tags['track-number']
                )
            self.parent.setToolTip(notifyText)

        if self.config['shownotify']:
            n = Notification(
                'CD Tray',
                notifyText,
                LOCAL_DIR + '/cdtray.svg',
                timeout=5000
            )
            n.show()

    def changeConf(self):
        self.player.get_by_name('cdda').set_property(
            'device', self.parent.config
        )

    def changeTrack(self, widget=None):
        if widget:
            self.actual_track = widget.data()

        self.player.set_state(Gst.State.READY)
        self.player.get_by_name('cdda').set_property(
            'track', self.actual_track
        )
        for action in self.parent.trackMenu.actions():
            if action.data() == self.actual_track:
                action.setEnabled(False)
            else:
                action.setEnabled(True)

        self.player.set_state(Gst.State.PLAYING)

    def play(self):
        status = self.player.get_state(Gst.CLOCK_TIME_NONE)
        icon = QIcon.fromTheme('media-playback-start')

        if status.state == Gst.State.PLAYING:
            self.player.set_state(Gst.State.PAUSED)
            self.parent.playBtn.setText(_translate('MainApp', "Play"))
        else:
            icon = QIcon.fromTheme("media-playback-pause")
            self.player.set_state(Gst.State.PLAYING)
            self.parent.playBtn.setText(_translate('MainApp', "Pause"))

        self.parent.playBtn.setIcon(icon)

    def prev(self):
        if self.actual_track > 0:
            self.actual_track -= 1
            self.changeTrack()

    def next(self, *args):
        if self.actual_track < self.file_tags['track-count']:
            self.actual_track += 1
            self.changeTrack()

    def reset(self):
        self.stop()
        self.actual_track = 1
        self.config = Config.loadConf()
        self.player.get_by_name('cdda').set_property(
            'device', self.config['device']
        )

        self.volume.unlink(self.sink)
        self.player.remove(self.sink)
        self.sink = Gst.ElementFactory.make(
            '{}sink'.format(self.config['outputdevice'])
        )
        self.player.add(self.sink)
        self.volume.link(self.sink)

        self.discTracks = []
        self.discTitle = ''

    def stop(self):
        self.player.set_state(Gst.State.READY)
        self.player.set_state(Gst.State.NULL)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
