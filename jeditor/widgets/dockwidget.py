from typing import Optional
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class Section(QTreeWidgetItem):
    def __init__(self, parent: QTreeWidget, name: str):
        super().__init__(parent)
        self.rootTree: QTreeWidget = parent
        self.name = name
        self.setExpanded(True)

    def Serialize(self):
        pass

    def Deserialize(self):
        pass


class DelegateSectionOperations(QWidget):
    def __init__(self, title: str, item: Section):
        super().__init__(parent=None)

        self.sectionTree = item

        lable = QLabel()
        lable.setText(title)

        buttonAdd = QtWidgets.QToolButton()
        buttonAdd.setIcon(QIcon.fromTheme("document-new"))
        buttonAdd.setCheckable(True)
        buttonAdd.setChecked(False)
        buttonAdd.setStyleSheet("QToolButton { border: none; }")
        buttonAdd.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        buttonRemove = QtWidgets.QToolButton()
        buttonRemove.setIcon(QIcon.fromTheme("edit-delete"))
        buttonRemove.setCheckable(True)
        buttonRemove.setChecked(False)
        buttonRemove.setStyleSheet("QToolButton { border: none; }")
        buttonRemove.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().addWidget(lable)
        self.layout().addWidget(buttonAdd)
        self.layout().addWidget(buttonRemove)

        buttonAdd.clicked.connect(self.AddChild)
        buttonRemove.clicked.connect(self.RemoveChild)

    def AddChild(self):
        item = QTreeWidgetItem()

        item.setFlags(
            QtCore.Qt.ItemIsEnabled  # type:ignore
            | QtCore.Qt.ItemIsEditable  # type:ignore
            | QtCore.Qt.ItemIsSelectable  # type:ignore
        )
        self.sectionTree.addChild(item)
        self.sectionTree.rootTree.setItemWidget(item, 0, QLineEdit("a"))

    def RemoveChild(self):
        for item in self.sectionTree.rootTree.selectedItems():
            self.sectionTree.removeChild(item)


class PropertiesTree(QTreeWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.setHeaderHidden(True)

    def AddPropertySection(self, sectionName="section") -> Section:
        section = Section(self, sectionName)
        # section.setText(0, sectionName)
        self.setItemWidget(section, 0, DelegateSectionOperations(sectionName, section))
        return section


class ExDockWidget1(QDialog):
    def __init__(self, parent: Optional[Optional[QWidget]] = None) -> None:
        super().__init__(parent=parent)

        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        # self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())
        self.properties = PropertiesTree()
        self.properties.setIndentation(8)
        self.layout().addWidget(self.properties)

        s1 = self.properties.AddPropertySection("seaction 1")
        s2 = self.properties.AddPropertySection("section 2")
        s3 = self.properties.AddPropertySection()


class ExDockWidget2(QWidget):
    def __init__(self, parent: Optional[Optional[QWidget]] = None) -> None:
        super().__init__(parent=parent)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())
        self.properties = PropertiesTree()
        self.properties.setIndentation(8)
        self.layout().addWidget(self.properties)

        s1 = self.properties.AddPropertySection("seaction 1")