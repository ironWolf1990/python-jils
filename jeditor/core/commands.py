import logging

from jeditor.core.graphicedge import JGraphicEdge
from jeditor.core.graphicnode import JGraphicNode
from jeditor.core.graphicsocket import JGraphicSocket
from jeditor.logger import logger
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGraphicsScene

logger = logging.getLogger(__name__)


class JNodeAddCommand(QtWidgets.QUndoCommand):
    def __init__(self, graphicScene: QGraphicsScene, node: JGraphicNode) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._node: JGraphicNode = node
        self.setText(f"add node {self._node.nodeId}")

    def undo(self) -> None:
        logger.debug("NodeAddCommand")
        self._graphicScene.removeItem(self._node)

    def redo(self) -> None:
        logger.debug("NodeAddCommand")
        self._graphicScene.addItem(self._node)


class JNodeRemoveCommand(QtWidgets.QUndoCommand):
    def __init__(self, graphicScene: QGraphicsScene, node: JGraphicNode) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._node: JGraphicNode = node
        self.setText(f"remove node {self._node.nodeId}")

    def undo(self) -> None:
        logger.debug("NodeRemoveCommand")
        self._graphicScene.addItem(self._node)

    def redo(self) -> None:
        logger.debug("NodeRemoveCommand")
        self._graphicScene.removeItem(self._node)


class JNodeMoveCommand(QtWidgets.QUndoCommand):
    ...
    # def __init__(self, graphicScene: QGraphicsScene, node: JGraphicNode) -> None:
    #     super().__init__()
    #     self._graphicScene: QGraphicsScene = graphicScene
    #     self._node: JGraphicNode = node
    #     self.setText(f"delete node {self._node.nodeId}")

    # def undo(self) -> None:
    #     self._graphicScene.addItem(self._node)

    # def redo(self) -> None:
    #     self._graphicScene.removeItem(self._node)


class JEdgeAddCommand(QtWidgets.QUndoCommand):
    def __init__(
        self,
        graphicScene: QGraphicsScene,
        edge: JGraphicEdge,
    ) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._edge: JGraphicEdge = edge
        self._startSocket = edge.startSocket
        self.setText(f"add edge {self._edge.edgeId}")

    def undo(self) -> None:
        logger.debug("EdgeAddCommand")
        self._edge.DisconnectFromSockets()
        self._graphicScene.removeItem(self._edge)

    def redo(self) -> None:
        logger.debug("EdgeAddCommand")
        self._edge.ReconnectToSockets()
        self._graphicScene.addItem(self._edge)


class JEdgeRemoveCommand(QtWidgets.QUndoCommand):
    def __init__(self, graphicScene: QGraphicsScene, edge: JGraphicEdge) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._edge: JGraphicEdge = edge
        self.setText(f"delete edge {self._edge.edgeId}")

    def undo(self) -> None:
        logger.debug("EdgeRemoveCommand")
        self._edge.ReconnectToSockets()
        self._graphicScene.addItem(self._edge)

    def redo(self) -> None:
        logger.debug("EdgeRemoveCommand")
        self._edge.DisconnectFromSockets()
        self._graphicScene.removeItem(self._edge)


class JEdgeRerouteCommand(QtWidgets.QUndoCommand):
    def __init__(
        self,
        graphicScene: QGraphicsScene,
        edge: JGraphicEdge,
        nDestinationSocket: JGraphicSocket,
    ) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._edge: JGraphicEdge = edge
        self._oDestinationSocket = edge.destinationSocket
        self._nDestinationSocket = nDestinationSocket
        self.setText(f"re-route edge {self._edge.edgeId}")

    def undo(self) -> None:
        logger.debug("EdgeRerouteCommand")
        self._edge.DisconnectFromSockets()
        assert self._oDestinationSocket is not None
        self._edge.destinationSocket = self._oDestinationSocket

        # ? Disconnecting because i couldnt find the error. remove if u find it
        self._edge.DisconnectFromSockets()
        self._edge.ReconnectToSockets()
        self._edge.update()

    def redo(self) -> None:
        logger.debug("EdgeRerouteCommand")
        self._edge.DisconnectFromSockets()
        self._edge.destinationSocket = self._nDestinationSocket

        # ? Disconnecting because i couldnt find the error. remove if u find it
        self._edge.DisconnectFromSockets()
        self._edge.ReconnectToSockets()
        self._edge.update()
