import logging
from typing import Dict, List, Optional, Tuple, Union
import json
from jigls.jeditor.stylesheet import STYLE_TREE
from jigls.jeditor.widgets.custom import (
    DelegateTreeOperations,
    JQComboBox,
    JQLabel,
    JQLineEdit,
    JQTextEdit,
    PropertiesSection,
    PropertyTree,
)
from jigls.logger import logger
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QValidator
from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QScrollArea,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


from typing import Optional


class UserDataPropertyTree(PropertyTree):
    def __init__(self, parent: QTreeWidget):
        super().__init__(parent)

    def AddChild(self, data: str = "Data"):
        self._AddChild(data)

    def _AddChild(self, data: str = "Data"):
        entry = QTreeWidgetItem()
        self.addChild(entry)

        entry.setFlags(
            Qt.ItemIsEnabled  # type:ignore
            | Qt.ItemIsEditable  # type:ignore
            | Qt.ItemIsSelectable  # type:ignore
        )

        socket = JQLabel("Value")
        data_ = JQLineEdit(text=data, readOnly=False)

        self.rootTree.setItemWidget(entry, 0, socket)
        self.rootTree.setItemWidget(entry, 1, data_)

    def Serialize(self) -> Dict[str, List[str]]:
        # super().Serialize()
        # print(self.columnCount(), self.childCount(), root.childCount())
        return {
            self.__TYPE__: [
                self.rootTree.itemWidget(self.rootTree.topLevelItem(0).child(i), 1).text()
                for i in range(self.rootTree.topLevelItem(0).childCount())
            ]
        }

    def Deserialize(self, data: List[str]):
        # return super().Deserialize()
        for d in data:
            self.AddChild(d)


class UserDataPropertyWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None, sectionName: str = "section") -> None:
        super().__init__(parent=parent)

        self.sectionName = sectionName
        self.propertiesSection = PropertiesSection(columnCount=2)

        self.initUI()

    def initUI(self):
        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())

        self.propertiesSection.setIndentation(8)
        self.layout().addWidget(self.propertiesSection)

        # * add section 1
        self.propertyTree1 = UserDataPropertyTree(self.propertiesSection)
        self.propertyTree1.setText(0, self.sectionName)
        self.propertiesSection.setItemWidget(
            self.propertyTree1, 1, DelegateTreeOperations(self.propertyTree1)
        )

    def Serialize(self) -> Dict[str, List[str]]:
        return self.propertyTree1.Serialize()

    def Deserialize(self, data: List[str]):
        self.propertyTree1.Deserialize(data)


class DataContent(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._property: List[Tuple[str, QWidget]] = []
        self.groupBox = QGroupBox("User data space")
        self.initUI()

    def initUI(self):
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.groupBox.setLayout(QFormLayout())

        scroll = QScrollArea()
        scroll.setWidget(self.groupBox)
        scroll.setWidgetResizable(True)

        self.layout().addWidget(scroll)

    def CheckDuplicateLabel(self, label: str) -> bool:

        dups = list(filter(lambda prop: prop[0] == label, self._property))
        if len(dups) > 0:
            logger.error(f"User data content duplicate label: {label}")
            return True
        return False

    def AddComboBox(self, label: str, options: List[str]):
        if self.CheckDuplicateLabel(label):
            return

        _property = JQComboBox(options)
        self.groupBox.layout().addRow(JQLabel(label), _property)
        self._property.append((label, _property))

    def AddLineEdit(
        self,
        label: str,
        text: Optional[str] = None,
        placeholder: Optional[str] = None,
        readOnly: bool = False,
    ):
        if self.CheckDuplicateLabel(label):
            return

        _property = JQLineEdit(text=text, placeholder=placeholder, readOnly=readOnly)
        self.groupBox.layout().addRow(JQLabel(label), _property)
        self._property.append((label, _property))

    def AddTextEdit(
        self,
        label: str,
        text: Optional[str] = None,
        placeholder: Optional[str] = None,
        readOnly: bool = False,
    ):
        if self.CheckDuplicateLabel(label):
            return

        _property = JQTextEdit(text=text, placeholder=placeholder, readOnly=readOnly)
        self.groupBox.layout().addRow(JQLabel(label), _property)
        self._property.append((label, _property))

    def AddSectionTree(self, label: str, sectionName: str = "sectionName"):
        if self.CheckDuplicateLabel(label):
            return

        _property = UserDataPropertyWidget(sectionName=sectionName)
        self.groupBox.layout().addRow(JQLabel(label), _property)
        self._property.append((label, _property))

    def Serialize(self) -> Dict[str, Dict]:
        _dict = dict()
        for property in self._property:
            _dict[property[0]] = property[1].Serialize()
        # print(json.dumps(_dict, indent=2))
        return _dict

    def Deserialize(self, dataContent: Dict[str, Dict]):
        for label, dict_ in dataContent.items():
            dictView = iter(dict_)
            dictKey = next(dictView)
            dictValye = dict_[dictKey]

            dups = list(
                filter(
                    # lambda prop: prop[0] == label and prop[1].widgetType == dictKey,
                    lambda prop: prop[0] == label,
                    self._property,
                )
            )

            if len(dups) > 0:
                # logger.debug(type(dups[0][1]))
                dups[0][1].Deserialize(dictValye)
            else:
                logger.error(f"content not found {label} of type {dictKey}")
