from __future__ import annotations

import logging
import typing
from typing import List, Optional

from jigls.base.nodebase import JBaseNode
from jigls.base.socketbase import JBaseSocket
from jigls.constants import JCONSTANTS
from jigls.jdantic import JGrNodeModel
from jigls.logger import logger
from jigls.ui.graphicsocket import JGraphicsSocket
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsProxyWidget,
    QGraphicsTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

logger = logging.getLogger(__name__)


class JGraphicsNode(QGraphicsItem):
    def __init__(
        self, baseNode: JBaseNode, parent: Optional[QGraphicsItem] = None
    ) -> None:

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
    def nodeTitle(self):
        return self.baseNode.name

    @nodeTitle.setter
    def nodeTitle(self, value: str) -> None:
        self.baseNode.name = value

    def GetNodeName(self) -> str:
        return self.baseNode.name

    def SetNodeName(self, name: str):
        self.baseNode.name = name

    def uid(self) -> str:
        return self.baseNode.uid

    def GetSocketList(self) -> List[JBaseSocket]:
        return self.baseNode.socketList

    def GetInSocketList(self) -> List[JBaseSocket]:
        return self.baseNode.inSocketList

    def GetOutSocketList(self) -> List[JBaseSocket]:
        return self.baseNode.outSocketList

    def GetSocketByName(self, name: str) -> List[JBaseSocket]:
        return self.baseNode.GetSocketByName(name)

    def GetSocketByUID(self, uid: str) -> List[JBaseSocket]:
        return self.baseNode.GetSocketByUID(uid)

    def AddInputSocket(self, name: str, multiConnection: bool):
        return self.baseNode.AddInputSocket(name, multiConnection=multiConnection)

    def AddOutputSocket(self, name: str, multiConnection: bool):
        return self.baseNode.AddOutputSocket(name, multiConnection=multiConnection)

    def initUI(self):
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        # * title
        titleFont: QtGui.QFont = QtGui.QFont(
            JCONSTANTS.GRNODE.TITLE_FONT, JCONSTANTS.GRNODE.TITLE_FONT_SIZE
        )
        titleFont.setItalic(True)
        titleFont.setBold(True)

        titleText: QGraphicsTextItem = QGraphicsTextItem(self)
        titleText.setDefaultTextColor(QtCore.Qt.black)
        titleText.setFont(titleFont)
        titleText.setPos(3 * JCONSTANTS.GRNODE.TITLE_PADDING, 0)
        titleText.setTextWidth(
            JCONSTANTS.GRNODE.NODE_WIDHT - 2 * JCONSTANTS.GRNODE.TITLE_PADDING
        )
        titleText.setPlainText(self.nodeTitle)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(
            0, 0, JCONSTANTS.GRNODE.NODE_WIDHT, JCONSTANTS.GRNODE.NODE_HEIGHT
        )

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QStyleOptionGraphicsItem,
        widget: typing.Optional[QWidget],
    ) -> None:

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
            # wk = weakref.ref(socket)()
            # assert wk is not None
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
            # wk = weakref.ref(socket)()
            # assert wk is not None
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

    def Serialize(self) -> JGrNodeModel:
        return JGrNodeModel(
            node=self.baseNode.Serialize(), posX=self.pos().x(), posY=self.pos().y()
        )

    @classmethod
    def Deserialize(cls, grNode: JGrNodeModel) -> JGraphicsNode:
        grNode_ = JGraphicsNode(baseNode=JBaseNode.Deserialize(grNode.node))
        grNode_.setPos(QtCore.QPointF(grNode.posX, grNode.posY))
        return grNode_
