from typing import List
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QTableView,
    QHeaderView,
    QVBoxLayout,
)
from PyQt5.QtCore import QModelIndex, Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class JSearchBox(QDialog):

    nodeUID = QtCore.pyqtSignal(str)  # return uid

    def __init__(self, columns: List[str]):
        super().__init__()
        self.resize(650, 500)
        self.columns: List[str] = columns
        # self.setFixedWidth(500)
        self.setLayout(QVBoxLayout(self))
        self.initUI()

    def initUI(self):

        # * filter model

        self.filterModel = QSortFilterProxyModel(self)
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        # * search

        searchLayout = QHBoxLayout(self)

        self.searchFields = QComboBox(self)
        self.searchFields.addItems(self.columns)

        self.searchInput = QLineEdit(self)
        self.filterModel.setFilterKeyColumn(0)

        searchLayout.addWidget(self.searchFields)
        searchLayout.addWidget(self.searchInput)
        self.layout().addLayout(searchLayout)

        # * model

        model = QStandardItemModel(self)
        model.setColumnCount(len(self.columns))
        model.setHorizontalHeaderLabels(self.columns)
        self.filterModel.setSourceModel(model)

        # * table view

        self.table = QTableView(self)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setModel(self.filterModel)
        self.layout().addWidget(self.table)

        # * trigger

        self.searchInput.textChanged.connect(self.filterModel.setFilterRegExp)
        self.searchFields.currentTextChanged.connect(self._FieldChange)
        self.table.clicked[QtCore.QModelIndex].connect(self.Search)  # type:ignore

    def _FieldChange(self, a0: str):
        self.filterModel.setFilterKeyColumn(self.columns.index(a0))

    def AddItems(self, row: int, name: str, uid: str, type: str = "BaseType"):

        nameItem = QStandardItem(name)
        uidItem = QStandardItem(uid)
        typeItem = QStandardItem(type)

        nameItem.setEditable(False)
        uidItem.setEditable(False)
        typeItem.setEditable(False)

        self.filterModel.sourceModel().setItem(row, 0, nameItem)
        self.filterModel.sourceModel().setItem(row, 1, uidItem)
        self.filterModel.sourceModel().setItem(row, 2, typeItem)

    def Search(self, index: QModelIndex):

        # *
        sib1 = index.siblingAtRow(index.row()).siblingAtColumn(0)
        sib2 = index.siblingAtRow(index.row()).siblingAtColumn(1)
        sib3 = index.siblingAtRow(index.row()).siblingAtColumn(2)

        print(
            self.filterModel.itemData(sib1)[0],
            self.filterModel.itemData(sib2)[0],
            self.filterModel.itemData(sib3)[0],
        )