import json
import logging
import typing
from typing import Dict, List, Optional, Set, Tuple

from jigls.jeditor.constants import JCONSTANTS
from jigls.jeditor.operations.clipboardoperation import JClipboard
from jigls.jeditor.operations.datastreamer import JDataStreamer
from jigls.jeditor.operations.edgeoperation import JEdgeDragging, JEdgeRerouting
from jigls.jeditor.operations.fileoperation import JFileManager
from jigls.jeditor.operations.nodefactory import JNodeFactory
from jigls.jeditor.ui.graphicedge import JGraphicsEdge
from jigls.jeditor.ui.graphicnode import JGraphicsNode
from jigls.jeditor.ui.graphicsocket import JGraphicsSocket
from jigls.logger import logger
from PyQt5.QtCore import QObject, QPointF, QRectF
from PyQt5.QtWidgets import QGraphicsItem, QUndoStack

from .commands import (
    JEdgeAddCommand,
    JEdgeRemoveCommand,
    JEdgeRerouteCommand,
    JNodeAddCommand,
    JNodeRemoveCommand,
)
from .graphicscene import JGraphicScene

logger = logging.getLogger(__name__)


class JSceneManager(QObject):
    def __init__(self) -> None:
        super().__init__(parent=None)

        self._graphicsScene = JGraphicScene()

        self._nodeFactory = JNodeFactory()
        self._undoStack = QUndoStack(self._graphicsScene)
        self._edgeDragging = JEdgeDragging(self._graphicsScene)
        self._edgeReroute = JEdgeRerouting(self._graphicsScene)

        self._dataStreamer = JDataStreamer(self._graphicsScene)
        self._fileManager = JFileManager()
        self._clipboard = JClipboard()

        self._currentFile: Optional[str] = None

        self._debug()

    @property
    def graphicsScene(self) -> JGraphicScene:
        return self._graphicsScene

    @property
    def nodeFactory(self) -> JNodeFactory:
        return self._nodeFactory

    @property
    def undoStack(self) -> QUndoStack:
        return self._undoStack

    @property
    def dataStreamer(self) -> JDataStreamer:
        return self._dataStreamer

    @property
    def fileManager(self) -> JFileManager:
        return self._fileManager

    @property
    def clipboard(self) -> JClipboard:
        return self._clipboard

    def _debug(self):
        node1 = self._nodeFactory.CreateNode(False, False)
        node2 = self._nodeFactory.CreateNode(True, True)
        node3 = self._nodeFactory.CreateNode(True, False)
        # node4 = JGraphicNode(inSockets=1, outSockets=1, nodeContent=JNodeContent())

        node1.setPos(QPointF(-350, -250))
        node2.setPos(QPointF(-75, 0))
        node3.setPos(QPointF(0, 0))

        self.graphicsScene.addItem(node1)
        self.graphicsScene.addItem(node2)
        self.graphicsScene.addItem(node3)

    def SaveFile(self, filename):
        logger.info(f"saving to file")
        self._fileManager.SaveFile(self._dataStreamer.Serialize(), filename=filename)

    def OpenFile(self, filename):
        logger.info(f"loading from file")
        self._undoStack.clear()
        self._graphicsScene.clear()
        for gItem in self._dataStreamer.Deserialize(self._fileManager.OpenFile(filename=filename)):
            if gItem is None:
                logger.error(f"deserialization error, got 'None' item")
                continue
            self._graphicsScene.addItem(gItem)

    def StartEdgeDrag(self, item: QGraphicsItem) -> bool:
        assert isinstance(item, JGraphicsSocket)
        return self._edgeDragging.StartDrag(item)

    def EndEdgeDrag(self, item: QGraphicsItem) -> bool:
        ret = self._edgeDragging.EndDrag(item)
        if ret:
            edge = self._edgeDragging._tempEdge
            assert edge is not None

            logger.debug(f"add new edge {edge.uid()}")

            self.undoStack.beginMacro("add edge")
            self.undoStack.push(JEdgeAddCommand(graphicScene=self.graphicsScene, edge=edge))
            self.undoStack.endMacro()

            self._edgeDragging.Reset()

        return ret

    def StartEdgeReRoute(self, cursorPos: QPointF) -> bool:
        if len(self._graphicsScene.selectedItems()) == 0:
            logger.warning("no edge selected for rerouting")
            return False
        elif len(self._graphicsScene.selectedItems()) > 1:
            logger.warning("multiple items selected for rerouting. select 1 edge")
            return False

        assert self._graphicsScene.selectedItems(), logger.error(
            f"initial edge rerouting condition check failed"
        )

        item = self._graphicsScene.selectedItems()[0]

        if not isinstance(item, JGraphicsEdge):
            logger.warning("none edge type selected for rerouting")
            return False
        elif isinstance(item, JGraphicsEdge):
            self._edgeReroute.StartRerouting(item, cursorPos)
            return True

        logger.error("edge rerouting failed")
        return False

    def EndEdgeReRoute(self, item: QGraphicsItem) -> bool:
        ret = self._edgeReroute.EndRerouting(item)
        if ret:
            edge = self._edgeReroute._tempEdge
            nDestinationSocket = self._edgeReroute._nDestinationSocket

            assert edge is not None
            assert nDestinationSocket is not None

            logger.debug(f"rerouting edge {edge.uid()}")
            self.undoStack.beginMacro("rerouting edge")
            self.undoStack.push(
                JEdgeRerouteCommand(
                    graphicScene=self.graphicsScene,
                    edge=edge,
                    nDestinationSocket=nDestinationSocket,
                )
            )
            self.undoStack.endMacro()
            self._edgeReroute.Reset()
        return ret

    def RemoveFromScene(self):
        if not self._graphicsScene.selectedItems():
            logger.debug("no items to delete")
            return

        edgeIdRemove: Set[str] = set()
        nodeIdRemove: Set[str] = set()

        for item in self._graphicsScene.selectedItems():
            if isinstance(item, JGraphicsNode):
                nodeIdRemove.add(item.uid())

                for gSocket in item.graphicsSocketList:
                    for edge in self._graphicsScene.items():
                        if isinstance(edge, JGraphicsEdge) and any(
                            gSocket.uid() == socket.uid() for socket in (edge.startSocket, edge.destnSocket)
                        ):
                            edgeIdRemove.add(edge.uid())

            elif isinstance(item, JGraphicsEdge):
                edgeIdRemove.add(item.uid())

            elif isinstance(item, JGraphicsSocket):
                continue

            else:
                logger.debug(f"unknown item selected in delete type {type(item)}")

        logger.debug(f"nodes marked for removal {nodeIdRemove}")
        logger.debug(f"edges marked for removal {edgeIdRemove}")

        self.undoStack.beginMacro("remove item")
        # * first always remove edges, easier to implement undo stack!
        self.RemoveEdgesFromScene(edgeIdRemove)
        self.RemoveNodesFromScene(nodeIdRemove)
        self.undoStack.endMacro()

    def RemoveNodesFromScene(self, nodes: typing.Set[str]):
        for node in nodes:
            self.RemoveNodeFromScene(node)

    def RemoveEdgesFromScene(self, edges: typing.Set[str]):
        for edge in edges:
            self.RemoveEdgeFromScene(edge)

    def RemoveNodeFromScene(self, nodeId: str):
        node_ = list(
            filter(
                lambda node: isinstance(node, JGraphicsNode) and node.uid() == nodeId,
                self._graphicsScene.items(),
            )
        )
        if len(node_) != 1:
            logger.error(f"error fetching node {nodeId} for removal, not found in scene")
            return

        node__ = node_[0]
        assert isinstance(node__, JGraphicsNode)

        logger.debug(f"remove node {nodeId}")
        self.undoStack.beginMacro("remove node")
        self.undoStack.push(JNodeRemoveCommand(graphicScene=self.graphicsScene, node=node__))
        self.undoStack.endMacro()

    def RemoveEdgeFromScene(self, edgeId: str):
        edge_ = list(
            filter(
                lambda edge: isinstance(edge, JGraphicsEdge) and edge.uid() == edgeId,
                self._graphicsScene.items(),
            )
        )
        if len(edge_) != 1:
            logger.error(f"error fetching edge {edgeId} for removal, not found in scene")
            return

        edge__ = edge_[0]
        assert isinstance(edge__, JGraphicsEdge)

        logger.debug(f"remove edge {edgeId}")
        self.undoStack.beginMacro("remove edge")
        self.undoStack.push(JEdgeRemoveCommand(graphicScene=self.graphicsScene, edge=edge__))
        self.undoStack.endMacro()

    def DebugSceneInformation(self):
        print(f"\n{30*'='}\n{10*'-'} SCENE NODES")
        for item in self._graphicsScene.items():
            if isinstance(item, JGraphicsNode):
                print(item)
        print(f"{10*'-'} SCENE EDGES")
        for item in self._graphicsScene.items():
            if isinstance(item, JGraphicsEdge):
                print(item)
        print(f"{10*'-'} SCENE SOCKET")
        for item in self._graphicsScene.items():
            if isinstance(item, JGraphicsSocket):
                print(item)
        print(f"{30*'='}\n")

    def CopyItems(self):
        logger.info("copying selected item")
        self._clipboard.Copy(self._dataStreamer.Serialize(selected=True))

    def CutItems(self):

        logger.info("cutting selected item")

        self._clipboard.Cut(self._dataStreamer.Serialize(selected=True))
        self.RemoveFromScene()

    def PasteItems(self, mousePosition: QPointF):

        logger.info("pasting selected item")

        genPaste = self._clipboard.Paste(mousePosition)
        if genPaste is None:
            logger.warning("no graphic items to paste")
            return

        self._undoStack.beginMacro("pasting items")
        for gItem in self._dataStreamer.Deserialize(genPaste):
            if isinstance(gItem, JGraphicsNode):
                self._undoStack.beginMacro("pasting node")
                self._undoStack.push(JNodeAddCommand(self._graphicsScene, gItem))
                self._undoStack.endMacro()

            if isinstance(gItem, JGraphicsEdge):
                gItem.DisconnectFromSockets()
                self._undoStack.beginMacro("pasting node")
                self._undoStack.push(JEdgeAddCommand(self._graphicsScene, gItem))
                self._undoStack.endMacro()

        self._undoStack.endMacro()

    def FocusSelection(self, focusList: Optional[List[str]] = None) -> QRectF:

        items: List[QGraphicsItem] = []

        # ? focus list got from search
        if focusList:
            logger.debug("focus items")
            # * to get rid of stupid error. dont like red lines in editor
            focusList_ = focusList
            items = list(
                filter(
                    lambda item: isinstance(item, JGraphicsNode) and item.uid() in focusList_,
                    self._graphicsScene.items(),
                )
            )

        else:
            items_ = self._graphicsScene.selectedItems()

            if len(items_) == 0:
                logger.debug("fit to view")
                items = list(
                    filter(lambda item: isinstance(item, JGraphicsNode), self._graphicsScene.items())
                )
            else:
                logger.debug("focus selected items")
                items = list(filter(lambda item: isinstance(item, JGraphicsNode), items_))

        self._graphicsScene.clearSelection()
        for item in items:
            item.setSelected(True)

        group = self._graphicsScene.createItemGroup(items)
        rect = group.boundingRect()
        self._graphicsScene.destroyItemGroup(group)
        return rect
