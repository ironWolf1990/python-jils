from __future__ import annotations

import logging
import typing
from typing import Optional

from jigls.jeditor.base.socketbase import JBaseSocket
from jigls.jeditor.constants import JCONSTANTS

from jigls.logger import logger
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QWidget

logger = logging.getLogger(__name__)


class JGraphicsSocket(QGraphicsItem):
    def __init__(self, parent: QGraphicsItem, baseSocket: JBaseSocket, pos: QPointF) -> None:
        super().__init__(parent=parent)

        self._baseSocket: JBaseSocket = baseSocket

        self._boundingBox: Optional[QRectF] = None
        self._outline: Optional[QRectF] = None

        self.initUI()
        self.setPos(pos)

    @property
    def baseSocket(self):
        return self._baseSocket

    def name(self):
        return self.baseSocket.name

    def uid(self):
        return self.baseSocket.uid

    def nodeId(self):
        return self.baseSocket.nodeId

    def socketType(self) -> int:
        return self.baseSocket.Type

    def multiConnection(self):
        return self.baseSocket.multiConnect

    def Connect(self, dSocket: JBaseSocket):
        return self.baseSocket.Connect(dSocket)

    def Disconnect(self, dSocket: JBaseSocket):
        return self.baseSocket.Disconnect(dSocket)

    def ConnectionList(self) -> typing.Set[JBaseSocket]:
        return self.baseSocket.connections  # type:ignore

    def HasEdge(self, socket: JBaseSocket) -> bool:
        return self.baseSocket.HasConnection(socket)

    def EdgeCount(self) -> int:
        return len(self.baseSocket.connections)

    def AtMaxLimit(self) -> bool:
        return self.baseSocket.AtMaxLimit()

    def __repr__(self) -> str:
        return self.baseSocket.__repr__()

    def initUI(self):
        self.setZValue(2)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)

        # ! high cpu usage bug fix sollution
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.penOutline = QPen(QColor(JCONSTANTS.GRSOCKET.COLOR_OUTLINE))
        self.penOutline.setWidthF(JCONSTANTS.GRSOCKET.WIDTH_OUTLINE)

    def boundingRect(self) -> QRectF:
        if self._boundingBox == None:
            self._boundingBox = QRectF(
                int(-JCONSTANTS.GRSOCKET.RADIUS),
                int(-JCONSTANTS.GRSOCKET.RADIUS),
                int(2 * JCONSTANTS.GRSOCKET.RADIUS),
                int(2 * JCONSTANTS.GRSOCKET.RADIUS),
            )
            return self._boundingBox
        return self._boundingBox

    def OutlinePath(self):
        if self._outline is None:
            self._outline = QRectF(
                int(-JCONSTANTS.GRSOCKET.RADIUS),
                int(-JCONSTANTS.GRSOCKET.RADIUS),
                int(2 * JCONSTANTS.GRSOCKET.RADIUS),
                int(2 * JCONSTANTS.GRSOCKET.RADIUS),
            )
            return self._outline
        return self._outline

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget],
    ) -> None:

        painter.setPen(self.penOutline)
        painter.setBrush(QBrush(QColor(JCONSTANTS.GRSOCKET.COLOR_BACKGROUND)))
        if self.multiConnection():
            painter.drawRect(self.OutlinePath())
        else:
            painter.drawEllipse(self.OutlinePath())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        return super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        self.penOutline.setColor(QColor(JCONSTANTS.GRSOCKET.COLOR_HOVER))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.penOutline.setColor(QColor(JCONSTANTS.GRSOCKET.COLOR_OUTLINE))
        super().hoverLeaveEvent(event)

    @staticmethod
    def CalculateSocketPos(index: int, position: int) -> QPointF:
        # * left posiition
        x = 0

        # * right posiition
        if position in [
            JCONSTANTS.GRSOCKET.POS_RIGHT_BOTTOM,
            JCONSTANTS.GRSOCKET.POS_RIGHT_TOP,
        ]:
            x = JCONSTANTS.GRNODE.NODE_WIDHT

        # * top position
        vertPadding = (
            JCONSTANTS.GRNODE.TITLE_HEIGHT + JCONSTANTS.GRNODE.TITLE_PADDING + JCONSTANTS.GRNODE.NODE_PADDING
        )
        y = vertPadding + index * JCONSTANTS.GRSOCKET.SPACING

        # * bottom position
        if position in [
            JCONSTANTS.GRSOCKET.POS_LEFT_BOTTOM,
            JCONSTANTS.GRSOCKET.POS_RIGHT_BOTTOM,
        ]:
            y = JCONSTANTS.GRNODE.NODE_HEIGHT - vertPadding - index * JCONSTANTS.GRSOCKET.SPACING

        return QPointF(x, y)
