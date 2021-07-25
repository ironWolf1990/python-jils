from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Optional

from jigls.jeditor.constants import JCONSTANTS
from jigls.jeditor.core.graphicedgepath import JGraphicEdgeBezier, JGraphicEdgeDirect, JGraphicEdgeSquare
from jigls.jeditor.jdantic import JGrEdgeModel
from jigls.jeditor.utils import UniqueIdentifier

from jigls.logger import logger
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget

from .graphicsocket import JGraphicsSocket

logger = logging.getLogger(__name__)


class JGraphicsEdge(QGraphicsPathItem):
    def __init__(
        self,
        startSocket: JGraphicsSocket,
        destnSocket: Optional[JGraphicsSocket] = None,
        uid: Optional[str] = None,
        parent: Optional[QGraphicsPathItem] = None,
        pathType: int = JCONSTANTS.GREDGE.PATH_BEZIER,
    ) -> None:
        super().__init__(parent=parent)

        self._uid = UniqueIdentifier() if uid is None else uid

        self._startSocket: JGraphicsSocket = startSocket
        self._destnSocket: Optional[JGraphicsSocket] = destnSocket
        self._pathType: int = pathType
        self._dragPos: QPointF = QPointF()

        self.initUI()

    def uid(self):
        return self._uid

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(0)

        # ! setting any chachemode breaks edge. not updating edge when socket is moved
        # self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # ? pens for diff mode
        self._edgePen = QPen(QColor(JCONSTANTS.GREDGE.COLOR_DEFAULT))
        self._edgePen.setWidthF(JCONSTANTS.GREDGE.WIDTH)

        self._edgePenSelected = QPen(QColor(JCONSTANTS.GREDGE.COLOR_SELECTED))
        self._edgePenSelected.setWidthF(JCONSTANTS.GREDGE.WIDTH)

        self._edgePenDrag = QPen(QColor(JCONSTANTS.GREDGE.COLOR_DRAG))
        self._edgePenDrag.setWidthF(JCONSTANTS.GREDGE.WIDTH)
        self._edgePenDrag.setStyle(Qt.DashLine)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget],
    ) -> None:

        painter.setPen(
            self._edgePenDrag
            if self.destnSocket is None
            else self._edgePenSelected
            if self.isSelected()
            else self._edgePen
        )

        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

        self.UpdatePath()

    @property
    def startSocket(self):
        return self._startSocket

    @property
    def destnSocket(self):
        return self._destnSocket

    @destnSocket.setter
    def destnSocket(self, socket: JGraphicsSocket) -> None:
        if socket.AtMaxLimit():
            logger.warning(f"max edge limit reached for socket {socket.uid()}")
            raise UserWarning
        self._destnSocket = socket
        self._dragPos = QPointF()

    @property
    def dragPos(self) -> QPointF:
        return self._dragPos

    @dragPos.setter
    def dragPos(self, pos: QPointF):
        self._dragPos = pos
        if self._destnSocket is not None:
            logger.info(f"removed edge from destination socket, edge is repositioning {self.uid()}")
            self._destnSocket = None

    @property
    def sourcePos(self):
        return self._startSocket.scenePos()

    @property
    def destinationPos(self) -> QPointF:
        if self._destnSocket is not None:
            return self._destnSocket.scenePos()
        return self._dragPos

    @property
    def endPos(self) -> QPointF:
        return self.destinationPos

    @property
    def pathType(self) -> int:
        return self._pathType

    @pathType.setter
    def pathType(self, pathType: int) -> None:
        self._pathType = pathType
        self.update()

    def DisconnectFromSockets(self):
        assert self._destnSocket is not None
        assert self._startSocket is not None
        self._destnSocket.Disconnect(self._startSocket.baseSocket)
        self._startSocket.Disconnect(self._destnSocket.baseSocket)

    def ConnectToSockets(self):
        """to help assist with undostack when re-inserting edge"""
        self.DisconnectFromSockets()
        self._destnSocket.Connect(self._startSocket.baseSocket)  # type:ignore
        self._startSocket.Connect(self._destnSocket.baseSocket)  # type:ignore

    def UpdatePath(self, *args, **kwargs):
        if self.pathType == JCONSTANTS.GREDGE.PATH_DIRECT:
            self.setPath(JGraphicEdgeDirect.GetPath(self.sourcePos, self.destinationPos))
        elif self.pathType == JCONSTANTS.GREDGE.PATH_BEZIER:
            self.setPath(JGraphicEdgeBezier.GetPath(self.sourcePos, self.destinationPos))
        elif self.pathType == JCONSTANTS.GREDGE.PATH_SQUARE:
            self.setPath(JGraphicEdgeSquare.GetPath(self.sourcePos, self.destinationPos))
        else:
            logger.error("unknown edge path type, defaulting direct")
            self.setPath(JGraphicEdgeDirect.GetPath(self.sourcePos, self.destinationPos))

    def __repr__(self) -> str:
        return "uid:%s sUid:%s dUid:%s" % (
            self.uid(),
            self.startSocket.uid(),
            self.destnSocket.uid() if self.destnSocket is not None else None,
        )

    def Serialize(self):
        assert self.destnSocket is not None
        assert self.startSocket is not None
        return JGrEdgeModel(
            uid=self.uid(),
            startSocket=self.startSocket.uid(),
            destnSocket=self.destnSocket.uid(),
            pathType=self.pathType,
        )

    @classmethod
    def Deserialize(
        cls,
        uid: str,
        startSocket: JGraphicsSocket,
        destnSocket: JGraphicsSocket,
        pathType=JCONSTANTS.GREDGE.PATH_BEZIER,
    ) -> Optional[JGraphicsEdge]:

        if startSocket.AtMaxLimit():
            logger.error("error deserializing edge, start socket at max limit")
            return None
        elif destnSocket.AtMaxLimit():
            logger.error("error deserializing edge, destination socket at max limit")
            return None

        edge = JGraphicsEdge(uid=uid, startSocket=startSocket, destnSocket=destnSocket, pathType=pathType)

        edge.ConnectToSockets()
        return edge

    @classmethod
    def DragNewEdge(cls, startSocket: JGraphicsSocket, dragPos: QPointF) -> JGraphicsEdge:
        edgeId = uuid.uuid4().hex
        instanceEdge = JGraphicsEdge(
            uid=edgeId, startSocket=startSocket, destnSocket=None, pathType=JCONSTANTS.GREDGE.PATH_BEZIER
        )
        instanceEdge.dragPos = dragPos
        return instanceEdge
