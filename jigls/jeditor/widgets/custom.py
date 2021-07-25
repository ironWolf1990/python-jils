import logging
from typing import Dict, List, Optional

from jigls.jeditor.stylesheet import STYLE_TREE
from jigls.logger import logger
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


from typing import Optional


class JQLabel(QLabel):

    __TYPE__ = "JQLabel"

    def __init__(self, text: str, maxWidth: int = 140):
        super().__init__(text=text)
        self.setFixedWidth(maxWidth)

    @property
    def widgetType(self):
        return self.__TYPE__

    def Serialize(self) -> Dict[str, str]:
        return {self.__TYPE__: self.text()}

    def Deserialize(self, text: str):
        self.setText(text)


class JQLineEdit(QLineEdit):

    __TYPE__ = "JQLineEdit"

    def __init__(
        self,
        text: Optional[str] = None,
        placeholder: Optional[str] = None,
        validator: Optional[QValidator] = None,
        width: Optional[int] = None,
        readOnly: bool = True,
    ):
        super().__init__()
        if text:
            self.setText(text)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setReadOnly(readOnly)
        if width:
            self.setFixedWidth(width)
        if validator:
            self.setValidator(validator)

    @property
    def widgetType(self):
        return self.__TYPE__

    def Serialize(self) -> Dict[str, str]:
        return {self.__TYPE__: self.text()}

    def Deserialize(self, text: str):
        self.setText(text)


class JQTextEdit(QTextEdit):

    __TYPE__ = "JQTextEdit"

    def __init__(
        self,
        text: Optional[str] = None,
        placeholder: Optional[str] = None,
        readOnly: bool = True,
        maxCharacter: Optional[int] = None,
    ):
        super().__init__()

        self.maxCharacter: Optional[int] = maxCharacter

        if text:
            self.setText(text)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setReadOnly(readOnly)

        self.textChanged.connect(self.CheckTextLimit)

    @property
    def widgetType(self):
        return self.__TYPE__

    def CheckTextLimit(self):
        if self.maxCharacter:
            if len(self.toPlainText()) > self.maxCharacter:
                self.setText(self.toPlainText()[: self.maxCharacter])

    def Serialize(self) -> Dict[str, str]:
        return {self.__TYPE__: self.toPlainText()}

    def Deserialize(self, text: str):
        self.setText(text)


class JQComboBox(QComboBox):

    __TYPE__ = "JQComboBox"

    def __init__(self, options: List[str] = [""]) -> None:
        super().__init__()

        for op in options:
            self.addItem(op)

    @property
    def widgetType(self):
        return self.__TYPE__

    def Serialize(self) -> Dict[str, str]:
        return {self.__TYPE__: self.currentText()}

    def Deserialize(self, text: str):
        for i in range(self.count()):
            if text == self.itemText(i):
                self.setCurrentIndex(i)
                return
        logger.error("invalid option")


class JQCheckBox(QCheckBox):
    def __init__(self, text: Optional[str] = None, enabled=True, Checked=True):
        super().__init__()

        if text:
            self.setText(text)
        self.setEnabled(enabled)
        if Checked:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)

    @property
    def widgetType(self):
        return self.__TYPE__

    def Serialize(self):
        raise NotImplementedError()

    def Deserialize(self):
        raise NotImplementedError()


class JQCheckBoxWidget(QWidget):
    def __init__(
        self, parent: Optional[QWidget] = None, text: Optional[str] = None, enabled=True, Checked=True
    ) -> None:
        super().__init__(parent=parent)

        self.setLayout(QHBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(JQCheckBox(text=text, enabled=enabled, Checked=Checked))

    @property
    def widgetType(self):
        return self.__TYPE__

    def Serialize(self):
        raise NotImplementedError()

    def Deserialize(self):
        raise NotImplementedError()


class PropertyTree(QTreeWidgetItem):

    __TYPE__ = "JQPropertyTree"

    def __init__(self, parent: QTreeWidget):
        super().__init__(parent)
        self.rootTree: QTreeWidget = parent
        self.setExpanded(True)

    # ? should be reimplemented based on use case
    def _AddChild(self):
        entry = QTreeWidgetItem()
        self.addChild(entry)

        entry.setFlags(
            Qt.ItemIsEnabled  # type:ignore
            | Qt.ItemIsEditable  # type:ignore
            | Qt.ItemIsSelectable  # type:ignore
        )

        label = QLabel("label")
        line = QLineEdit("this is text")

        self.rootTree.setItemWidget(entry, 0, label)
        self.rootTree.setItemWidget(entry, 1, line)

    @property
    def widgetType(self):
        return self.__TYPE__

    def _RemoveChild(self):
        for item in self.rootTree.selectedItems():
            self.removeChild(item)

    def Serialize(self):
        raise NotImplementedError()

    def Deserialize(self):
        raise NotImplementedError()


class DelegateTreeOperations(QWidget):
    def __init__(self, sectionTree: PropertyTree):
        super().__init__(parent=None)

        self.sectionTree = sectionTree

        self.initUI()

    # ? should be reimplemented based on use case
    def initUI(self):
        self.setLayout(QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setAlignment(Qt.AlignLeft)

        buttonAdd = QToolButton()
        buttonAdd.setIcon(QIcon.fromTheme("document-new"))
        buttonAdd.setCheckable(True)
        buttonAdd.setChecked(False)
        buttonAdd.setStyleSheet("QToolButton { border: none; }")
        buttonAdd.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        buttonRemove = QToolButton()
        buttonRemove.setIcon(QIcon.fromTheme("edit-delete"))
        buttonRemove.setCheckable(True)
        buttonRemove.setChecked(False)
        buttonRemove.setStyleSheet("QToolButton { border: none; }")
        buttonRemove.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.layout().addWidget(buttonAdd)
        self.layout().addWidget(buttonRemove)

        buttonAdd.clicked.connect(self.AddChild)
        buttonRemove.clicked.connect(self.RemoveChild)

    def AddChild(self):
        self.sectionTree._AddChild()

    def RemoveChild(self):
        self.sectionTree._RemoveChild()


class PropertiesSection(QTreeWidget):
    def __init__(self, parent: Optional[QWidget] = None, columnCount: int = 2) -> None:
        super().__init__(parent=parent)
        self.setHeaderHidden(True)
        self.setColumnCount(columnCount)

        self.setAlternatingRowColors(True)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        # self.setStyleSheet(STYLE_TREE)

    def AddSectionTree(self):
        raise NotImplementedError("")
