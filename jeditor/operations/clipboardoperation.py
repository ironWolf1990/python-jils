from jeditor.constants import JCONSTANTS
from jeditor.core.utils import UniqueIdentifier
import json
import logging
import typing
from typing import Dict, List, Optional, Set, Tuple

from jeditor.logger import logger
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, QPointF

logger = logging.getLogger(__name__)
from pprint import pprint


class JClipboard(QObject):
    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._copiedData: Optional[Dict] = None
        self._mode: Optional[int] = None

    def Cut(self, data: Dict):
        self._copiedData = None
        self._copiedData = data
        self._mode = JCONSTANTS.CLIPBOARD.MODE_CUT

    def Copy(self, data: Dict):
        self._copiedData = None
        self._copiedData = data
        self._mode = JCONSTANTS.CLIPBOARD.MODE_COPY

    def Paste(self, mousePosition: QPointF):

        if self._copiedData is None or not self._copiedData:
            logger.warning("copied data is empty")
            return dict()

        if self._mode == JCONSTANTS.CLIPBOARD.MODE_CUT:
            return self._copiedData

        minX, minY, maxX, maxY = 0, 0, 0, 0
        newSocketIds: Dict[str, str] = {}

        for node in self._copiedData["nodes"]:

            # * assign new node id
            oId = node["nodeId"]
            node["nodeId"] = UniqueIdentifier()

            # * calculate centre position to paste
            x = node["posX"]
            y = node["posY"]
            if x < minX:
                minX = x
            elif x > maxX:
                maxX = x
            if y < minY:
                minY = y
            elif y > maxY:
                maxY = y

            # * assign socket id, keep old to replace in edges
            for _, socketInfo in node["socketInfo"].items():
                oSocketId = socketInfo["socketId"]
                nSocketID = UniqueIdentifier()
                socketInfo["socketId"] = nSocketID
                newSocketIds.update({oSocketId: nSocketID})

        offsetX = mousePosition.x() - (minX + maxX) / 2
        offsetY = mousePosition.y() - (minY + maxY) / 2

        for node in self._copiedData["nodes"]:
            node["posX"] += offsetX
            node["posY"] += offsetY

        for edge in self._copiedData["edges"]:

            # * new edge id
            edge["edgeId"] = UniqueIdentifier()

            # * replace old socket ids
            ssId = newSocketIds.get(edge["sourceSocketId"], None)
            if ssId:
                edge["sourceSocketId"] = ssId
            else:
                logger.warning("open connection for source node socket")
            #     self._copiedData["edges"].remove(edge)
            #     continue

            dsId = newSocketIds.get(edge["destinationSocketId"], None)
            if dsId:
                edge["destinationSocketId"] = dsId
            else:
                logger.warning("open connection for destination node socket")
            #     self._copiedData["edges"].remove(edge)
            #     continue

        return self._copiedData
