from jigls.jeditor.widgets.datacontent import DataContent
from jigls.jeditor.widgets.connectioninfo import JConnectionInfoWidget
import logging
from typing import Dict, Optional

from jigls.jeditor.jdantic import JGrNodeModel
from jigls.jeditor.widgets.custom import JQLabel, JQLineEdit
from jigls.jeditor.widgets.nodeinfo import JNodeInfoWidget
from jigls.jeditor.widgets.socketinfo import JSocketInfoWidget
from jigls.logger import logger
from PyQt5.QtCore import QRegExp, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class JNodeProperty(QDialog):

    signalDataContent = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self._dataContent: DataContent = DataContent()
        self.resize(650, 500)
        self.initUI()

    @property
    def dataContent(self) -> DataContent:
        return self._dataContent

    def initUI(self):

        self.setLayout(QVBoxLayout(self))

        self.tabs: QTabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabs)

        # ? Add tabs

        # *info tab
        self.infoTab = JNodeInfoWidget(self.tabs)
        self.tabs.addTab(self.infoTab, "Node Info")

        # *socket tab
        self.socketTab = JSocketInfoWidget(self.tabs)
        self.tabs.addTab(self.socketTab, "Sockets Info")

        # *connection tab
        self.connectionTab = JConnectionInfoWidget(self.tabs)
        self.tabs.addTab(self.connectionTab, "Connection Info")

        # *operation tab
        self.functionTab = QWidget(self.tabs)
        self.functionTab.setLayout(QVBoxLayout())
        self.tabs.addTab(self.functionTab, "Operation Info")

        # * data tab
        self._dataContent = DataContent(self.tabs)
        self.tabs.addTab(self._dataContent, "Custom Data")

        # Button
        self.buttonBoxLayout = QHBoxLayout()
        self.buttonBoxLayout.addStretch()

        self.btnOK = QPushButton("Ok")
        self.btnApply = QPushButton("Apply")
        self.btnCancel = QPushButton("Cancel")

        self.btnOK.clicked.connect(self.ButtonPressOk)
        self.btnApply.clicked.connect(self.ButtonPressApply)
        self.btnCancel.clicked.connect(self.ButtonPressCancel)

        self.buttonBoxLayout.addWidget(self.btnOK)
        self.buttonBoxLayout.addWidget(self.btnApply)
        self.buttonBoxLayout.addWidget(self.btnCancel)

        self.layout().addLayout(self.buttonBoxLayout)

    def ButtonPressOk(self):
        self.signalDataContent.emit(self.Serialize())  # type:ignore
        self.close()

    def ButtonPressApply(self):
        self.signalDataContent.emit(self.Serialize())  # type:ignore

    def ButtonPressCancel(self):
        self.close()

    def Serialize(self) -> Dict[str, Dict]:
        return self._dataContent.Serialize()

    def Deserialize(self, dataContent: Dict[str, Dict]):
        self._dataContent.Deserialize(dataContent)
