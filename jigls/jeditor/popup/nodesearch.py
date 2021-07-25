from typing import List
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QTableView,
    QHeaderView,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import QModelIndex, Qt, QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from typing import Optional


class JSearchBox(QDialog):

    signalNodeUID = pyqtSignal(str)  # return uid

    def __init__(self, parent: Optional[QWidget], columns: List[str]):
        super().__init__(parent=parent)

        self.setWindowTitle("J-Search")
        self.resize(650, 500)
        # self.setFixedWidth(500)

        self.columns: List[str] = columns

        self.setLayout(QVBoxLayout(self))

        self.initUI()

    def initUI(self):

        # * filter model

        self.filterModel = QSortFilterProxyModel(self)
        self.filterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filterModel.setFilterKeyColumn(0)

        # * search

        searchLayout = QHBoxLayout(self)

        self.searchComboBox = QComboBox(self)
        self.searchComboBox.addItems(self.columns)

        self.searchInput = QLineEdit(self)

        searchLayout.addWidget(self.searchComboBox)
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
        self.searchComboBox.currentTextChanged.connect(self._FieldChange)
        self.table.clicked[QModelIndex].connect(self.Search)  # type:ignore

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

        sib1 = index.siblingAtRow(index.row()).siblingAtColumn(0)
        sib2 = index.siblingAtRow(index.row()).siblingAtColumn(1)
        sib3 = index.siblingAtRow(index.row()).siblingAtColumn(2)

        self.signalNodeUID.emit(  # type:ignore
            self.filterModel.itemData(sib2)[0],
        )

        # print(
        #     self.filterModel.itemData(sib1)[0],
        #     self.filterModel.itemData(sib2),
        #     self.filterModel.itemData(sib3)[0],
        # )
