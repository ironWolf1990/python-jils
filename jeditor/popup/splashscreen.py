from jeditor.core.constants import JCONSTANTS
from jeditor.stylesheet import STYLE_SPLASH
import typing
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class StartUp(QDialog):

    finish = QtCore.pyqtSignal(bool)

    def __init__(
        self,
        parent: typing.Optional[QWidget],
        flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType],
    ) -> None:
        super().__init__(parent=parent, flags=flags)

        self.setWindowTitle("J-Editor Spash Screen")
        # self.setGeometry(parent.geometry())
        self.resize(QSize(640, 360))
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet(STYLE_SPLASH)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # self.setWindowOpacity(0.1)

        # shadow = QGraphicsDropShadowEffect(self)
        # shadow.setBlurRadius(20)
        # shadow.setXOffset(0)
        # shadow.setYOffset(0)
        # shadow.setColor(QColor(0, 0, 0, 60))
        # self.setGraphicsEffect(shadow)

        self._Splash()

    def _Splash(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        splash = QLabel(self)
        splash.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter  # type:ignore
        )
        splash.setPixmap(QPixmap(JCONSTANTS.EDITOR.SPLASH_IMAGE))
        self.layout().addWidget(splash)

        self.timer = QTimer()
        self.timer.singleShot(JCONSTANTS.EDITOR.SPLASH_TIME, self.Close)

    def Close(self):
        self.finish.emit(True)  # type:ignore
        super().close()
