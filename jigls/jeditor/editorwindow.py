from jigls.jeditor.popup.splashscreen import JSplashScreen
from jigls.jeditor.editormenu import JMenuBar
from jigls.jeditor.constants import JCONSTANTS
from jigls.jeditor.core.editorwidget import JEditorWidget
import typing
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QDialog,
    QDockWidget,
    QHBoxLayout,
    QMainWindow,
    QStatusBar,
    QWidget,
)
import weakref


class JStatusBar(QStatusBar):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

    pass


class JEditorWindow(QMainWindow):
    def __init__(
        self,
        parent: typing.Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)

        self._editorWidget = JEditorWidget(self)
        self.initUI()

    @property
    def editorWidget(self) -> JEditorWidget:
        return self._editorWidget

    def toggleDocket(self, a0: weakref):
        self.dockable.setWidget(a0())

    def initUI(self):

        self.setGeometry(200, 200, JCONSTANTS.EDITOR.WIDTH, JCONSTANTS.EDITOR.HEIGHT)
        self.Center()

        self.setWindowTitle(JCONSTANTS.EDITOR.TITLE)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint)
        # self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        menuBar = JMenuBar(self._editorWidget)
        self._editorWidget.graphicView.SignalNodeDoubleClick.connect(  # type:ignore
            self.toggleDocket
        )
        self.setMenuBar(menuBar)

        self.setCentralWidget(self._editorWidget)

        self.setStatusBar(JStatusBar(self))
        self.statusBar().showMessage("this is message")

        self.dockable = QDockWidget("Node Property Dock", self)
        self.dockable.setFloating(False)
        self.dockable.setContentsMargins(0, 0, 0, 0)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockable)

    def Center(self):

        frame = self.frameGeometry()

        if JCONSTANTS.EDITOR.START_CENTER_ON_MOUSE:
            frame.moveCenter(
                QApplication.desktop()
                .screenGeometry(QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos()))
                .center()
            )
        else:
            frame.moveCenter(QDesktopWidget().availableGeometry().center())

        self.move(frame.topLeft())

    def show(self) -> None:
        if JCONSTANTS.EDITOR.SPLASH:
            splash = JSplashScreen(parent=self, flags=QtCore.Qt.WindowStaysOnTopHint)
            splash.finished.connect(self._show)
            splash.show()
        else:
            self._show()

    def _show(self):
        return super().show()