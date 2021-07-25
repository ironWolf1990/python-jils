from jigls.jeditor.jdantic import JGrEdgeModel, JGrNodeModel, JModel
from jigls.jeditor.base.nodebase import JBaseNode
from jigls.jeditor.core.graphicscene import JGraphicScene
from jigls.jeditor.ui.graphicsocket import JGraphicsSocket
from jigls.jeditor.ui.graphicnode import JGraphicsNode
from jigls.jeditor.ui.graphicedge import JGraphicsEdge
import logging
from typing import Dict, Generator, List, Optional, Union

from jigls.logger import logger
from PyQt5 import QtCore

logger = logging.getLogger(__name__)


class JModelStreamer(QtCore.QDataStream):
    def __init__(self, graphicsScene: JGraphicScene) -> None:
        super().__init__()
        self._nodeRegistry: Dict[str, object] = {}
        self._graphicsScene = graphicsScene

    @property
    def nodeRegistry(self) -> Dict[str, object]:
        return self._nodeRegistry

    @property
    def registeredNodeNames(self) -> List[str]:
        return list(self._nodeRegistry.keys())

    def GetNodeObject(self, nodeTypeName: str) -> object:
        if nodeTypeName in self._nodeRegistry:
            return self._nodeRegistry[nodeTypeName]
        logger.critical(f"node of type {nodeTypeName} is not registered")

    def RegisterNode(self, name: str, node: object):
        if name is self._nodeRegistry:
            logger.warning("node with name already registered")
            return
        self._nodeRegistry[name] = node

    def RegisterNodes(self, nodeDict: Dict[str, object]):
        for k, v in nodeDict.items():
            self.RegisterNode(k, v)

    def Serialize(self, selected: bool = False) -> JModel:

        nodes: List[JGrNodeModel] = []
        edges: List[JGrEdgeModel] = []

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
            selectedItems = self._graphicsScene.selectedItems()

            if len(selectedItems) == 0:
                logger.warning("empty scene, nothing to copy")

            else:
                for item in selectedItems:
                    if isinstance(item, JGraphicsNode):
                        nodes.append(item.Serialize())
                    if isinstance(item, JGraphicsEdge):
                        edges.append(item.Serialize())

        return JModel(nodes=nodes, edges=edges)

    def Deserialize(self, data: JModel) -> Generator[Union[JGraphicsNode, JGraphicsEdge], None, None]:

        logger.info("deserializing")

        for node in data.nodes:
            assert node
            nodeObj = self.GetNodeObject(node.nodeType)
            if nodeObj:
                yield nodeObj.Deserialize(node)  # type:ignore
            else:
                logger.error(f"node type {node.nodeType} not found node registry")
                return None

        for edge in data.edges:
            assert edge is not None

            startSocket: Optional[JGraphicsSocket] = None
            destnSocket: Optional[JGraphicsSocket] = None

            for socket in list(
                filter(
                    lambda socket_: isinstance(socket_, JGraphicsSocket),
                    self._graphicsScene.items(),
                )
            ):
                assert isinstance(socket, JGraphicsSocket)
                if socket.uid() == edge.startSocket:
                    startSocket = socket
                elif socket.uid() == edge.destnSocket:
                    destnSocket = socket

            if startSocket is None:
                logger.error(f"for E:{edge.uid} startSocket:{edge.startSocket} not found")
                continue
            if destnSocket is None:
                logger.error(f"for E:{edge.uid} startSocket:{edge.destnSocket} not found")
                continue

            instanceEdge = JGraphicsEdge.Deserialize(
                uid=edge.uid, startSocket=startSocket, destnSocket=destnSocket, pathType=edge.pathType
            )
            if instanceEdge is None:
                logger.error(f"unable to deserialize edge {edge.uid}")
                continue

            yield instanceEdge
