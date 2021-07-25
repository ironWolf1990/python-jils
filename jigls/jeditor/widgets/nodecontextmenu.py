from functools import partial
import logging
import re
from typing import Callable, Dict, List, Optional

from jigls.jeditor.stylesheet import STYLE_NODECONTEXTTABSEARCH, STYLE_NODECONTEXTMENU
from jigls.logger import logger
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QLineEdit,
    QMenu,
    QWidgetAction,
)


def CreateAction(
    menu: QMenu,
    name: str,
    shortcut: Optional[str] = None,
    tooltip: Optional[str] = None,
    callback: Optional[Callable] = None,
) -> QAction:

    action = QAction(name, parent=menu)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tooltip is not None:
        action.setToolTip(tooltip)
    if callback is not None:
        action.triggered.connect(callback)
    return action


class NodeContextMenu(QMenu):

    signalCreateNode = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._searchLineEdit = QLineEdit()
        self._nodeMenu = self.addMenu("Nodes")
        self._isPopulated: bool = False

        self._suggestions: List[QAction] = []

        self.initUI()

    @property
    def isPopulated(self) -> bool:
        return self._isPopulated

    def initUI(self):

        self.setWindowFlag(Qt.Popup)

        self.setStyleSheet(STYLE_NODECONTEXTMENU)
        self._searchLineEdit.setStyleSheet(STYLE_NODECONTEXTTABSEARCH)

        self._searchLineEdit.setPlaceholderText("search node ...")

        search_widget = QWidgetAction(self)
        search_widget.setDefaultWidget(self._searchLineEdit)

        self.addSection("search")

        self.addAction(search_widget)
        self.setDefaultAction(search_widget)

        self._searchLineEdit.textChanged.connect(self._SearchNode)

    def _Build(self, nodeTypes: List[str]):
        self._isPopulated = True
        for nt in nodeTypes:
            action = CreateAction(self, nt, None, None, partial(self._NodeSelected, nt))
            self._nodeMenu.addAction(action)

    def _FuzzyFinder(self, a0: str) -> List[str]:
        if not a0.isalnum():
            return []

        suggestions = []
        pattern = ".*?".join(a0.lower())
        regex = re.compile(pattern)

        for item in [action.text() for action in self._nodeMenu.actions()]:
            match = regex.search(item.lower())
            if match:
                suggestions.append((len(match.group()), match.start(), item))

        return [x for _, _, x in sorted(suggestions)]

    def _NodeSelected(self, a0: str):
        self.signalCreateNode.emit(a0)  # type:ignore
        self.close()

    def _SearchNode(self, a0: str):

        for sug in self._suggestions:
            self.removeAction(sug)
        self._suggestions.clear()

        if len(a0) == 0:
            return

        for suggestion in self._FuzzyFinder(a0):
            action = CreateAction(self, suggestion, None, None, partial(self._NodeSelected, suggestion))
            self._suggestions.append(action)
            self.addAction(action)

    def setVisible(self, visible: bool) -> None:
        self._searchLineEdit.clear()
        self._searchLineEdit.setFocus()
        return super().setVisible(visible)
