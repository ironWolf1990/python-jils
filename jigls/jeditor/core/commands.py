import logging

from jigls.jeditor.ui.graphicedge import JGraphicsEdge
from jigls.jeditor.ui.graphicnode import JGraphicsNode
from jigls.jeditor.ui.graphicsocket import JGraphicsSocket

from jigls.logger import logger
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QUndoCommand

logger = logging.getLogger(__name__)


class JNodeAddCommand(QUndoCommand):
    def __init__(self, graphicScene: QGraphicsScene, node: JGraphicsNode) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._node: JGraphicsNode = node
        self.setText(f"add node {self._node.uid()}")

    def undo(self) -> None:
        logger.debug("NodeAddCommand")
        self._graphicScene.removeItem(self._node)

    def redo(self) -> None:
        logger.debug("NodeAddCommand")
        self._graphicScene.addItem(self._node)


class JNodeRemoveCommand(QUndoCommand):
    def __init__(self, graphicScene: QGraphicsScene, node: JGraphicsNode) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._node: JGraphicsNode = node
        self.setText(f"remove node {self._node.uid()}")

    def undo(self) -> None:
        logger.debug("NodeRemoveCommand")
        self._graphicScene.addItem(self._node)

    def redo(self) -> None:
        logger.debug("NodeRemoveCommand")
        self._graphicScene.removeItem(self._node)


class JNodeMoveCommand(QUndoCommand):
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


class JEdgeAddCommand(QUndoCommand):
    def __init__(
        self,
        graphicScene: QGraphicsScene,
        edge: JGraphicsEdge,
    ) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._edge: JGraphicsEdge = edge
        self._startSocket = edge.startSocket
        self.setText(f"add edge {self._edge.uid}")

    def undo(self) -> None:
        logger.debug("EdgeAddCommand")
        self._edge.DisconnectFromSockets()
        self._graphicScene.removeItem(self._edge)

    def redo(self) -> None:
        logger.debug("EdgeAddCommand")
        self._edge.ConnectToSockets()
        self._graphicScene.addItem(self._edge)


class JEdgeRemoveCommand(QUndoCommand):
    def __init__(self, graphicScene: QGraphicsScene, edge: JGraphicsEdge) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._edge: JGraphicsEdge = edge
        self.setText(f"delete edge {self._edge.uid}")

    def undo(self) -> None:
        logger.debug("EdgeRemoveCommand")
        self._edge.ConnectToSockets()
        self._graphicScene.addItem(self._edge)

    def redo(self) -> None:
        logger.debug("EdgeRemoveCommand")
        self._edge.DisconnectFromSockets()
        self._graphicScene.removeItem(self._edge)


class JEdgeRerouteCommand(QUndoCommand):
    def __init__(
        self,
        graphicScene: QGraphicsScene,
        edge: JGraphicsEdge,
        nDestinationSocket: JGraphicsSocket,
    ) -> None:
        super().__init__()
        self._graphicScene: QGraphicsScene = graphicScene
        self._edge: JGraphicsEdge = edge
        self._oDestinationSocket = edge.destnSocket
        self._nDestinationSocket = nDestinationSocket
        self.setText(f"re-route edge {self._edge.uid}")

    def undo(self) -> None:
        logger.debug("EdgeRerouteCommand")
        self._edge.DisconnectFromSockets()
        assert self._oDestinationSocket is not None
        self._edge.destnSocket = self._oDestinationSocket

        self._edge.ConnectToSockets()
        self._edge.update()

    def redo(self) -> None:
        logger.debug("EdgeRerouteCommand")
        self._edge.DisconnectFromSockets()
        assert self._nDestinationSocket is not None
        self._edge.destnSocket = self._nDestinationSocket

        self._edge.ConnectToSockets()
        self._edge.update()
