from jigls.jeditor.popup.nodesearch import JSearchBox
from jigls.jeditor.popup.filedialog import JFileDialog
from jigls.jeditor.core.graphicview import JGraphicView
import logging
from functools import partial
from typing import Callable, Optional

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction, QDialog, QMenuBar, QWidget

from jigls.jeditor.core.editorwidget import JEditorWidget
from jigls.jeditor.core.scenemanager import JSceneManager
from jigls.logger import logger
from jigls.jeditor.stylesheet import STYLE_QMENUBAR

logger = logging.getLogger(__name__)

# https://zetcode.com/gui/pyqt5/menustoolbars/


def CreateAction(
    menuBar: QMenuBar,
    name: str,
    shortcut: Optional[str] = None,
    tooltip: Optional[str] = None,
    callback: Optional[Callable] = None,
) -> QAction:

    action = QAction(name, parent=menuBar)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tooltip is not None:
        action.setToolTip(tooltip)
    if callback is not None:
        action.triggered.connect(callback)
    return action


class JMenuBar(QMenuBar):
    def __init__(self, editorWidget: JEditorWidget):
        super().__init__(parent=None)
        self._editorWidget = editorWidget
        self.setStyleSheet(STYLE_QMENUBAR)

        self._SetupMenu()

    def _SetupMenu(self):

        fileMenu = self.addMenu("&File")
        editMenu = self.addMenu("&Edit")
        graphMenu = self.addMenu("&Graph")
        helpMenu = self.addMenu("&Help")

        # * file menu
        fileMenu.addAction(
            CreateAction(
                self,
                "&New",
                "Ctrl+N",
                "create new graph model",
                partial(New, self._editorWidget.sceneManager),
            )
        )
        fileMenu.addAction(
            CreateAction(
                self,
                "&Open",
                "Ctrl+O",
                "open graph model",
                partial(Open, self._editorWidget.graphicView),
            )
        )
        fileMenu.addSeparator()
        fileMenu.addAction(
            CreateAction(
                self,
                "&Save",
                "Ctrl+S",
                "save the graph model",
                partial(Save, self._editorWidget.graphicView),
            )
        )
        fileMenu.addAction(
            CreateAction(
                self,
                "Save &As",
                "Ctrl+Shift+S",
                "save graph model as",
                partial(SaveAs, self._editorWidget.graphicView),
            )
        )
        fileMenu.addSeparator()

        # * export menu
        exportMenu = fileMenu.addMenu("&Export")
        exportMenu.addAction(
            CreateAction(
                self,
                "&Robot Framework",
                "Ctrl+Shift+R",
                "export to robot framework",
                partial(RobotFramework, self._editorWidget.sceneManager),
            )
        )
        exportMenu.addAction(
            CreateAction(
                self,
                "&Pytorch",
                "Ctrl+Shift+P",
                "export to pytorch",
                partial(Pytorch, self._editorWidget.sceneManager),
            )
        )
        exportMenu.addSeparator()
        exportMenu.addAction(
            CreateAction(
                self,
                "&PNG",
                None,
                "export to robot framework",
                partial(RobotFramework, self._editorWidget.sceneManager),
            )
        )
        exportMenu.addAction(
            CreateAction(
                self,
                "&PDF",
                None,
                "export to pytorch",
                partial(Pytorch, self._editorWidget.sceneManager),
            )
        )

        fileMenu.addSeparator()
        fileMenu.addAction(
            CreateAction(
                self,
                "&Close",
                "Ctrl+W",
                "close model",
                partial(Close, self._editorWidget.sceneManager),
            )
        )
        fileMenu.addAction(
            CreateAction(
                self,
                "E&xit",
                "Ctrl+Q",
                "exit program",
                partial(Exit, self._editorWidget.sceneManager),
            )
        )

        # * edit menu
        editMenu.addAction(
            CreateAction(
                self,
                "&Undo",
                "Ctrl+Z",
                "create new graph model",
                partial(Undo, self._editorWidget.sceneManager),
            )
        )
        editMenu.addAction(
            CreateAction(
                self,
                "&Redo",
                "Ctrl+R",
                "create new graph model",
                partial(Redo, self._editorWidget.sceneManager),
            )
        )
        editMenu.addSeparator()
        editMenu.addAction(
            CreateAction(
                self,
                "Select &All",
                "Ctrl+A",
                "select all graphics item(s)",
                partial(SelectAll, self._editorWidget.sceneManager),
            )
        )
        editMenu.addAction(
            CreateAction(
                self,
                "D&eselect All",
                "Ctrl+Shift+A",
                "deselect all graphics item(s)",
                partial(DeselectAll, self._editorWidget.sceneManager),
            )
        )
        editMenu.addSeparator()
        editMenu.addAction(
            CreateAction(
                self,
                "&Delete",
                "Delete",
                "delete graphics item(s)",
                partial(Delete, self._editorWidget.sceneManager),
            )
        )
        editMenu.addSeparator()
        editMenu.addAction(
            CreateAction(
                self,
                "Cu&t",
                "Ctrl+X",
                "create new graph model",
                partial(Cut, self._editorWidget.graphicView),
            )
        )
        editMenu.addAction(
            CreateAction(
                self,
                "&Copy",
                "Ctrl+C",
                "create new graph model",
                partial(Copy, self._editorWidget.graphicView),
            )
        )
        editMenu.addAction(
            CreateAction(
                self,
                "&Paste",
                "Ctrl+V",
                "create new graph model",
                partial(Paste, self._editorWidget.graphicView),
            )
        )
        editMenu.addSeparator()
        editMenu.addAction(
            CreateAction(
                self,
                "&Find",
                "Ctrl+F",
                "create new graph model",
                partial(Find, self._editorWidget.graphicView, self._editorWidget),
            )
        )
        editMenu.addSeparator()
        editMenu.addAction(
            CreateAction(
                self,
                "&Preferences",
                "Ctrl+,",
                "preferences",
                partial(Preferences, self._editorWidget.sceneManager),
            )
        )

        # * help menu
        helpMenu.addAction(
            CreateAction(
                self,
                "&Welcome",
                tooltip="welcome notes",
                callback=partial(Welcome, self._editorWidget.sceneManager),
            )
        )
        helpMenu.addAction(
            CreateAction(
                self,
                "&Documentation",
                tooltip="documentation",
                callback=partial(Documentation, self._editorWidget.sceneManager),
            )
        )
        helpMenu.addAction(
            CreateAction(
                self,
                "&Release Notes",
                tooltip="changelog",
                callback=partial(Changelog, self._editorWidget.sceneManager),
            )
        )
        helpMenu.addSeparator()
        helpMenu.addAction(
            CreateAction(
                self,
                "&Keyboard Shortcuts",
                tooltip="shortcut key bindings",
                callback=partial(Shortcuts, self._editorWidget.sceneManager),
            )
        )
        helpMenu.addSeparator()
        helpMenu.addAction(
            CreateAction(
                self,
                "Sc&ene Information",
                shortcut="Ctrl+Shift+D",
                tooltip="jeditor dump debug log",
                callback=partial(DebugSceneInformation, self._editorWidget.sceneManager),
            )
        )
        helpMenu.addSeparator()
        helpMenu.addAction(
            CreateAction(
                self,
                "&About",
                tooltip="about jeditor",
                callback=partial(About, self._editorWidget.sceneManager),
            )
        )


def New(sceneManager: JSceneManager):
    logger.debug("new")


def Open(graphicsView: JGraphicView):
    logger.debug("open")
    filename = JFileDialog.GetOpenFileName(QDialog())
    if filename:
        graphicsView.OpenFile(filename)


def Close(sceneManager: JSceneManager):
    logger.debug("close")


def Save(graphicsView: JGraphicView):
    logger.debug("save")
    filename = JFileDialog.GetSaveFileName(QDialog())
    if filename:
        graphicsView.SaveFile(filename)


def SaveAs(sceneManager: JSceneManager):
    logger.debug("save as")


def Exit(sceneManager: JSceneManager):
    logger.debug("exit")


def Delete(sceneManager: JSceneManager):
    logger.debug("delete")
    sceneManager.RemoveFromScene()


def Undo(sceneManager: JSceneManager):
    logger.debug("undo")
    sceneManager.undoStack.undo()


def Redo(sceneManager: JSceneManager):
    logger.debug("redo")
    sceneManager.undoStack.redo()


def SelectAll(sceneManager: JSceneManager):
    logger.debug("select all")


def DeselectAll(sceneManager: JSceneManager):
    logger.debug("deselect all")


def Cut(graphicsView: JGraphicView):
    logger.debug("cut")
    graphicsView.CutGraphicsItems()


def Copy(graphicsView: JGraphicView):
    logger.debug("copy")
    graphicsView.CopyGraphicsItems()


def Paste(graphicsView: JGraphicView):
    logger.debug("paste")
    graphicsView.PasteGraphicsItems()


def _Find(a0: str):
    print(a0)


def Find(graphicsView: JGraphicView, editorWidget: QWidget):
    logger.debug("find")

    def _Find(a0: str):
        print(a0)

    data = graphicsView.sceneManager.dataStreamer.Serialize()
    searchBox = JSearchBox(editorWidget, columns=["Name", "UID", "Type"])

    for idx, grNode in enumerate(data.nodes):
        searchBox.AddItems(idx, grNode.node.name, grNode.node.uid)

    searchBox.nodeUID.connect(graphicsView.FocusSelection)  # type:ignore
    searchBox.show()


def Welcome(sceneManager: JSceneManager):
    logger.debug("welcome")


def Documentation(sceneManager: JSceneManager):
    logger.debug("documentation")


def Changelog(sceneManager: JSceneManager):
    logger.debug("changelog")


def Shortcuts(sceneManager: JSceneManager):
    logger.debug("shortcuts")


def DebugSceneInformation(sceneManager: JSceneManager):
    logger.debug("debug")
    sceneManager.DebugSceneInformation()


def About(sceneManager: JSceneManager):
    logger.debug("about")


def Preferences(sceneManager: JSceneManager):
    logger.debug("preferences")


def RobotFramework(sceneManager: JSceneManager):
    logger.debug("about")


def Pytorch(sceneManager: JSceneManager):
    logger.debug("preferences")
