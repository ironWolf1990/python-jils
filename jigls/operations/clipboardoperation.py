from uuid import UUID
from jigls.jdantic import JModel
from jigls.constants import JCONSTANTS
from jigls.utils import UniqueIdentifier
import logging
import typing
from typing import Dict, Optional

from jigls.logger import logger
from PyQt5.QtCore import QObject, QPointF

logger = logging.getLogger(__name__)
from pprint import pprint


class JClipboard(QObject):
    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._copiedData: Optional[JModel] = None
        self._mode: Optional[int] = None

    def Cut(self, data: JModel):
        self._copiedData = None
        self._copiedData = data
        self._mode = JCONSTANTS.CLIPBOARD.MODE_CUT

    def Copy(self, data: JModel):
        self._copiedData = None
        self._copiedData = data
        self._mode = JCONSTANTS.CLIPBOARD.MODE_COPY

    def Paste(self, mousePosition: QPointF) -> Optional[JModel]:

        if self._copiedData is None or not self._copiedData:
            logger.warning("copied data is empty")
            return None

        if self._mode == JCONSTANTS.CLIPBOARD.MODE_CUT:
            return self._copiedData

        minX, minY, maxX, maxY = 0, 0, 0, 0
        newSocketIds: Dict[UUID, UUID] = {}

        for grNode in self._copiedData.nodes:

            # * assign new node id
            oId = grNode.node.uid.hex
            grNode.node.uid = UUID(UniqueIdentifier())

            # * calculate centre position to paste
            x = grNode.posX
            y = grNode.posY
            if x < minX:
                minX = x
            elif x > maxX:
                maxX = x
            if y < minY:
                minY = y
            elif y > maxY:
                maxY = y

            # * assign socket id, keep old to replace in edges
            for socket in grNode.node.socketList:
                oSocketId = socket.uid
                nSocketID = UUID(UniqueIdentifier())
                socket.uid = nSocketID
                newSocketIds.update({oSocketId: nSocketID})

        offsetX = mousePosition.x() - (minX + maxX) / 2
        offsetY = mousePosition.y() - (minY + maxY) / 2

        for grNode in self._copiedData.nodes:
            grNode.posX += offsetX
            grNode.posX += offsetY

        for edge in self._copiedData.edges:

            # * new edge id
            edge.uid = UUID(UniqueIdentifier())

            # * replace old socket ids
            ssId = newSocketIds.get(edge.startSocket, None)
            if ssId:
                edge.startSocket = ssId
            else:
                logger.warning("open connection for source node socket")
            #     self._copiedData["edges"].remove(edge)
            #     continue

            dsId = newSocketIds.get(edge.destnSocket, None)
            if dsId:
                edge.destnSocket = dsId
            else:
                logger.warning("open connection for destination node socket")
            #     self._copiedData["edges"].remove(edge)
            #     continue

        return self._copiedData
