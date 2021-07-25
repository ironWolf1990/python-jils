from jigls.jeditor.widgets.custom import JQLabel, JQLineEdit
from PyQt5.QtGui import QRegExpValidator
from typing import Optional
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout
from PyQt5.QtCore import QRegExp, Qt, pyqtSignal


class JNodeInfoWidget(QWidget):

    signalNameChange = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self.name: JQLineEdit = JQLineEdit(
            "node name", "max length: 15", QRegExpValidator(QRegExp(r"[\w+]{15}")), readOnly=False
        )
        self.uid: JQLineEdit = JQLineEdit("UUID4", None, readOnly=True)
        self.nodeType: JQLineEdit = JQLineEdit("BaseType", None, readOnly=True)
        self.posX: JQLineEdit = JQLineEdit(None, "64000", readOnly=True, width=70)
        self.posY: JQLineEdit = JQLineEdit(None, "64000", readOnly=True, width=70)

        # self.resize(650, 500)
        self.initUI()

        self.name.textChanged.connect(self._NameChange)

    def _NameChange(self, a0: str):
        self.signalNameChange.emit(self.name.text())  # type:ignore

    def initUI(self):

        self.setLayout(QVBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)

        name = QHBoxLayout()
        name.addWidget(JQLabel("Name"))
        name.addWidget(self.name)
        self.layout().addLayout(name)

        uid = QHBoxLayout()
        uid.addWidget(JQLabel("UID"))
        uid.addWidget(self.uid)
        self.layout().addLayout(uid)

        type = QHBoxLayout()
        type.addWidget(JQLabel("Type"))
        type.addWidget(self.nodeType)
        self.layout().addLayout(type)

        pos = QHBoxLayout()
        pos.addWidget(JQLabel("Position"))
        pos.addWidget(self.posX)
        pos.addWidget(JQLabel(": PosX"))
        pos.addWidget(self.posY)
        pos.addWidget(JQLabel(": PosY"))
        pos.addStretch()
        self.layout().addLayout(pos)

    def Serialize(self):
        pass

    def Populate(self):
        pass
