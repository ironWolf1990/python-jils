from distutils.spawn import spawn
from jeditor.popup.splashscreen import StartUp
from jeditor.editormenu import JMenuBar
from jeditor.core.constants import JCONSTANTS
from jeditor.core.editorwidget import JEditorWidget
import typing
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QStatusBar, QWidget


class JStatusBar(QStatusBar):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

    pass


class JEditorWindow(QMainWindow):
    def __init__(
        self,
        parent: typing.Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)

        self._editorWidget = JEditorWidget(self)
        self.initUI()

    def initUI(self):

        self.setGeometry(200, 200, JCONSTANTS.EDITOR.WIDTH, JCONSTANTS.EDITOR.HEIGHT)
        self.Center()

        self.setWindowTitle(JCONSTANTS.EDITOR.TITLE)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        menuBar = JMenuBar(self._editorWidget)
        self.setMenuBar(menuBar)

        self.setCentralWidget(self._editorWidget)

        self.statusBar().showMessage("this is message")

    def Center(self):

        frame = self.frameGeometry()

        if JCONSTANTS.EDITOR.START_CENTER_ON_MOUSE:
            frame.moveCenter(
                QtWidgets.QApplication.desktop()
                .screenGeometry(
                    QtWidgets.QApplication.desktop().screenNumber(
                        QtWidgets.QApplication.desktop().cursor().pos()
                    )
                )
                .center()
            )
        else:
            frame.moveCenter(QDesktopWidget().availableGeometry().center())

        self.move(frame.topLeft())

    def show(self) -> None:
        if JCONSTANTS.EDITOR.SPLASH:
            splash = StartUp(parent=self, flags=QtCore.Qt.WindowStaysOnTopHint)
            splash.finished.connect(self._show)
            splash.show()
        else:
            self._show()

    def _show(self):
        return super().show()