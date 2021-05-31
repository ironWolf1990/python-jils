from __future__ import annotations
from jigls.jdantic import JEdgeModel

import logging
import uuid
from collections import OrderedDict
from typing import TYPE_CHECKING, Optional

from jigls.constants import JCONSTANTS
from jigls.core.graphicedgepath import (
    JGraphicEdgeBezier,
    JGraphicEdgeDirect,
    JGraphicEdgeSquare,
)
from jigls.logger import logger
from jigls.utils import UniqueIdentifier
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

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

        # gui purpose
        self._startSocket: JGraphicsSocket = startSocket
        self._destnSocket: Optional[JGraphicsSocket] = destnSocket
        self._pathType: int = pathType
        self._dragPos: QtCore.QPointF = QtCore.QPointF()

        self._startSocket.ConnectEdge(self._uid)
        if self._destnSocket is not None:
            self._destnSocket.ConnectEdge(self._uid)

        self.initUI()

    def uid(self):
        return self._uid

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(-1.0)

        # pens for diff mode

        self._edgePen = QtGui.QPen(QtGui.QColor(JCONSTANTS.GREDGE.COLOR_DEFAULT))
        self._edgePen.setWidthF(JCONSTANTS.GREDGE.WIDTH)

        self._edgePenSelected = QtGui.QPen(
            QtGui.QColor(JCONSTANTS.GREDGE.COLOR_SELECTED)
        )
        self._edgePenSelected.setWidthF(JCONSTANTS.GREDGE.WIDTH)

        self._edgePenDrag = QtGui.QPen(QtGui.QColor(JCONSTANTS.GREDGE.COLOR_DRAG))
        self._edgePenDrag.setWidthF(JCONSTANTS.GREDGE.WIDTH)
        self._edgePenDrag.setStyle(QtCore.Qt.DashLine)

    def paint(
        self,
        painter: QtGui.QPainter,
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

        painter.setBrush(QtCore.Qt.NoBrush)
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
        assert not socket.AtMaxLimit(), logger.warning(
            f"max edge limit reached for socket {socket.uid()}"
        )
        self._destnSocket = socket
        self._destnSocket.ConnectEdge(self.uid())
        self._dragPos = QtCore.QPointF()

    @property
    def dragPos(self) -> QtCore.QPointF:
        return self._dragPos

    @dragPos.setter
    def dragPos(self, pos: QtCore.QPointF):
        self._dragPos = pos
        if self._destnSocket is not None:
            self._destnSocket.DisconnectEdge(self.uid())
            logger.info(
                f"removed edge from destination socket, edge is repositioning {self.uid()}"
            )
            self._destnSocket = None

    @property
    def sourcePos(self):
        return self._startSocket.scenePos()

    @property
    def destinationPos(self) -> QtCore.QPointF:
        if self._destnSocket is not None:
            return self._destnSocket.scenePos()
        return self._dragPos

    @property
    def endPos(self) -> QtCore.QPointF:
        return self.destinationPos

    @property
    def pathType(self) -> int:
        return self._pathType

    @pathType.setter
    def pathType(self, pathType: int) -> None:
        self._pathType = pathType
        self.update()

    def DisconnectFromSockets(self):
        if self._startSocket is not None:
            self._startSocket.DisconnectEdge(self.uid())
        if self._destnSocket is not None:
            self._destnSocket.DisconnectEdge(self.uid())

    def ReconnectToSockets(self):
        """to help assist with undostack when re-inserting edge"""
        self._startSocket.ConnectEdge(self.uid())
        if self._destnSocket is not None:
            self._destnSocket.ConnectEdge(self.uid())

    def UpdatePath(self, *args, **kwargs):
        if self.pathType == JCONSTANTS.GREDGE.PATH_DIRECT:
            self.setPath(
                JGraphicEdgeDirect.GetPath(self.sourcePos, self.destinationPos)
            )
        elif self.pathType == JCONSTANTS.GREDGE.PATH_BEZIER:
            self.setPath(
                JGraphicEdgeBezier.GetPath(self.sourcePos, self.destinationPos)
            )
        elif self.pathType == JCONSTANTS.GREDGE.PATH_SQUARE:
            self.setPath(
                JGraphicEdgeSquare.GetPath(self.sourcePos, self.destinationPos)
            )
        else:
            logger.error("unknown edge path type, defaulting direct")
            self.setPath(
                JGraphicEdgeDirect.GetPath(self.sourcePos, self.destinationPos)
            )

    def __repr__(self) -> str:
        return "uid:%s sUid:%s dUid:%s" % (
            self.uid(),
            self.startSocket.uid(),
            self.destnSocket.uid() if self.destnSocket is not None else None,
        )

    def Serialize(self):
        return JEdgeModel(
            uid=self.uid(),
            startSocket=self.startSocket.uid(),
            destnSocket=self.destnSocket.uid(),
        )

    @classmethod
    def Deserialize(
        cls,
        uid: str,
        startSocket: JGraphicsSocket,
        destnSocket: JGraphicsSocket,
    ) -> Optional[JGraphicsEdge]:

        if startSocket.AtMaxLimit():
            logger.error("error deserializing edge, start socket at max limit")
            return None
        elif destnSocket.AtMaxLimit():
            logger.error("error deserializing edge, destination socket at max limit")
            return None

        return JGraphicsEdge(
            uid=uid,
            startSocket=startSocket,
            destnSocket=destnSocket,
            pathType=JCONSTANTS.GREDGE.PATH_BEZIER,
        )

    @classmethod
    def DragNewEdge(
        cls, startSocket: JGraphicsSocket, dragPos: QtCore.QPointF
    ) -> JGraphicsEdge:
        edgeId = uuid.uuid4().hex
        instanceEdge = JGraphicsEdge(
            uid=edgeId,
            startSocket=startSocket,
            destnSocket=None,
            pathType=JCONSTANTS.GREDGE.PATH_BEZIER,
        )
        instanceEdge.dragPos = dragPos
        return instanceEdge
