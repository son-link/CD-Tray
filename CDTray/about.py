from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
)
from PyQt5.QtGui import QIcon, QPixmap
from os import path

_translate = QCoreApplication.translate
LOCAL_DIR = path.dirname(path.realpath(__file__))


class About(QDialog):
    def __init__(self, parent):
        super(About, self).__init__()
        self.parent = parent
        self.setWindowIcon(QIcon(QPixmap(LOCAL_DIR + '/cdtray.svg')))
        self.setWindowTitle(
            _translate('AboutDialog', 'About CD Tray')
        )
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        about = _translate('AboutDialog', """
CD Tray<br />
(c) 2012 -2023 Alfonso Saavedra "Son Link"<br />
Under the GNU/GPL 3 or newer license<br />
<a href="https://github.com/son-link/CD-Tray">Proyect repo</a>
        """)

        label1 = QLabel(_translate('ConfigDialog', about))
        label1.setTextFormat(Qt.RichText)
        label1.setOpenExternalLinks(True)
        mainLayout.addWidget(label1)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok
        )
        mainLayout.addWidget(button_box)
        button_box.accepted.connect(self.hide)
