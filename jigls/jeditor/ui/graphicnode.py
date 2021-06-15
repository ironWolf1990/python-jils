from __future__ import annotations
from jigls.jcore.ibase import ISocket

import logging
import typing
from typing import List, Optional, Set

from jigls.jeditor.base.nodebase import JBaseNode
from jigls.jeditor.base.socketbase import JBaseSocket
from jigls.jeditor.constants import JCONSTANTS
from jigls.jeditor.jdantic import JGrNodeModel
from jigls.logger import logger
from jigls.jeditor.ui.graphicsocket import JGraphicsSocket
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

logger = logging.getLogger(__name__)


class JGraphicsNode(QGraphicsItem):

    __NODE__: str = "BaseNode"

    def __init__(self, baseNode: JBaseNode, parent: Optional[QGraphicsItem] = None) -> None:

        super().__init__(parent=parent)

        self._baseNode: JBaseNode = baseNode

        # todo find a better way to draw the sockets
        self.__graphicsSocketList: List[JGraphicsSocket] = []

        self.initUI()
        self.initSocketUI()

    @property
    def baseNode(self) -> JBaseNode:
        return self._baseNode

    @property
    def nodeTypeName(self):
        return self.__NODE__

    @property
    def graphicsSocketList(self) -> List[JGraphicsSocket]:
        return self.__graphicsSocketList

    def GetNodeName(self) -> str:
        return self.baseNode.name

    def SetNodeName(self, name: str):
        self.baseNode.name = name

    def uid(self) -> str:
        return self.baseNode.uid

    def GetSocketList(self) -> Set[ISocket]:
        return self.baseNode.socketList

    def GetInSocketList(self) -> List[JBaseSocket]:
        return self.baseNode.InSocketList()

    def GetOutSocketList(self) -> List[JBaseSocket]:
        return self.baseNode.OutSocketList()

    def GetSocketByName(self, name: str) -> Optional[ISocket]:
        return self.baseNode.GetSocketByName(name)

    def GetSocketByUID(self, uid: str) -> Optional[ISocket]:
        return self.baseNode.GetSocketByUid(uid)

    def AddInputSocket(self, name: str, multiConnection: bool):
        return self.baseNode.AddInputSocket(name, multiConnection=multiConnection)

    def AddOutputSocket(self, name: str, multiConnection: bool):
        return self.baseNode.AddOutputSocket(name, multiConnection=multiConnection)

    def initUI(self):
        self.setZValue(1000)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        # ! high cpu usage bug fix sollution
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # * title
        titleFont: QtGui.QFont = QtGui.QFont(JCONSTANTS.GRNODE.TITLE_FONT, JCONSTANTS.GRNODE.TITLE_FONT_SIZE)
        titleFont.setItalic(True)
        titleFont.setBold(True)

        self._titleText: QGraphicsTextItem = QGraphicsTextItem(self)
        self._titleText.setDefaultTextColor(QtCore.Qt.black)
        self._titleText.setFont(titleFont)
        self._titleText.setPos(3 * JCONSTANTS.GRNODE.TITLE_PADDING, 0)
        self._titleText.setTextWidth(JCONSTANTS.GRNODE.NODE_WIDHT - 2 * JCONSTANTS.GRNODE.TITLE_PADDING)
        self._titleText.setPlainText(self.nodeTypeName)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, JCONSTANTS.GRNODE.NODE_WIDHT, JCONSTANTS.GRNODE.NODE_HEIGHT)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QStyleOptionGraphicsItem,
        widget: typing.Optional[QWidget],
    ) -> None:

        self._titleText.setPlainText(f"X:{self.pos().x()} Y: {self.pos().y()}")

        # * title
        titlePath = QtGui.QPainterPath()
        titlePath.setFillRule(QtCore.Qt.WindingFill)

        titlePath.addRoundedRect(
            0,
            0,
            JCONSTANTS.GRNODE.NODE_WIDHT,
            JCONSTANTS.GRNODE.TITLE_HEIGHT,
            JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
        )

        titlePath.addRect(
            0,
            JCONSTANTS.GRNODE.TITLE_HEIGHT - JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
        )

        titlePath.addRect(
            JCONSTANTS.GRNODE.NODE_WIDHT - JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.TITLE_HEIGHT - JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
        )

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(JCONSTANTS.GRNODE.COLOR_TITLE)))
        painter.drawPath(titlePath.simplified())

        # ? content
        ContentPath = QtGui.QPainterPath()
        ContentPath.setFillRule(QtCore.Qt.WindingFill)
        ContentPath.addRoundedRect(
            0,
            JCONSTANTS.GRNODE.TITLE_HEIGHT,
            JCONSTANTS.GRNODE.NODE_WIDHT,
            JCONSTANTS.GRNODE.NODE_HEIGHT - JCONSTANTS.GRNODE.TITLE_HEIGHT,
            JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
        )
        ContentPath.addRect(
            0,
            JCONSTANTS.GRNODE.TITLE_HEIGHT,
            JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
        )
        ContentPath.addRect(
            JCONSTANTS.GRNODE.NODE_WIDHT - JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.TITLE_HEIGHT,
            JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
        )
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(JCONSTANTS.GRNODE.COLOR_BACKGROUND)))
        painter.drawPath(ContentPath.simplified())

        # ? outline
        outline = QtGui.QPainterPath()
        outline.addRoundedRect(
            0,
            0,
            JCONSTANTS.GRNODE.NODE_WIDHT,
            JCONSTANTS.GRNODE.NODE_HEIGHT,
            JCONSTANTS.GRNODE.NODE_PADDING,
            JCONSTANTS.GRNODE.NODE_PADDING,
        )

        painter.setPen(
            QtGui.QPen(QtGui.QColor(JCONSTANTS.GRNODE.COLOR_DEFAULT))
            if not self.isSelected()
            else QtGui.QPen(QtGui.QColor(JCONSTANTS.GRNODE.COLOR_SELECTED))
        )
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(outline.simplified())

    def initSocketUI(self):
        for idx, socket in enumerate(self.GetInSocketList()):
            self.__graphicsSocketList.append(
                JGraphicsSocket(
                    parent=self,
                    baseSocket=socket,
                    pos=JGraphicsSocket.CalculateSocketPos(
                        index=idx, position=JCONSTANTS.GRSOCKET.POS_LEFT_TOP
                    ),
                )
            )
        for idx, socket in enumerate(self.GetOutSocketList()):
            self.__graphicsSocketList.append(
                JGraphicsSocket(
                    parent=self,
                    baseSocket=socket,
                    pos=JGraphicsSocket.CalculateSocketPos(
                        index=idx, position=JCONSTANTS.GRSOCKET.POS_RIGHT_BOTTOM
                    ),
                )
            )

    def __repr__(self) -> str:
        return self.baseNode.__repr__()

    def Serialize(self):
        return JGrNodeModel(node=self.baseNode.Serialize(), posX=self.pos().x(), posY=self.pos().y())

    @classmethod
    def Deserialize(cls, grNode: JGrNodeModel):
        grNode_ = JGraphicsNode(baseNode=JBaseNode.Deserialize(grNode.node))
        grNode_.setPos(QtCore.QPointF(grNode.posX, grNode.posY))
        return grNode_
