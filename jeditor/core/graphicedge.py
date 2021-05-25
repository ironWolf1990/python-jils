from __future__ import annotations

import logging
import uuid
from collections import OrderedDict
from typing import TYPE_CHECKING, Optional

from jeditor.logger import logger
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

from .constants import JCONSTANTS
from .graphicedgepath import JGraphicEdgeBezier, JGraphicEdgeDirect, JGraphicEdgeSquare
from .graphicsocket import JGraphicSocket

logger = logging.getLogger(__name__)


class JGraphicEdge(QGraphicsPathItem):
    def __init__(
        self,
        edgeId: str,
        startSocket: "JGraphicSocket",
        destinationSocket: Optional["JGraphicSocket"],
        parent: Optional[QGraphicsPathItem] = None,
        edgePathType: int = JCONSTANTS.GREDGE.PATH_BEZIER,
    ) -> None:
        super().__init__(parent=parent)

        self._edgeId: str = edgeId
        self._startSocket: JGraphicSocket = startSocket
        self._destinationSocket: Optional[JGraphicSocket] = destinationSocket
        self._edgePathType: int = edgePathType
        self._dragPos: QtCore.QPointF = QtCore.QPointF()

        self._startSocket.ConnectEdge(self._edgeId)
        if self._destinationSocket is not None:
            self._destinationSocket.ConnectEdge(self._edgeId)

        self.initUI()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(-1.0)

        self._edgeColor = QtGui.QColor(JCONSTANTS.GREDGE.COLOR_DEFAULT)
        self._edgeColorSelected = QtGui.QColor(JCONSTANTS.GREDGE.COLOR_SELECTED)
        self._edgeColorDrag = QtGui.QColor(JCONSTANTS.GREDGE.COLOR_DRAG)
        self._edgePen = QtGui.QPen(self._edgeColor)
        self._edgePenSelected = QtGui.QPen(self._edgeColorSelected)
        self._edgePenDrag = QtGui.QPen(self._edgeColorDrag)
        self._edgePen.setWidthF(JCONSTANTS.GREDGE.WIDTH)
        self._edgePenSelected.setWidthF(JCONSTANTS.GREDGE.WIDTH)
        self._edgePenDrag.setWidthF(JCONSTANTS.GREDGE.WIDTH)
        self._edgePenDrag.setStyle(QtCore.Qt.DashLine)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget],
    ) -> None:

        painter.setPen(self._edgePenSelected if self.isSelected() else self._edgePen)
        if self.destinationSocket is None:
            painter.setPen(self._edgePenDrag)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(self.path())

        self.UpdatePath()

    @property
    def startSocket(self):
        return self._startSocket

    @property
    def edgeId(self):
        return self._edgeId

    @property
    def destinationSocket(self):
        return self._destinationSocket

    @destinationSocket.setter
    def destinationSocket(self, socket: "JGraphicSocket") -> None:
        assert not socket.AtMaxLimit(), logger.warning(
            f"max edge limit reached for socket {socket.socketId}"
        )
        self._destinationSocket = socket
        self._destinationSocket.ConnectEdge(self._edgeId)
        self._dragPos = QtCore.QPointF()

    @property
    def dragPos(self) -> QtCore.QPointF:
        return self._dragPos

    @dragPos.setter
    def dragPos(self, pos: QtCore.QPointF):
        self._dragPos = pos
        if self._destinationSocket is not None:
            self._destinationSocket.DisconnectEdge(self._edgeId)
            logger.info(
                f"removed edge from destination socket, edge is repositioning {self._edgeId}"
            )
            self._destinationSocket = None

    @property
    def sourcePos(self):
        return self._startSocket.scenePos()

    @property
    def destinationPos(self) -> QtCore.QPointF:
        if self._destinationSocket is not None:
            return self._destinationSocket.scenePos()
        return self._dragPos

    @property
    def endPos(self) -> QtCore.QPointF:
        return self.destinationPos

    @property
    def edgePathType(self) -> int:
        return self._edgePathType

    @edgePathType.setter
    def edgePathType(self, pathType: int) -> None:
        self._edgePathType = pathType
        self.update()

    def DisconnectFromSockets(self):
        if self._startSocket is not None:
            self._startSocket.DisconnectEdge(self._edgeId)
        if self._destinationSocket is not None:
            self._destinationSocket.DisconnectEdge(self._edgeId)

    def ReconnectToSockets(self):
        """to help assist with undostack when re-inserting edge"""
        self._startSocket.ConnectEdge(self._edgeId)
        if self._destinationSocket is not None:
            self._destinationSocket.ConnectEdge(self._edgeId)

    def UpdatePath(self, *args, **kwargs):
        if self.edgePathType == JCONSTANTS.GREDGE.PATH_DIRECT:
            self.setPath(
                JGraphicEdgeDirect.GetPath(self.sourcePos, self.destinationPos)
            )
        elif self.edgePathType == JCONSTANTS.GREDGE.PATH_BEZIER:
            self.setPath(
                JGraphicEdgeBezier.GetPath(self.sourcePos, self.destinationPos)
            )
        elif self.edgePathType == JCONSTANTS.GREDGE.PATH_SQUARE:
            self.setPath(
                JGraphicEdgeSquare.GetPath(self.sourcePos, self.destinationPos)
            )
        else:
            logger.error("unknown edge path type, defaulting direct")
            self.setPath(
                JGraphicEdgeDirect.GetPath(self.sourcePos, self.destinationPos)
            )

    def Serialize(self):
        return OrderedDict(
            [
                ("edgeId", self._edgeId),
                ("sourceSocketId", self.startSocket.socketId),
                ("destinationSocketId", self.destinationSocket.socketId),
            ]
        )

    @classmethod
    def Deserialize(
        cls, edgeId: str, startSocket: JGraphicSocket, destinationSocket: JGraphicSocket
    ) -> Optional[JGraphicEdge]:
        edge: Optional[JGraphicEdge] = None

        if startSocket.AtMaxLimit():
            logger.error("error deserializing edge, start socket at max limit")
            return None
        elif destinationSocket.AtMaxLimit():
            logger.error("error deserializing edge, destination socket at max limit")
            return None

        return JGraphicEdge(
            edgeId=edgeId,
            startSocket=startSocket,
            destinationSocket=destinationSocket,
            edgePathType=JCONSTANTS.GREDGE.PATH_BEZIER,
        )

    @classmethod
    def DragNewEdge(
        cls, startSocket: JGraphicSocket, dragPos: QtCore.QPointF
    ) -> JGraphicEdge:
        edgeId = uuid.uuid4().hex
        instanceEdge = JGraphicEdge(
            edgeId=edgeId,
            startSocket=startSocket,
            destinationSocket=None,
            edgePathType=JCONSTANTS.GREDGE.PATH_BEZIER,
        )
        instanceEdge.dragPos = dragPos
        return instanceEdge
