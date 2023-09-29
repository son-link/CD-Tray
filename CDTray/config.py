from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLineEdit,
    QLabel,
    QCheckBox,
    QComboBox,
    QLayout,
    QPushButton
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
        self.layout = mainLayout
        widgetsLayout = QGridLayout()
        widgetsLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.setLayout(mainLayout)

        label1 = QLabel(_translate('ConfigDialog', 'Set CD Device'), self)
        widgetsLayout.addWidget(label1, 0, 0)

        self.editDevice = QLineEdit(self)
        widgetsLayout.addWidget(self.editDevice, 0, 1)

        label2 = QLabel(_translate('ConfigDialog', 'Set audio output'), self)
        widgetsLayout.addWidget(label2, 1, 0)

        self.outputdevice = QComboBox(self)
        self.outputdevice.addItem('ALSA', 'alsa')
        self.outputdevice.addItem('Pulse', 'pulse')
        self.outputdevice.addItem('Pipewire', 'pipewire')
        widgetsLayout.addWidget(self.outputdevice, 1, 1)

        self.autostartCheck = QCheckBox(
            _translate('ConfigDialog', 'autostart at boot'),
            self
        )
        widgetsLayout.addWidget(self.autostartCheck, 2, 0, 1, 2)

        self.notifyCheck = QCheckBox(
            _translate(
                'ConfigDialog',
                'Show notifications when start new track'
            ),
            self
        )
        widgetsLayout.addWidget(self.notifyCheck, 3, 0, 1, 2)

        self.useCDDB = QCheckBox(
            _translate(
                'ConfigDialog',
                'Get disc info from the Internet'
            ),
            self
        )
        widgetsLayout.addWidget(self.useCDDB, 4, 0, 1, 2)

        mainLayout.addLayout(widgetsLayout, 0, 0, 1, 1)

        okBtn = QPushButton(_translate('ConfigDialog', 'Accept'))
        cancelBtn = QPushButton(_translate('ConfigDialog', 'Cancel'))

        button_box = QDialogButtonBox()
        button_box.addButton(cancelBtn, QDialogButtonBox.RejectRole)
        button_box.addButton(okBtn, QDialogButtonBox.AcceptRole)

        mainLayout.addWidget(button_box, 1, 0)
        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.close)

        self.adjustSize()
        self.setFixedSize(self.size())

    def open(self):
        config = self.loadConf()
        self.editDevice.setText(config['device'])

        self.autostartCheck.setChecked(False)
        if config['autostart'] == 1:
            self.autostartCheck.setChecked(True)

        self.notifyCheck.setChecked(False)
        if config['shownotify'] == 1:
            self.notifyCheck.setChecked(True)

        self.useCDDB.setChecked(False)
        if config['cddb'] == 1:
            self.useCDDB.setChecked(True)

        index = self.outputdevice.findData(config['outputdevice'])
        self.outputdevice.setCurrentIndex(index)

        self.show()

    @staticmethod
    def loadConf(device=None):
        if not path.isfile(configfile):
            f = open(configfile, 'w')
            f.write("[cdtray]\ndevice=/dev/sr0\nautostart=0\nshownotify=0\noutput=pulse\ncddb=0")
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

            config['cddb'] = 0
            if cfg.has_option('cdtray', 'cddb'):
                config['cddb'] = int(cfg.get('cdtray', 'cddb'))

            if not search('alsa|pipewire|pulse', config['outputdevice']):
                config['outputdevice'] = 'pulse'

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

        if self.useCDDB.isChecked():
            cfg.set('cdtray', 'cddb', '1')
        else:
            cfg.set('cdtray', 'cddb', '0')

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
