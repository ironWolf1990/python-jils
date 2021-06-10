from jigls.jeditor.constants import JCONSTANTS
from jigls.jeditor.ui.graphicedge import JGraphicsEdge
from PyQt5.QtCore import QObject, QPointF
from jigls.jeditor.ui.graphicsocket import JGraphicsSocket
import logging
from typing import Optional, Tuple
from PyQt5 import QtWidgets

from jigls.logger import logger

logger = logging.getLogger(__name__)


class JEdgeDragging(QObject):
    def __init__(self, graphicsScene: QtWidgets.QGraphicsScene):
        self._graphicsScene = graphicsScene
        self._startSocket: Optional[JGraphicsSocket] = None
        self._destinationSocket: Optional[JGraphicsSocket] = None
        self._dragPosition: QPointF = QPointF()
        self._tempEdge: Optional[JGraphicsEdge] = None

    def StartDrag(self, startSocket: QtWidgets.QGraphicsItem) -> bool:

        assert isinstance(startSocket, JGraphicsSocket)

        # todo enable drawing edge from input socket
        if startSocket.socketType() == JCONSTANTS.SOCKET.TYPE_INPUT:
            logger.debug("cannot start drawing edge from input socket, select an output socket")
            return False

        if startSocket.multiConnection():

            self._tempEdge = JGraphicsEdge.DragNewEdge(
                startSocket=startSocket,
                dragPos=startSocket.scenePos(),
            )

            self._graphicsScene.addItem(self._tempEdge)
            self._tempEdge.update()
            self._startSocket = startSocket
            self._dragPosition = startSocket.scenePos()
            logger.debug(f"creating new edge {self._tempEdge.uid()}")
            return True

        elif not startSocket.AtMaxLimit():

            self._tempEdge = JGraphicsEdge.DragNewEdge(
                startSocket=startSocket,
                dragPos=startSocket.scenePos(),
            )

            self._graphicsScene.addItem(self._tempEdge)
            self._tempEdge.update()
            self._startSocket = startSocket
            self._dragPosition = startSocket.scenePos()
            logger.debug(f"creating new edge {self._tempEdge.uid()}")
            return True

        logger.warning(f"unable to create new edge from current socket {startSocket.uid()}")
        return False

    def UpdateDragPosition(self, dragPosition: QPointF):

        assert self._tempEdge is not None
        self._dragPosition = dragPosition
        self._tempEdge.dragPos = dragPosition
        self._tempEdge.update()

    def EndDrag(self, destnSocket: QtWidgets.QGraphicsItem) -> bool:

        assert self._tempEdge is not None
        flag: Optional[bool] = None

        if isinstance(destnSocket, JGraphicsSocket):
            # * check same socket
            if self._startSocket.uid() == destnSocket.uid():
                logger.warning(f"tried connecting same socket")
                flag = False

            # * check if same socket type, intput type
            elif destnSocket.socketType() == JCONSTANTS.SOCKET.TYPE_OUTPUT:
                logger.warning(f"tried connecting output type")
                flag = False

            # * check if connecttion possible, non multi connection type
            elif destnSocket.AtMaxLimit():
                logger.warning(f"socket cannot add edge, maxlimit")
                flag = False

            # * check sockets belong to same parent
            elif self._tempEdge.startSocket.nodeId() == destnSocket.nodeId():
                logger.warning(f"socket belong to same parent")
                flag = False

            elif (
                len(
                    list(
                        filter(
                            lambda edge: isinstance(edge, JGraphicsEdge)
                            and isinstance(destnSocket, JGraphicsSocket)
                            and edge.uid() != self._tempEdge.uid()
                            and edge.startSocket.uid() == self._tempEdge.startSocket.uid()
                            and edge.destnSocket.uid() == destnSocket.uid(),
                            self._graphicsScene.items(),
                        )
                    )
                )
                >= 1
            ):
                logger.warning(f"duplicate edge")
                flag = False

            # * only add edge if all above fail
            else:
                logger.debug("adding new edge")
                flag = True

        elif not isinstance(destnSocket, JGraphicsSocket):
            logger.warning(f"clicked none socket type")
            flag = False

        if flag is None:
            logger.error("unhandled condition")
            # self._tempEdge.DisconnectFromSockets()
            self._graphicsScene.removeItem(self._tempEdge)
            self.Reset()
            return False
        elif not flag:
            # self._tempEdge.DisconnectFromSockets()
            self._graphicsScene.removeItem(self._tempEdge)
            self.Reset()
            return False
        elif flag:
            assert isinstance(destnSocket, JGraphicsSocket)
            self._tempEdge.destnSocket = destnSocket

            # # ! this step is done so that the logic can be handeled in redo for EdgeAddCommand
            # self._tempEdge.DisconnectFromSockets()
            self._graphicsScene.removeItem(self._tempEdge)
            return True
        return False

    def Reset(self):
        assert isinstance(self._tempEdge, JGraphicsEdge)
        self._tempEdge.update()
        self._startSocket = None
        self._destinationSocket = None
        self._dragPosition = QPointF()
        self._tempEdge = None


class JEdgeRerouting(QObject):
    def __init__(self, graphicsScene: QtWidgets.QGraphicsScene):
        self._graphicsScene = graphicsScene

        self._startSocket: Optional[JGraphicsSocket] = None
        self._oDestinationSocket: Optional[JGraphicsSocket] = None
        self._nDestinationSocket: Optional[JGraphicsSocket] = None
        self._dragPosition: QPointF = QPointF()

        self._tempEdge: Optional[JGraphicsEdge] = None

    def StartRerouting(self, edge: QtWidgets.QGraphicsItem, tempDragPos: QPointF):
        assert isinstance(edge, JGraphicsEdge)
        assert self._tempEdge is None, logger.error(
            "re-routing a new edge while previous edge re-routing is not finished / not reset to none"
        )

        logger.debug(f"re-routing edge {edge.uid()}")
        self._tempEdge = edge
        self._tempEdge.DisconnectFromSockets()
        self._startSocket = edge.startSocket
        self._oDestinationSocket = edge.destnSocket
        self._dragPosition = tempDragPos
        self._tempEdge.dragPos = tempDragPos
        self._tempEdge.update()
        return True

    def UpdateDragPosition(self, dragPosition: QPointF):
        assert self._tempEdge is not None
        self._dragPosition = dragPosition
        self._tempEdge.dragPos = dragPosition
        self._tempEdge.update()

    def EndRerouting(self, destnSocket: QtWidgets.QGraphicsItem) -> bool:

        assert self._tempEdge is not None
        flag: Optional[bool] = None

        if isinstance(destnSocket, JGraphicsSocket):
            # * check same socket
            if self._startSocket.uid() == destnSocket.uid():
                logger.warning(f"tried connecting to start socket")
                flag = False

            # * check if same socket type, output to output type
            elif destnSocket.socketType == JCONSTANTS.SOCKET.TYPE_OUTPUT:
                logger.warning(f"tried connecting output type socket")
                flag = False

            # * check if connecttion possible, non multi connection type
            elif destnSocket.AtMaxLimit():
                logger.warning(f"socket cannot add edge, maxlimit")
                flag = False

            # * check sockets belong to same parent
            elif self._tempEdge.startSocket.nodeId() == destnSocket.nodeId():
                logger.warning(f"socket belong to same parent")
                flag = False

            # * reconnecting to same destination socket
            elif self._oDestinationSocket.uid() == destnSocket.uid():
                logger.warning(f"reconnecting to same destination socket")
                flag = False

            # * checking for duplicate edge
            elif (
                len(
                    list(
                        filter(
                            lambda edge: isinstance(edge, JGraphicsEdge)
                            and isinstance(destnSocket, JGraphicsSocket)
                            and edge.uid() != self._tempEdge.uid()
                            and edge.startSocket.uid() == self._tempEdge.startSocket.uid()
                            and edge.destnSocket.uid() == destnSocket.uid(),
                            self._graphicsScene.items(),
                        )
                    )
                )
                >= 1
            ):
                logger.warning(f"duplicate edge")
                flag = False

            # * only add edge if all above fail
            else:
                flag = True

        elif not isinstance(destnSocket, JGraphicsSocket):
            logger.warning(f"clicked none socket type")
            flag = False

        if flag is None:
            logger.error("unhandled condition")
            assert isinstance(self._oDestinationSocket, JGraphicsSocket)
            self._tempEdge.destnSocket = self._oDestinationSocket
            self.Reset()
            return False

        elif not flag:
            logger.error("edge re-routing failed, reverting to previous connection")
            assert isinstance(self._oDestinationSocket, JGraphicsSocket)
            self._tempEdge.destnSocket = self._oDestinationSocket
            self.Reset()
            return False

        elif flag:
            logger.debug("re-routing edge")
            assert isinstance(destnSocket, JGraphicsSocket)
            self._nDestinationSocket = destnSocket

            # ! this step is done so that the logic can be handeled in redo for EdgeAddCommand
            assert isinstance(self._oDestinationSocket, JGraphicsSocket)
            self._tempEdge.destnSocket = self._oDestinationSocket
            return True
        return False

    def Reset(self):
        assert isinstance(self._tempEdge, JGraphicsEdge)
        self._tempEdge.update()
        self._startSocket = None
        self._oDestinationSocket = None
        self._nDestinationSocket = None
        self._dragPosition = QPointF()
        self._tempEdge = None