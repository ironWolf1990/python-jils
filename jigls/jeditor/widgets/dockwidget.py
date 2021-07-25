from jigls.jeditor.widgets.custom import DelegateTreeOperations, PropertiesSection, PropertyTree
from typing import Optional

from jigls.jeditor.stylesheet import STYLE_TREE
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

# https://www.youtube.com/watch?v=m_LXqG8VoDA
# https://www.programmersought.com/article/52804863200/
# https://www.programmersought.com/article/45943894768/


class DockWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)

        self.properties = PropertiesSection(columnCount=2)

        self.initUI()

    def initUI(self):
        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())

        self.properties.setIndentation(8)
        self.layout().addWidget(self.properties)

        # * add section 1
        self.propertyTree1 = PropertyTree(self.properties)
        self.propertyTree1.setText(0, "Section 1")
        self.properties.setItemWidget(self.propertyTree1, 1, DelegateTreeOperations(self.propertyTree1))
        # _ = QtWidgets.QTreeWidgetItem(section, ["ansh", " david"])

        # * add section 2
        self.propertyTree2 = PropertyTree(self.properties)
        self.propertyTree2.setText(0, "Section 2")
        self.properties.setItemWidget(self.propertyTree2, 1, DelegateTreeOperations(self.propertyTree2))
        # _ = QtWidgets.QTreeWidgetItem(section, ["ansh", " david"])
