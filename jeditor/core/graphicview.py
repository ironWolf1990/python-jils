from json.encoder import JSONEncoder
import logging
import typing
from copy import deepcopy

from jeditor.core.graphicedge import JGraphicEdge
from jeditor.core.graphicnode import JGraphicNode
from jeditor.core.graphicsocket import JGraphicSocket
from jeditor.core.scenemanager import JSceneManager
from jeditor.logger import logger
from PyQt5 import QtCore, QtGui, QtWidgets

from jeditor.constants import JCONSTANTS

logger = logging.getLogger(__name__)


class JGraphicView(QtWidgets.QGraphicsView):
    def __init__(
        self,
        sceneManager: JSceneManager,
        parent: typing.Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._sceneManager: JSceneManager = sceneManager

        self.setScene(sceneManager.graphicsScene)

        self.initUI()

    def initUI(self):

        self.scrollbarVertPolicy: int = JCONSTANTS.GRVIEW.VERT_SCROLLBAR
        self.scrollbarHorzPolicy: int = JCONSTANTS.GRVIEW.HORZ_SCROLLBAR

        self._zoomInFactor: float = JCONSTANTS.GRVIEW.ZOOM_IN_FACTOR
        self._zoomClamped: bool = JCONSTANTS.GRVIEW.ZOOM_CLAMPED
        self._zoom: int = JCONSTANTS.GRVIEW.ZOOM
        self._zoomStep: int = JCONSTANTS.GRVIEW.ZOOM_STEP

        self._zoomRangeMin = JCONSTANTS.GRVIEW.ZOOM_RANGE_MIN
        self._zoomRangeMax = JCONSTANTS.GRVIEW.ZOOM_RANGE_MAX
        self._currentMode: int = JCONSTANTS.GRVIEW.MODE_DEFAULT
        self._previousState: typing.Optional[int] = None

        # * selection band
        self._rubberband: QtWidgets.QRubberBand = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, self
        )
        self._rubberBandStart: QtCore.QPoint = QtCore.QPoint()

        self.setRenderHints(
            QtGui.QPainter.Antialiasing  # type:ignore
            | QtGui.QPainter.HighQualityAntialiasing
            | QtGui.QPainter.TextAntialiasing
            | QtGui.QPainter.SmoothPixmapTransform
        )

        # * policy and property
        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        # self.setOptimizationFlag(QtWidgets.QGraphicsView.DontAdjustForAntialiasing)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.MinimalViewportUpdate)
        self.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy(self.scrollbarHorzPolicy)
        )
        self.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy(self.scrollbarVertPolicy)
        )
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        # * helper
        self._mousePosition = QtCore.QPointF()

    def mousePressEvent(self, event: QtGui.QMouseEvent):

        # * pan view
        if event.button() == QtCore.Qt.RightButton:
            self._previousState = self._currentMode
            self._currentMode = JCONSTANTS.GRVIEW.MODE_PAN_VIEW
            self.prevPos = event.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.setInteractive(False)

        # * Rubber band selection
        elif (
            event.button() == QtCore.Qt.LeftButton
            and event.modifiers() == QtCore.Qt.NoModifier
            and self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform())
            is None
        ):
            self._currentMode = JCONSTANTS.GRVIEW.MODE_SELECTION
            self._InitRubberband(event.pos())
            self.setInteractive(False)

        # * start edge drag
        elif (
            event.button() == QtCore.Qt.LeftButton
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
            and isinstance(
                self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()),
                JGraphicSocket,
            )
        ):
            self.StartEdgeDrag(
                self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform())
            )

        # * end edge drag
        elif (
            event.button() == QtCore.Qt.LeftButton
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_DRAG
        ):
            self.EndEdgeDrag(
                self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform())
            )

        # * end edge reroute
        elif (
            event.button() == QtCore.Qt.LeftButton
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_REROUTE
        ):
            self.EndEdgeReRouting(
                self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform())
            )

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):

        # * pan canvas.
        if self._currentMode == JCONSTANTS.GRVIEW.MODE_PAN_VIEW:
            offset = self.prevPos - event.pos()  # type:ignore
            self.prevPos = event.pos()
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + offset.y()
            )
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + offset.x()
            )

        # * RuberBand selection.
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_SELECTION:
            self._rubberband.setGeometry(
                QtCore.QRect(self._rubberBandOrigin, event.pos()).normalized()
            )

        # * Edge drag
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_DRAG:
            self._sceneManager._edgeDragging.UpdateDragPosition(
                self.mapToScene(event.pos())
            )

        # * edge rerouting
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_REROUTE:
            self._sceneManager._edgeReroute.UpdateDragPosition(
                self.mapToScene(event.pos())
            )

        # * save mouse positon if needed to be used by other methods
        self._mousePosition = self.mapToScene(event.pos())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):

        # * Pan view
        if self._currentMode == JCONSTANTS.GRVIEW.MODE_PAN_VIEW:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.setInteractive(True)
            assert self._previousState is not None
            self._currentMode = self._previousState
            self._previousState = None

        # * Selection
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_SELECTION:
            self._rubberband.setGeometry(
                QtCore.QRect(self._rubberBandOrigin, event.pos()).normalized()
            )
            painterPath = self._ReleaseRubberband()
            self.setInteractive(True)
            self.scene().setSelectionArea(painterPath)
            self._currentMode = JCONSTANTS.GRVIEW.MODE_DEFAULT

        # * do nothing is rerouting edge
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_DRAG:
            pass

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        return super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        zoomOutFactor = 1 / self._zoomInFactor

        if event.angleDelta().y() > 0:
            zoomFactor = self._zoomInFactor
            self._zoom += self._zoomStep
        else:
            zoomFactor = zoomOutFactor
            self._zoom -= self._zoomStep

        clamped = False
        if self._zoom < self._zoomRangeMin:
            self._zoom, clamped = self._zoomRangeMin, True
        if self._zoom > self._zoomRangeMax:
            self._zoom, clamped = self._zoomRangeMax, True

        if not clamped or self._zoomClamped is False:
            self.scale(zoomFactor, zoomFactor)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:

        # * delete item(s) in scene
        if event.key() == QtCore.Qt.Key_Delete:
            self._sceneManager.RemoveFromScene()

        # * save to file
        elif (
            event.key() == QtCore.Qt.Key_S
            and event.modifiers() == QtCore.Qt.ControlModifier
        ):
            self._sceneManager.SaveToFile()

        # * load from file
        elif (
            event.key() == QtCore.Qt.Key_O
            and event.modifiers() == QtCore.Qt.ControlModifier
        ):
            self._sceneManager.LoadFromFile()

        # * undo
        elif (
            event.key() == QtCore.Qt.Key_Z
            and event.modifiers() == QtCore.Qt.ControlModifier
        ):
            self._sceneManager.undoStack.undo()

        # * redo
        elif (
            event.key() == QtCore.Qt.Key_R
            and event.modifiers() == QtCore.Qt.ControlModifier
        ):
            self._sceneManager.undoStack.redo()

        # * debug
        elif event.key() == QtCore.Qt.Key_D and event.modifiers() == (
            QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier
        ):
            self._sceneManager.DebugSceneInformation()

        # * debug
        elif (
            event.key() == QtCore.Qt.Key_E
            and event.modifiers() == QtCore.Qt.ShiftModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.StartEdgeReRouting()

        # * cut
        elif (
            event.key() == QtCore.Qt.Key_X
            and event.modifiers() == QtCore.Qt.NoModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.CutGraphicsItems()

        # * copy
        elif (
            event.key() == QtCore.Qt.Key_C
            and event.modifiers() == QtCore.Qt.NoModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.CopyGraphicsItems()

        # * paste
        elif (
            event.key() == QtCore.Qt.Key_V
            and event.modifiers() == QtCore.Qt.NoModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.PasteGraphicsItems()

        super().keyPressEvent(event)

    def _InitRubberband(self, position: QtCore.QPoint):
        self._rubberBandStart = position
        self._rubberBandOrigin = position
        self._rubberband.setGeometry(
            QtCore.QRect(self._rubberBandOrigin, QtCore.QSize())
        )
        self._rubberband.show()

    def _ReleaseRubberband(self):
        painterPath = QtGui.QPainterPath()
        rect = self.mapToScene(self._rubberband.geometry())
        painterPath.addPolygon(rect)
        self._rubberband.hide()
        return painterPath

    def StartEdgeDrag(self, item: QtWidgets.QGraphicsItem):
        assert isinstance(item, JGraphicSocket)
        if self._sceneManager.StartEdgeDrag(item):
            self._currentMode = JCONSTANTS.GRVIEW.MODE_EDGE_DRAG
            self.setCursor(QtCore.Qt.DragLinkCursor)

    def EndEdgeDrag(self, item: QtWidgets.QGraphicsItem):
        self._sceneManager.EndEdgeDrag(item)
        self._currentMode = JCONSTANTS.GRVIEW.MODE_DEFAULT
        self.setCursor(QtCore.Qt.ArrowCursor)

    def StartEdgeReRouting(self):
        if self._sceneManager.StartEdgeReRoute(self._mousePosition):
            self._currentMode = JCONSTANTS.GRVIEW.MODE_EDGE_REROUTE
            self.setCursor(QtCore.Qt.DragLinkCursor)

    def EndEdgeReRouting(self, item: QtWidgets.QGraphicsItem):
        self._sceneManager.EndEdgeReRoute(item)
        self._currentMode = JCONSTANTS.GRVIEW.MODE_DEFAULT
        self.setCursor(QtCore.Qt.ArrowCursor)

    def CopyGraphicsItems(self):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(
                f"can only perform copy action in MODE_DEFAULT, current mode {self._currentMode}"
            )
            return
        self._sceneManager.CopyItems()

    def CutGraphicsItems(self):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(
                f"can only perform cut action in MODE_DEFAULT, current mode {self._currentMode}"
            )
            return
        self._sceneManager.CutItems()

    def PasteGraphicsItems(self):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(
                f"can only perform paste action in MODE_DEFAULT, current mode {self._currentMode}"
            )
            return
        self._sceneManager.PasteItems(self._mousePosition)
