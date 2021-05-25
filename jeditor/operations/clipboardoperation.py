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

    def Copy(self, data: Dict):
        self._copiedData = None
        self._copiedData = data

    def Paste(self, mousePosition: QPointF):
        assert self._copiedData is not None
        """
        "nodes": [
        {
            "nodeId": "8615ece5edcb40149606f2708437f281",
            "posX": 59.0,
            "posY": -365.0,
            "socketCount": 2,
            "socketInfo": {
                "0": {
                    "socketId": "0dd2b8f7ecce43deaeb0c0113e2c5e38",
                    "socketType": 1,
                    "multiConnection": true
                },
                "1": {
                    "socketId": "5298a8036413464d90d77a68c2256e52",
                    "socketType": 2,
                    "multiConnection": false
                }
            }
        },
        "edges": [
        {
            "edgeId": "b7fa01af6c544e289352fda247a14484",
            "sourceSocketId": "7952bac66b394edd981c221a3555c06a",
            "destinationSocketId": "0dd2b8f7ecce43deaeb0c0113e2c5e38"
        },
        """
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

    def Cut(self, data: Dict):
        pass