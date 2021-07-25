from __future__ import annotations

import json
import logging
import typing
from typing import Any, List, Optional, Set

from jigls.jcore.ibase import ISocket
from jigls.jeditor.base.nodebase import JBaseNode
from jigls.jeditor.base.socketbase import JBaseSocket
from jigls.jeditor.constants import JCONSTANTS
from jigls.jeditor.jdantic import JGrNodeModel
from jigls.jeditor.popup.nodeproperty import JNodeProperty
from jigls.jeditor.ui.graphicsocket import JGraphicsSocket
from jigls.jeditor.widgets import datacontent
from jigls.jeditor.widgets.datacontent import DataContent
from jigls.logger import logger
from PyQt5.QtCore import QObject, QPointF, QRectF, Qt, QThread
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QGraphicsTextItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

logger = logging.getLogger(__name__)


# class NodePropertyT(QThread):
#     def __init__(self, parent: Optional[QObject] = None):
#         super().__init__(parent=parent)

#     def run(self):
#         self.nodeProperty = JNodeProperty()
#         self.nodeProperty.signalCancel.connect(self.CancelNodeProperty)  # type:ignore
#         self.nodeProperty.signalOk.connect(self.OkNodeProperty)  # type:ignore
#         self.nodeProperty.exec_()

#     def OkNodeProperty(self, a0: bool):
#         logger.info(f"OkNodeProperty {a0}")
#         self.quit()

#     def CancelNodeProperty(self, a0: bool):
#         logger.info(f"CancelNodeProperty {a0}")


class JGraphicsNode(QGraphicsItem):

    __TYPE__: str = "BaseNode"

    def __init__(self, baseNode: JBaseNode, parent: Optional[QGraphicsItem] = None) -> None:

        super().__init__(parent=parent)

        self._baseNode: JBaseNode = baseNode

        self._graphicsSocketList: List[JGraphicsSocket] = []
        self._doubleClicked: bool = False

        self._boundingBox: Optional[QRectF] = None
        self._titlePath: Optional[QPainterPath] = None
        self._contentPath: Optional[QPainterPath] = None
        self._outline: Optional[QPainterPath] = None

        self._triggerUpdate: bool = True

        self._nodeProperty = JNodeProperty()

        self._titleBrush = QBrush()

        self.initUI()
        self.initSocketUI()

        # todo wire signals properly
        self._nodeProperty.infoTab.signalNameChange.connect(self._NodeNameChangeSignal)  # type:ignore

    @property
    def name(self) -> str:
        return self.GetNodeName()

    @name.setter
    def name(self, value: str) -> None:
        self.SetNodeName(value)

    @property
    def baseNode(self) -> JBaseNode:
        return self._baseNode

    @property
    def nodeType(self):
        return self.__TYPE__

    @property
    def nodeProperty(self) -> JNodeProperty:
        return self._nodeProperty

    @property
    def dataContent(self) -> DataContent:
        return self._nodeProperty.dataContent

    @property
    def graphicsSocketList(self) -> List[JGraphicsSocket]:
        return self._graphicsSocketList

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

    def SetTitleColor(self, color: str):
        self._titleBrush = QBrush(QColor(color))

    def initUI(self):
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # ! high cpu usage bug fix sollution
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # * title
        titleFont: QFont = QFont(JCONSTANTS.GRNODE.TITLE_FONT, JCONSTANTS.GRNODE.TITLE_FONT_SIZE)
        titleFont.setItalic(True)
        titleFont.setBold(True)

        self._titleBrush = QBrush(QColor(JCONSTANTS.GRNODE.COLOR_TITLE_DEFAULT))

        self._titleText: QGraphicsTextItem = QGraphicsTextItem(self)
        self._titleText.setDefaultTextColor(Qt.black)
        self._titleText.setFont(titleFont)
        self._titleText.setPos(3 * JCONSTANTS.GRNODE.TITLE_PADDING, 0)
        self._titleText.setTextWidth(JCONSTANTS.GRNODE.NODE_WIDHT - 2 * JCONSTANTS.GRNODE.TITLE_PADDING)
        self._titleText.setPlainText(self.name)

    def boundingRect(self) -> QRectF:
        if self._boundingBox == None:
            self._boundingBox = QRectF(0, 0, JCONSTANTS.GRNODE.NODE_WIDHT, JCONSTANTS.GRNODE.NODE_HEIGHT)
            return self._boundingBox
        return self._boundingBox

    def TitlePath(self) -> QPainterPath:
        if self._titlePath is None:
            self._titlePath = QPainterPath()
            self._titlePath.setFillRule(Qt.WindingFill)
            self._titlePath.addRoundedRect(
                0,
                0,
                JCONSTANTS.GRNODE.NODE_WIDHT,
                JCONSTANTS.GRNODE.TITLE_HEIGHT,
                JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
            )
            self._titlePath.addRect(
                0,
                JCONSTANTS.GRNODE.TITLE_HEIGHT - JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
            )
            self._titlePath.addRect(
                JCONSTANTS.GRNODE.NODE_WIDHT - JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.TITLE_HEIGHT - JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
            )
            return self._titlePath

        # ? print position of node as title
        # self._titleText.setPlainText(f"X:{self.pos().x()} Y: {self.pos().y()}")
        return self._titlePath

    def ContentPath(self):
        if self._contentPath is None:
            self._contentPath = QPainterPath()
            self._contentPath.setFillRule(Qt.WindingFill)
            self._contentPath.addRoundedRect(
                0,
                JCONSTANTS.GRNODE.TITLE_HEIGHT,
                JCONSTANTS.GRNODE.NODE_WIDHT,
                JCONSTANTS.GRNODE.NODE_HEIGHT - JCONSTANTS.GRNODE.TITLE_HEIGHT,
                JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
            )
            self._contentPath.addRect(
                0,
                JCONSTANTS.GRNODE.TITLE_HEIGHT,
                JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
            )
            self._contentPath.addRect(
                JCONSTANTS.GRNODE.NODE_WIDHT - JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.TITLE_HEIGHT,
                JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
            )
            return self._contentPath
        return self._contentPath

    def OutlinePath(self):
        if self._outline is None:
            self._outline = QPainterPath()
            self._outline.addRoundedRect(
                0,
                0,
                JCONSTANTS.GRNODE.NODE_WIDHT,
                JCONSTANTS.GRNODE.NODE_HEIGHT,
                JCONSTANTS.GRNODE.NODE_PADDING,
                JCONSTANTS.GRNODE.NODE_PADDING,
            )
            return self._outline
        return self._outline

    # def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
    #     if change == QGraphicsItem.ItemSelectedHasChanged and self._doubleClicked:
    #         logger.debug("node de-double selected")
    #         self._doubleClicked = False
    #     return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        # self._doubleClicked = True
        # logger.debug("peropert")

        # self.npt = NodePropertyT()
        # self.npt.start()
        # self.npt.wait()
        # logger.debug("thread end")
        # self.update()
        self._nodeProperty.show()
        return super().mouseDoubleClickEvent(event)

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget]
    ) -> None:

        # * init graphic socket
        if not self._graphicsSocketList:
            self.initSocketUI()

        # * title
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._titleBrush)
        painter.drawPath(self.TitlePath().simplified())

        # * content
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(JCONSTANTS.GRNODE.COLOR_BACKGROUND)))
        painter.drawPath(self.ContentPath().simplified())

        # * outline
        painter.setPen(
            QPen(QColor(JCONSTANTS.GRNODE.COLOR_OUTLINE_DEFAULT))
            if not self.isSelected()
            else QPen(QColor(JCONSTANTS.GRNODE.COLOR_OUTLINE_SELECTED))
        )
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.OutlinePath().simplified())

    def initSocketUI(self):
        for idx, socket in enumerate(self.GetInSocketList()):
            self._graphicsSocketList.append(
                JGraphicsSocket(
                    parent=self,
                    baseSocket=socket,
                    pos=JGraphicsSocket.CalculateSocketPos(
                        index=idx, position=JCONSTANTS.GRSOCKET.POS_LEFT_TOP
                    ),
                )
            )
        for idx, socket in enumerate(self.GetOutSocketList()):
            self._graphicsSocketList.append(
                JGraphicsSocket(
                    parent=self,
                    baseSocket=socket,
                    pos=JGraphicsSocket.CalculateSocketPos(
                        index=idx, position=JCONSTANTS.GRSOCKET.POS_RIGHT_BOTTOM
                    ),
                )
            )

    def _NodeNameChangeSignal(self, a0: str):
        self.name = a0
        self._titleText.setPlainText(a0)

    def __repr__(self) -> str:
        return f"{self.baseNode.__repr__()} nodeType:{self.nodeType}"

    def Serialize(self):
        return JGrNodeModel(
            node=self.baseNode.Serialize(),
            nodeType=self.nodeType,
            posX=self.pos().x(),
            posY=self.pos().y(),
            dataContent=self._nodeProperty.Serialize(),
        )

    @classmethod
    def Deserialize(cls, grNode: JGrNodeModel):
        logger.debug(f"deserializing {cls.__name__}")
        grNode_ = cls(baseNode=JBaseNode.Deserialize(grNode.node))
        grNode_.setPos(QPointF(grNode.posX, grNode.posY))
        grNode_.nodeProperty.Deserialize(grNode.dataContent)
        return grNode_
