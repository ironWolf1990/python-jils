from __future__ import annotations
from jigls.jcore.ibase import ISocket
import typing
from jigls.jeditor.base.socketbase import JBaseSocket
import logging
from typing import List, Optional, Union

from jigls.logger import logger
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)

from jigls.jeditor.constants import JCONSTANTS

logger = logging.getLogger(__name__)


class JGraphicsSocket(QGraphicsItem):
    def __init__(self, parent: QGraphicsItem, baseSocket: JBaseSocket, pos: QtCore.QPointF) -> None:
        super().__init__(parent=parent)

        self._baseSocket: JBaseSocket = baseSocket
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

        self._penOutline = QtGui.QPen(QtGui.QColor(JCONSTANTS.GRSOCKET.COLOR_OUTLINE))
        self._penOutline.setWidthF(JCONSTANTS.GRSOCKET.WIDTH_OUTLINE)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget],
    ) -> None:

        painter.setPen(self._penOutline)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(JCONSTANTS.GRSOCKET.COLOR_BACKGROUND)))
        if self.multiConnection():
            painter.drawRect(
                int(-JCONSTANTS.GRSOCKET.RADIUS),
                int(-JCONSTANTS.GRSOCKET.RADIUS),
                int(2 * JCONSTANTS.GRSOCKET.RADIUS),
                int(2 * JCONSTANTS.GRSOCKET.RADIUS),
            )
        else:
            painter.drawEllipse(
                int(-JCONSTANTS.GRSOCKET.RADIUS),
                int(-JCONSTANTS.GRSOCKET.RADIUS),
                int(2 * JCONSTANTS.GRSOCKET.RADIUS),
                int(2 * JCONSTANTS.GRSOCKET.RADIUS),
            )

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(
            int(-JCONSTANTS.GRSOCKET.RADIUS),
            int(-JCONSTANTS.GRSOCKET.RADIUS),
            int(2 * JCONSTANTS.GRSOCKET.RADIUS),
            int(2 * JCONSTANTS.GRSOCKET.RADIUS),
        )

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        return super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        self._penOutline.setColor(QtGui.QColor(JCONSTANTS.GRSOCKET.COLOR_HOVER))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._penOutline.setColor(QtGui.QColor(JCONSTANTS.GRSOCKET.COLOR_OUTLINE))
        super().hoverLeaveEvent(event)

    @staticmethod
    def CalculateSocketPos(index: int, position: int) -> QtCore.QPointF:
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

        return QtCore.QPointF(x, y)
