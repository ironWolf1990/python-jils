import logging
from typing import Optional

from jigls.jeditor.widgets.custom import JQLabel, JQLineEdit, PropertiesSection, PropertyTree
from jigls.logger import logger
from PyQt5.QtWidgets import QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)


class JConnPropertyTree(PropertyTree):
    def __init__(self, parent: QTreeWidget):
        super().__init__(parent)

    def AddChild(self, socketName: str, socketParent: str):
        self._AddChild(socketName, socketParent)

    def _AddChild(self, socketName: str, socketParent: str):
        entry = QTreeWidgetItem()
        self.addChild(entry)

        entry.setFlags(
            Qt.ItemIsEnabled  # type:ignore
            | Qt.ItemIsEditable  # type:ignore
            | Qt.ItemIsSelectable  # type:ignore
        )

        socket = QLabel(socketName)
        parent = QLabel(socketParent)

        self.rootTree.setItemWidget(entry, 0, socket)
        self.rootTree.setItemWidget(entry, 1, parent)


class JConnectionInfoWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self.properties = PropertiesSection(columnCount=2)
        self.initUI()
        self.Populate()

    def initUI(self):
        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setLayout(QVBoxLayout())

        self.properties.setIndentation(8)
        self.layout().addWidget(self.properties)

    def Serialize(self):
        pass

    def Populate(self):
        self.propertyTree1 = JConnPropertyTree(self.properties)
        self.propertyTree1.setText(0, "Socket Name")
        self.propertyTree1.setText(1, "Incoming")

        self.propertyTree1.AddChild("1", "1p")
        self.propertyTree1.AddChild("2", "1p")

        self.propertyTree2 = JConnPropertyTree(self.properties)
        self.propertyTree2.setText(0, "Socket Name")
        self.propertyTree2.setText(1, "Outgoing")
