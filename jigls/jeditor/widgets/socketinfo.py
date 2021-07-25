from jigls.jeditor.widgets.custom import JQCheckBox, JQCheckBoxWidget, JQLabel, JQLineEdit
from PyQt5.QtGui import QRegExpValidator
from typing import Optional
from PyQt5.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QTableWidgetItem,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QAbstractScrollArea,
)
from PyQt5.QtCore import QRegExp, Qt, pyqtSlot
from copy import deepcopy


class JSocketInfoWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):

        super().__init__(parent=parent)

        # self.resize(650, 500)
        self.headerLables = [
            "Name",
            "UID",
            "Type",
            "Data type",
            "Dirty",
            "Multiconnect",
            "Exec",
            "OnCh",
            "OnCn",
            # "Monitor on change",
        ]

        self.table = QTableWidget(self)
        self.initUI()
        self.Populate()

    def initUI(self):

        self.setLayout(QVBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().addWidget(self.table)

        self.table.setColumnCount(len(self.headerLables) + 1)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        column = deepcopy(self.headerLables)
        column.append("")
        self.table.setHorizontalHeaderLabels(column)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def Serialize(self):
        pass

    def Populate(self):
        # "name": "in1",
        # "uid": "f2f0baf625a2430d90a944ea689b3a9f",
        # "type": 1,
        # "multiConnect": false,
        # "dataType": "bool",
        # "default": null,
        # "exec": true,
        # "execOnChange": true,
        # "execOnConnect": true,
        # "monitorOnChange": false,
        # "traceback": false
        # "dirty": True

        #     chkBoxItem = QTableWidgetItem(string)
        #     chkBoxItem.setText(string)
        #     chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)  # type:ignore
        #     chkBoxItem.setCheckState(Qt.Unchecked)
        #     self.table.setItem(row, 1, chkBoxItem)

        for idx in range(2):
            self.table.insertRow(self.table.rowCount())

            # * socket name
            name = QTableWidgetItem("in1")
            name.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(idx, 0, name)

            # * UID
            uid = QTableWidgetItem("f2f0baf625a2430d90a944ea689b3a9f")
            uid.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(idx, 1, uid)

            # * type
            type_ = "input"
            # if socket.type == JCONSTANTS.SOCKET.TYPE_OUTPUT:
            #     type_ = "output"
            type = QTableWidgetItem(type_)
            type.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(idx, 2, type)

            # * data type
            dtype = QTableWidgetItem("bool")
            dtype.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(idx, 3, dtype)

            # * is dirty
            dirty = QTableWidgetItem("True")
            dirty.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(idx, 4, dirty)

            # * multiconnect
            multiconnect = QTableWidgetItem("True")
            multiconnect.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(idx, 5, multiconnect)

            # * exec
            self.table.setCellWidget(idx, 6, JQCheckBoxWidget(enabled=False, Checked=False))

            # *exec on change
            self.table.setCellWidget(idx, 7, JQCheckBoxWidget(enabled=True, Checked=False))

            # * exec on connect
            self.table.setCellWidget(idx, 8, JQCheckBoxWidget(enabled=False, Checked=True))

        self.table.resizeColumnsToContents()
