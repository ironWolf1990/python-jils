import logging
from pprint import pprint
from .socketmanager import JNodeSocketManager
from .contentwidget import JNodeContent
from jeditor.constants import JCONSTANTS
from typing import Dict, List, Optional, OrderedDict, Tuple
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsProxyWidget,
    QGraphicsSceneMouseEvent,
    QGraphicsTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
)
from jeditor.logger import logger

logger = logging.getLogger(__name__)


class JGraphicNode(QGraphicsItem):
    def __init__(
        self,
        parent: Optional[QGraphicsItem] = None,
        nodeId: str = "",
        title: str = "Base Node",
        nodeContent: Optional[JNodeContent] = None,
    ) -> None:
        super().__init__(parent=parent)

        self._nodeId: str = nodeId
        self._nodeTitle: str = title
        self._nodeContent: Optional[JNodeContent] = nodeContent

        self._nodeSocketManager: JNodeSocketManager = JNodeSocketManager(
            self, self._nodeId
        )
        self._nodeTitleText: QGraphicsTextItem = QGraphicsTextItem(self)

        self.initUI()
        self._InitContent(nodeContent)

    @property
    def nodeTitle(self):
        return self._nodeTitle

    @property
    def nodeWidth(self):
        return self._nodeWidth

    @property
    def nodeHeight(self):
        return self._nodeHeight

    @nodeTitle.setter
    def nodeTitle(self, value: str) -> None:
        self._nodeTitle = value
        self._nodeTitleText.setPlainText(value)

    @property
    def nodeId(self):
        return self._nodeId

    @property
    def socketManager(self) -> JNodeSocketManager:
        return self._nodeSocketManager

    def initUI(self):
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        # * node dimension
        self._nodeWidth: int = JCONSTANTS.GRNODE.NODE_WIDHT
        self._nodeHeight: int = JCONSTANTS.GRNODE.NODE_HEIGHT
        self._nodeEdgeSize: float = JCONSTANTS.GRNODE.NODE_PADDING
        self._nodePenDefault: QtGui.QPen = QtGui.QPen(
            QtGui.QColor(JCONSTANTS.GRNODE.COLOR_DEFAULT)
        )
        self._nodePenSelected: QtGui.QPen = QtGui.QPen(
            QtGui.QColor(JCONSTANTS.GRNODE.COLOR_SELECTED)
        )
        self._nodeBrushBackground: QtGui.QBrush = QtGui.QBrush(
            QtGui.QColor(JCONSTANTS.GRNODE.COLOR_BACKGROUND)
        )

        # * title
        self._nodeTitleColor = QtCore.Qt.black
        self._nodeTitleFont: QtGui.QFont = QtGui.QFont(
            JCONSTANTS.GRNODE.TITLE_FONT, JCONSTANTS.GRNODE.TITLE_FONT_SIZE
        )
        self._nodeTitleFont.setItalic(True)
        self._nodeTitleFont.setBold(True)
        self._nodeTitlePadding: int = JCONSTANTS.GRNODE.TITLE_PADDING
        self._nodeTitleHeight: float = JCONSTANTS.GRNODE.TITLE_HEIGHT
        self._nodeTitleBrush: QtGui.QBrush = QtGui.QBrush(
            QtGui.QColor(JCONSTANTS.GRNODE.COLOR_TITLE)
        )
        self._nodeTitleText.setDefaultTextColor(self._nodeTitleColor)
        self._nodeTitleText.setFont(self._nodeTitleFont)
        self._nodeTitleText.setPos(3 * self._nodeTitlePadding, 0)
        self._nodeTitleText.setTextWidth(self._nodeWidth - 2 * self._nodeTitlePadding)
        self._nodeTitleText.setPlainText(self._nodeTitle)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(
            0,
            0,
            self._nodeWidth,
            self._nodeHeight,
        )

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget],
    ) -> None:

        # * title
        titlePath = QtGui.QPainterPath()
        titlePath.setFillRule(QtCore.Qt.WindingFill)

        titlePath.addRoundedRect(
            0,
            0,
            self._nodeWidth,
            self._nodeTitleHeight,
            self._nodeEdgeSize,
            self._nodeEdgeSize,
        )

        titlePath.addRect(
            0,
            self._nodeTitleHeight - self._nodeEdgeSize,
            self._nodeEdgeSize,
            self._nodeEdgeSize,
        )

        titlePath.addRect(
            self._nodeWidth - self._nodeEdgeSize,
            self._nodeTitleHeight - self._nodeEdgeSize,
            self._nodeEdgeSize,
            self._nodeEdgeSize,
        )

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._nodeTitleBrush)
        painter.drawPath(titlePath.simplified())

        # ? content
        ContentPath = QtGui.QPainterPath()
        ContentPath.setFillRule(QtCore.Qt.WindingFill)
        ContentPath.addRoundedRect(
            0,
            self._nodeTitleHeight,
            self._nodeWidth,
            self._nodeHeight - self._nodeTitleHeight,
            self._nodeEdgeSize,
            self._nodeEdgeSize,
        )
        ContentPath.addRect(
            0, self._nodeTitleHeight, self._nodeEdgeSize, self._nodeEdgeSize
        )
        ContentPath.addRect(
            self._nodeWidth - self._nodeEdgeSize,
            self._nodeTitleHeight,
            self._nodeEdgeSize,
            self._nodeEdgeSize,
        )
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._nodeBrushBackground)
        painter.drawPath(ContentPath.simplified())

        # ? outline
        outline = QtGui.QPainterPath()
        outline.addRoundedRect(
            0,
            0,
            self._nodeWidth,
            self._nodeHeight,
            self._nodeEdgeSize,
            self._nodeEdgeSize,
        )

        painter.setPen(
            self._nodePenDefault if not self.isSelected() else self._nodePenSelected
        )
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(outline.simplified())

    def _InitContent(self, nodeContent: Optional[JNodeContent]):
        # nodeContent = None
        if nodeContent is not None:
            self._graphicsNodeContent = QGraphicsProxyWidget(self)
            nodeContent.setGeometry(
                int(self._nodeEdgeSize),
                int(self._nodeTitleHeight + self._nodeEdgeSize),
                int(self._nodeWidth - 2 * self._nodeEdgeSize),
                int(self._nodeHeight - 2 * self._nodeEdgeSize - self._nodeTitleHeight),
            )
            self._graphicsNodeContent.setWidget(nodeContent)

    def Serialize(self) -> OrderedDict:
        node = OrderedDict(
            {
                "nodeId": self._nodeId,
                "posX": self.pos().x(),
                "posY": self.pos().y(),
            }
        )
        node.update(self._nodeSocketManager.Serialize())
        return node

    @classmethod
    def Deserialize(cls, data: Dict):
        instance = cls(nodeId=data["nodeId"])
        instance.setPos(QtCore.QPointF(data["posX"], data["posY"]))
        for _, socket in data["socketInfo"].items():
            instance.socketManager.AddSocket(
                socket["socketId"], socket["socketType"], socket["multiConnection"]
            )
        return instance
