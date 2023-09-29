#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication, QTranslator, QLocale
from PyQt5.QtWidgets import (
    QApplication,
    QMenu,
    QSystemTrayIcon,
    QWidget
)
from PyQt5.QtGui import QIcon, QPixmap
from functools import partial
from optparse import OptionParser
from pathlib import Path

from .player import Player
from .config import Config
from .about import About

import subprocess
import sys
import os
import psutil

_translate = QCoreApplication.translate


class CDTRAY(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.config = Config.loadConf()

        def _checkDevice(options, opt_str, value, parser):
            if not value:
                parser.values.device = self.config['device']

        usage = "Usage: %prog [options]"
        parser = OptionParser(usage=usage, version='2.0.rc1')
        parser.add_option("-d", "--device",
                          dest="device",
                          action="callback",
                          metavar="DEVICE",
                          callback=_checkDevice,
                          help=_translate('MainApp', "Set CD device"))
        parser.add_option("-f", "--force",
                          action="store_true",
                          dest="force",
                          default=False,
                          help=_translate(
                              'MainApp',
                              "Force kill another CD Tray instance"
                          ))

        (self.options, args) = parser.parse_args()

        self.checkIfRuning()

        self.setToolTip('CD Tray')
        self.player = Player(self)
        self.configDialog = Config(self)
        self.about = About(self)

        self.menu = QMenu(parent)
        self.trackMenu = self.menu.addMenu(_translate('MainApp', "Tracks"))

        self.playBtn = self.menu.addAction(
            QIcon.fromTheme('media-playback-start'),
            _translate('MainApp', "Play")
        )

        self.nextBtn = self.menu.addAction(
            QIcon.fromTheme('media-skip-forward'),
            _translate('MainApp', "Next")
        )

        self.prevBtn = self.menu.addAction(
            QIcon.fromTheme('media-skip-backward'),
            _translate('MainApp', "Previous")
        )

        self.stopBtn = self.menu.addAction(
            QIcon.fromTheme('media-playback-stop'),
            _translate('MainApp', "Stop")
        )

        self.ejectBtn = self.menu.addAction(
            QIcon.fromTheme('media-eject'),
            _translate('MainApp', "Eject")
        )

        self.confBtn = self.menu.addAction(
            QIcon.fromTheme('configure'),
            _translate('MainApp', "Configure")
        )

        self.aboutBtn = self.menu.addAction(
            QIcon.fromTheme('help-about'),
            _translate('MainApp', "About")
        )

        self.exitBtn = self.menu.addAction(
            QIcon.fromTheme('application-exit'),
            _translate('MainApp', "Exit")
        )

        self.ejectBtn.triggered.connect(self.eject)
        self.nextBtn.triggered.connect(self.player.next)
        self.playBtn.triggered.connect(self.player.play)
        self.prevBtn.triggered.connect(self.player.prev)
        self.stopBtn.triggered.connect(self.player.stop)
        self.confBtn.triggered.connect(self.configDialog.open)
        self.aboutBtn.triggered.connect(self.about.show)
        self.exitBtn.triggered.connect(self.exit)

        self.nextBtn.setEnabled(False)
        self.prevBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)
        self.trackMenu.setEnabled(False)

        self.setContextMenu(self.menu)

        if self.config['autostart'] == 1:
            self.player.play()

    def checkIfRuning(self):
        """ Checks if an instance of the application is already running.
            If this is the case and the -f|--force parameter is not passed
            to the program, it closes.
        """
        lockfile = '/tmp/cdtray.lock'

        if Path(lockfile).is_file():
            with open(lockfile, 'r') as file:
                pid = file.read()
                pid = int(pid)
                file.close()

                if psutil.pid_exists(pid):
                    if self.options.force:
                        p = psutil.Process(pid)
                        p.terminate()
                        with open(lockfile, 'w') as file:
                            file.write(str(os.getpid()))
                            file.close()
                    else:
                        exit()
        else:
            with open(lockfile, 'w') as file:
                file.write(str(os.getpid()))
                file.close()

    def eject(self):
        self.player.reset()
        self.player.actual_track = 1
        self.player.total_tracks = 0
        self.trackMenu.clear()
        self.trackMenu.setEnabled(False)
        icon = QIcon.fromTheme('media-playback-start')
        self.playBtn.setText(_translate('MainApp', "Play"))
        self.playBtn.setIcon(icon)
        subprocess.run(['eject', self.device])

    def updateMenu(self):
        self.trackMenu.setEnabled(True)
        self.trackMenu.clear()
        if len(self.player.discTracks) > 0:
            for i in range(0, len(self.player.discTracks)):
                action = self.trackMenu.addAction(self.player.discTracks[i])
                action.setData(i + 1)
                action.triggered.connect(
                    partial(self.player.changeTrack, action)
                )

                if i + 1 == 1:
                    action.setEnabled(False)
        else:
            for i in range(1, self.player.file_tags['track-count']+1):
                if i < 10:
                    tn = '0'+str(i)
                else:
                    tn = str(i)

                action = self.trackMenu.addAction(
                    _translate('MainApp', 'Track {}').format(tn)
                )
                action.setData(i)
                action.triggered.connect(
                    partial(self.player.changeTrack, action)
                )

                if i == 1:
                    action.setEnabled(False)

    def exit(self):
        self.player.stop()
        sys.exit()


def main():
    LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    defaultLocale = QLocale.system().name()
    if defaultLocale.startswith('es_'):
        defaultLocale = 'es'

    translator = QTranslator()
    translator.load(LOCAL_DIR + "/locales/" + defaultLocale + ".qm")
    app.installTranslator(translator)

    w = QWidget()
    cdt = CDTRAY(QIcon(QPixmap(LOCAL_DIR + '/cdtray.svg')), w)
    cdt.show()
    app.exec_()
