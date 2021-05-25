from jeditor.core.graphicscene import JGraphicScene
from jeditor.core.graphicsocket import JGraphicSocket
from jeditor.core.graphicnode import JGraphicNode
from jeditor.core.graphicedge import JGraphicEdge
import logging
from typing import Dict, Generator, List, Optional, Union

from jeditor.logger import logger
from PyQt5 import QtCore

logger = logging.getLogger(__name__)


class JDataStreamer(QtCore.QDataStream):
    def __init__(self, graphicsScene: JGraphicScene) -> None:
        super().__init__()
        self._graphicsScene = graphicsScene

    def Serialize(self, selected: bool = False) -> Dict:

        node: List[Dict] = []
        edge: List[Dict] = []

        if not selected:
            logger.info("serializing all graphics items")

            if len(self._graphicsScene.items()) == 0:
                logger.warning("empty scene, nothing to serialize")

            else:
                for item in self._graphicsScene.items():
                    if isinstance(item, JGraphicNode):
                        node.append(item.Serialize())
                    if isinstance(item, JGraphicEdge):
                        edge.append(item.Serialize())
        else:
            logger.info("serializing selected graphics items")

            if len(self._graphicsScene.selectedItems()) == 0:
                logger.warning("empty scene, nothing to copy")

            else:
                for item in self._graphicsScene.selectedItems():
                    if isinstance(item, JGraphicNode):
                        node.append(item.Serialize())
                    if isinstance(item, JGraphicEdge):
                        edge.append(item.Serialize())

        return {"nodes": node, "edges": edge}

    def Deserialize(
        self, data: Dict
    ) -> Generator[Union[JGraphicNode, JGraphicEdge], None, None]:

        logger.info("deserializing")

        for node in data["nodes"]:
            instanceNode = JGraphicNode.Deserialize(node)
            yield instanceNode

        for edge in data["edges"]:
            edgeId = edge["edgeId"]
            sourceSocketId = edge["sourceSocketId"]
            destinationSocketId = edge["destinationSocketId"]

            sourceSocket: Optional[JGraphicSocket] = None
            destinationSocket: Optional[JGraphicSocket] = None

            for socket in list(
                filter(
                    lambda socket_: isinstance(socket_, JGraphicSocket),
                    self._graphicsScene.items(),
                )
            ):
                assert isinstance(socket, JGraphicSocket)
                if socket.socketId == sourceSocketId:
                    sourceSocket = socket
                elif socket.socketId == destinationSocketId:
                    destinationSocket = socket

            assert sourceSocket, logger.error("source socket not found")
            assert destinationSocket, logger.error("destination socket not found")

            instanceEdge = JGraphicEdge.Deserialize(
                edgeId, sourceSocket, destinationSocket
            )

            if instanceEdge is None:
                logger.warning(f"unable to deserialize edge {edgeId}")
                continue

            yield instanceEdge
