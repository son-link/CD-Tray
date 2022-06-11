import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from PyQt5.QtCore import QCoreApplication
from .config import Config

Gst.init(None)
_translate = QCoreApplication.translate


class Player():
    def __init__(self, parent):
        self.parent = parent
        self.total_tracks = 0
        self.actual_track = 1
        self.config = Config.loadConf()

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
        taglist = message.parse_tag()

        def my_callback(list, tag, user_data):
            if tag == 'discid' or tag == 'musicbrainz-discid':
                self.file_tags[tag] = list.get_string(tag)[1]
            elif tag == 'track-count' or tag == 'track-number':
                self.file_tags[tag] = list.get_uint(tag)[1]
            elif tag == 'duration':
                self.file_tags[tag] = list.get_uint64(tag)[1]

        taglist.foreach(my_callback, self)

        if self.total_tracks != self.file_tags['track-count']:
            self.parent.updateMenu()
            self.total_tracks = self.file_tags['track-count']

        self.parent.nextBtn.setEnabled(True)
        self.parent.prevBtn.setEnabled(True)
        self.parent.stopBtn.setEnabled(True)
        if self.file_tags['track-number'] == 1:
            self.parent.prevBtn.setEnabled(False)

        if self.file_tags['track-number'] == self.total_tracks:
            self.parent.nextBtn.setEnabled(False)

        self.parent.setToolTip(
            _translate('MainApp', 'CD Tray: Playing track {}'.format(
                self.file_tags['track-number']
            ))
        )

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
        if status.state == Gst.State.PLAYING:
            self.player.set_state(Gst.State.PAUSED)
        else:
            self.player.set_state(Gst.State.PLAYING)

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

    def stop(self):
        self.player.set_state(Gst.State.READY)
        self.player.set_state(Gst.State.NULL)

    def on_message(self, bus, message):
        print(message)
        t = message.type
        print(t)
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
