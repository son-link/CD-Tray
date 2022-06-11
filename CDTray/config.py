from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLineEdit,
    QLabel,
    QCheckBox,
    QComboBox
)
from PyQt5.QtGui import QIcon, QPixmap
from os import environ, path
from re import search
import configparser


_translate = QCoreApplication.translate
configfile = environ['HOME']+'/.cdtray'
LOCAL_DIR = path.dirname(path.realpath(__file__))


class Config(QDialog):
    def __init__(self, parent):
        super(Config, self).__init__()
        self.parent = parent
        self.setWindowIcon(QIcon(QPixmap(LOCAL_DIR + '/cdtray.svg')))
        self.setWindowTitle(
            _translate('ConfigDialog', 'Configure CD Tray')
        )

        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        label1 = QLabel(_translate('ConfigDialog', 'Set CD Device'))
        mainLayout.addWidget(label1, 1, 0)

        self.editDevice = QLineEdit()
        mainLayout.addWidget(self.editDevice, 1, 1)

        self.autostartCheck = QCheckBox(
            _translate('ConfigDialog', 'autostart at boot')
        )
        mainLayout.addWidget(self.autostartCheck, 2, 0, 2, 0)

        self.notifyCheck = QCheckBox(
            _translate(
                'ConfigDialog',
                'Show notifications when start new track'
            )
        )
        mainLayout.addWidget(self.notifyCheck, 3, 0, 2, 0)

        label2 = QLabel(_translate('ConfigDialog', 'Set audio output'))
        mainLayout.addWidget(label2, 5, 0)

        self.outputdevice = QComboBox()
        self.outputdevice.addItem('ALSA', 'alsa')
        self.outputdevice.addItem('Pulse', 'pulse')
        self.outputdevice.addItem('Pipewire', 'pipewire')
        mainLayout.addWidget(self.outputdevice, 5, 1)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        mainLayout.addWidget(button_box, 6, 0, 2, 0)
        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.close)

    def open(self):
        config = self.loadConf()
        self.editDevice.setText(config['device'])

        self.autostartCheck.setChecked(False)
        if config['autostart'] == 1:
            self.autostartCheck.setChecked(True)

        self.notifyCheck.setChecked(False)
        if config['shownotify'] == 1:
            self.notifyCheck.setChecked(True)

        index = self.outputdevice.findData(config['outputdevice'])
        self.outputdevice.setCurrentIndex(index)

        self.show()

    @staticmethod
    def loadConf(device=None):
        if not path.isfile(configfile):
            f = open(configfile, 'w')
            f.write("[cdtray]\ndevice=/dev/sr0\nautostart=0\nshownotify=0\noutput=pulse")
            f.close()
        
        cfg = configparser.ConfigParser()
        cfg.read([configfile])
        config = {}

        try:
            if device:
                config['device'] = device
            else:
                config['device'] = cfg.get('cdtray', 'device')

            config['autostart'] = int(cfg.get('cdtray', 'autostart'))
            config['shownotify'] = int(cfg.get('cdtray', 'shownotify'))
            config['outputdevice'] = cfg.get('cdtray', 'output')
            if not search('alsa|pipewire|pulse', config['outputdevice']):
                config['outputdevice'] = 'pulse'

        except configparser.NoOptionError:
            print('Error')

        return config

    def save(self):
        currentConf = self.loadConf()
        cfg = configparser.ConfigParser()
        cfg.read([configfile])

        cfg.set('cdtray', 'device', self.editDevice.text())
        if self.autostartCheck.isChecked():
            cfg.set('cdtray', 'autostart', '1')
        else:
            cfg.set('cdtray', 'autostart', '0')

        if self.notifyCheck.isChecked():
            cfg.set('cdtray', 'shownotify', '1')
        else:
            cfg.set('cdtray', 'shownotify', '0')

        cfg.set('cdtray', 'output', self.outputdevice.currentData())

        with open(configfile, "w") as file:
            cfg.write(file)
            file.close()

        self.close()

        if (
            currentConf['device'] != self.editDevice.text() or
            currentConf['outputdevice'] != self.outputdevice.currentData()
        ):
            self.parent.player.reset()
