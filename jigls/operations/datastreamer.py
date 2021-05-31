from jigls.jdantic import JEdgeModel, JGrNodeModel, JModel
from jigls.base.nodebase import JBaseNode
from jigls.core.graphicscene import JGraphicScene
from jigls.ui.graphicsocket import JGraphicsSocket
from jigls.ui.graphicnode import JGraphicsNode
from jigls.ui.graphicedge import JGraphicsEdge
import logging
from typing import Dict, Generator, List, Optional, Union

from jigls.logger import logger
from PyQt5 import QtCore

logger = logging.getLogger(__name__)


class JDataStreamer(QtCore.QDataStream):
    def __init__(self, graphicsScene: JGraphicScene) -> None:
        super().__init__()
        self._graphicsScene = graphicsScene

    def Serialize(self, selected: bool = False) -> JModel:

        nodes: List[JGrNodeModel] = []
        edges: List[JEdgeModel] = []

        if not selected:
            logger.info("serializing all graphics items")

            if len(self._graphicsScene.items()) == 0:
                logger.warning("empty scene, nothing to serialize")

            else:
                for item in self._graphicsScene.items():
                    if isinstance(item, JGraphicsNode):
                        nodes.append(item.Serialize())
                    if isinstance(item, JGraphicsEdge):
                        edges.append(item.Serialize())
        else:
            logger.info("serializing selected graphics items")

            if len(self._graphicsScene.selectedItems()) == 0:
                logger.warning("empty scene, nothing to copy")

            else:
                for item in self._graphicsScene.selectedItems():
                    if isinstance(item, JGraphicsNode):
                        nodes.append(item.Serialize())
                    if isinstance(item, JGraphicsEdge):
                        edges.append(item.Serialize())

        return JModel(nodes=nodes, edges=edges)

    def Deserialize(
        self, data: JModel
    ) -> Generator[Union[JGraphicsNode, JGraphicsEdge], None, None]:

        logger.info("deserializing")

        for node in data.nodes:
            assert node
            yield JGraphicsNode.Deserialize(node)

        for edge in data.edges:

            startSocket: Optional[JGraphicsSocket] = None
            destnSocket: Optional[JGraphicsSocket] = None

            for socket in list(
                filter(
                    lambda socket_: isinstance(socket_, JGraphicsSocket),
                    self._graphicsScene.items(),
                )
            ):
                assert isinstance(socket, JGraphicsSocket)
                if socket.uid() == edge.startSocket.hex:
                    startSocket = socket
                elif socket.uid() == edge.destnSocket.hex:
                    destnSocket = socket

            if startSocket is None:
                logger.error(
                    f"for E:{edge.uid} startSocket:{edge.startSocket} not found"
                )
                continue
            if destnSocket is None:
                logger.error(
                    f"for E:{edge.uid} startSocket:{edge.destnSocket} not found"
                )
                continue

            instanceEdge = JGraphicsEdge.Deserialize(
                uid=edge.uid.hex, startSocket=startSocket, destnSocket=destnSocket
            )
            if instanceEdge is None:
                logger.warning(f"unable to deserialize edge {edge.uid}")
                continue
            yield instanceEdge
