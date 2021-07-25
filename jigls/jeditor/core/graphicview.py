from jigls.jeditor.jdantic import JModel
import logging
import typing
from typing import List, Optional

from jigls.jeditor.constants import JCONSTANTS
from jigls.jeditor.core.scenemanager import JSceneManager
from jigls.jeditor.ui.graphicnode import JGraphicsNode
from jigls.jeditor.ui.graphicsocket import JGraphicsSocket
from jigls.jeditor.widgets.dockwidget import DockWidget

from jigls.logger import logger
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint, QPointF, QRect, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QTransform, QWheelEvent
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsView, QMenu, QRubberBand, QWidget

logger = logging.getLogger(__name__)
import weakref
from copy import deepcopy


class JGraphicView(QGraphicsView):

    SignalNodeDoubleClick = pyqtSignal(object, name="david")

    def __init__(
        self,
        sceneManager: JSceneManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._sceneManager: JSceneManager = sceneManager

        self.setScene(sceneManager.graphicsScene)

        self.initUI()

    @property
    def sceneManager(self) -> JSceneManager:
        return self._sceneManager

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
        self._previousState: Optional[int] = None

        # * selection band
        self._rubberband: QRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self._rubberBandStart: QPoint = QPoint()

        self.setRenderHints(
            QtGui.QPainter.Antialiasing  # type:ignore
            # | QtGui.QPainter.HighQualityAntialiasing
            | QtGui.QPainter.TextAntialiasing
            | QtGui.QPainter.SmoothPixmapTransform
        )

        # * policy and property
        self.setCacheMode(QGraphicsView.CacheBackground)

        # self.setOptimizationFlag(QtWidgets.QGraphicsView.DontAdjustForAntialiasing)
        # self.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)

        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy(self.scrollbarHorzPolicy))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy(self.scrollbarVertPolicy))
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # * helper
        self._mousePosition = QPointF()

    def mousePressEvent(self, event: QMouseEvent):

        # * pan view
        if event.button() == Qt.RightButton:
            self._previousState = self._currentMode
            self._currentMode = JCONSTANTS.GRVIEW.MODE_PAN_VIEW
            self.prevPos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.setInteractive(False)

        # * Rubber band selection
        elif (
            event.button() == Qt.LeftButton
            and event.modifiers() == Qt.NoModifier
            and self.scene().itemAt(self.mapToScene(event.pos()), QTransform()) is None
        ):
            self._currentMode = JCONSTANTS.GRVIEW.MODE_SELECTION
            self._InitRubberband(event.pos())
            self.setInteractive(False)

        # * start edge drag
        elif (
            event.button() == Qt.LeftButton
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
            and isinstance(
                self.scene().itemAt(self.mapToScene(event.pos()), QTransform()),
                JGraphicsSocket,
            )
        ):
            self.StartEdgeDrag(self.scene().itemAt(self.mapToScene(event.pos()), QTransform()))

        # * end edge drag
        elif event.button() == Qt.LeftButton and self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_DRAG:
            self.EndEdgeDrag(self.scene().itemAt(self.mapToScene(event.pos()), QTransform()))

        # * end edge reroute
        elif event.button() == Qt.LeftButton and self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_REROUTE:
            self.EndEdgeReRouting(self.scene().itemAt(self.mapToScene(event.pos()), QTransform()))

        # * save mouse positon if needed to be used by other methods
        self._mousePosition = self.mapToScene(event.pos())

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):

        # * pan canvas.
        if self._currentMode == JCONSTANTS.GRVIEW.MODE_PAN_VIEW:
            offset = self.prevPos - event.pos()  # type:ignore
            self.prevPos = event.pos()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + offset.x())

        # * RuberBand selection.
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_SELECTION:
            self._rubberband.setGeometry(QRect(self._rubberBandOrigin, event.pos()).normalized())

        # * Edge drag
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_DRAG:
            self._sceneManager._edgeDragging.UpdateDragPosition(self.mapToScene(event.pos()))

        # * edge rerouting
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_REROUTE:
            self._sceneManager._edgeReroute.UpdateDragPosition(self.mapToScene(event.pos()))

        # * save mouse positon if needed to be used by other methods
        self._mousePosition = self.mapToScene(event.pos())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):

        # * Pan view
        if self._currentMode == JCONSTANTS.GRVIEW.MODE_PAN_VIEW:
            self.setCursor(Qt.ArrowCursor)
            self.setInteractive(True)
            assert self._previousState is not None
            self._currentMode = self._previousState
            self._previousState = None

        # * Selection
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_SELECTION:
            self._rubberband.setGeometry(QRect(self._rubberBandOrigin, event.pos()).normalized())
            painterPath = self._ReleaseRubberband()
            self.setInteractive(True)
            self.scene().setSelectionArea(painterPath)
            self._currentMode = JCONSTANTS.GRVIEW.MODE_DEFAULT

        # * do nothing is rerouting edge
        elif self._currentMode == JCONSTANTS.GRVIEW.MODE_EDGE_DRAG:
            pass

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        # ? was old idea, double click to show node property in dock
        # self.o1 = DockWidget()
        # self.o2 = DockWidget()
        # self.tog = False
        # if (
        #     event.button() == Qt.LeftButton
        #     and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        #     and isinstance(
        #         self.scene().itemAt(self.mapToScene(event.pos()), QTransform()),
        #         (JGraphicsNode, JProxyWidget),
        #     )
        # ):
        #     logger.debug("got double click for dock")
        #     if self.tog:
        #         self.SignalNodeDoubleClick.emit(weakref.ref(self.o1))  # type:ignore
        #         self.tog = not self.tog
        #     elif not self.tog:
        #         self.SignalNodeDoubleClick.emit(weakref.ref(self.o2))  # type:ignore
        #         self.tog = not self.tog

        return super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        return super().contextMenuEvent(event)
        # ? was old idea,node context menu triggered by keypress
        # contextMenu = QMenu(self)
        # newAct = contextMenu.addAction("New")
        # newClose = contextMenu.addAction("Close")

        # # if self.underMouse()
        # action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        # if action == newClose:
        #     print(action.text())
        #     contextMenu.close()

        # self.setCursor(Qt.ArrowCursor)
        # self.setInteractive(True)

    def wheelEvent(self, event: QWheelEvent):
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

    def keyPressEvent(self, event: QKeyEvent) -> None:

        # * delete item(s) in scene
        if event.key() == Qt.Key_Delete:
            self._sceneManager.RemoveFromScene()

        # * save to file
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            self.SaveFile(filename=f"default.{JCONSTANTS.MODEL.FILE_EXTENSION}")

        # * load from file
        elif event.key() == Qt.Key_O and event.modifiers() == Qt.ControlModifier:
            self.OpenFile(filename=f"default.{JCONSTANTS.MODEL.FILE_EXTENSION}")

        # * undo
        elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            self._sceneManager.undoStack.undo()

        # * redo
        elif event.key() == Qt.Key_R and event.modifiers() == Qt.ControlModifier:
            self._sceneManager.undoStack.redo()

        # * debug
        elif event.key() == Qt.Key_D and event.modifiers() == (Qt.ShiftModifier | Qt.ControlModifier):
            self._sceneManager.DebugSceneInformation()

        # * edge reroute
        elif (
            event.key() == Qt.Key_E
            and event.modifiers() == Qt.ShiftModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.StartEdgeReRouting()

        # * cut
        elif (
            event.key() == Qt.Key_X
            and event.modifiers() == Qt.NoModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.CutGraphicsItems()

        # * copy
        elif (
            event.key() == Qt.Key_C
            and event.modifiers() == Qt.NoModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.CopyGraphicsItems()

        # * paste
        elif (
            event.key() == Qt.Key_V
            and event.modifiers() == Qt.NoModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.PasteGraphicsItems()

        # * focus elements
        elif (
            event.key() == Qt.Key_F
            and event.modifiers() == Qt.ShiftModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.FocusSelection()

        # * node create menu
        elif (
            # event.key() == Qt.Key_N
            # and event.modifiers() == Qt.ShiftModifier
            event.key() == Qt.Key_Tab
            and event.modifiers() == Qt.NoModifier
            and self._currentMode == JCONSTANTS.GRVIEW.MODE_DEFAULT
        ):
            self.GraphicsNodeContextMenu()

        super().keyPressEvent(event)

    def _InitRubberband(self, position: QPoint):
        self._rubberBandStart = position
        self._rubberBandOrigin = position
        self._rubberband.setGeometry(QRect(self._rubberBandOrigin, QSize()))
        self._rubberband.show()

    def _ReleaseRubberband(self):
        painterPath = QtGui.QPainterPath()
        rect = self.mapToScene(self._rubberband.geometry())
        painterPath.addPolygon(rect)
        self._rubberband.hide()
        return painterPath

    def _ResetZoom(self, center: Optional[QPointF] = None):
        sceneRange = QtCore.QRectF(0, 0, self.size().width(), self.size().height())
        if center:
            sceneRange.translate(center.x() - sceneRange.center().x(), center.y() - sceneRange.center().y())
        self.setSceneRect(sceneRange)
        self.fitInView(sceneRange)
        # self._zoom = self._zoomRangeMax

    # ? OPERATIONS
    def StartEdgeDrag(self, item: QGraphicsItem):
        assert isinstance(item, JGraphicsSocket)
        if self._sceneManager.StartEdgeDrag(item):
            self._currentMode = JCONSTANTS.GRVIEW.MODE_EDGE_DRAG
            self.setCursor(Qt.DragLinkCursor)

    def EndEdgeDrag(self, item: QGraphicsItem):
        self._sceneManager.EndEdgeDrag(item)
        self._currentMode = JCONSTANTS.GRVIEW.MODE_DEFAULT
        self.setCursor(Qt.ArrowCursor)

    def StartEdgeReRouting(self):
        if self._sceneManager.StartEdgeReRoute(self._mousePosition):
            self._currentMode = JCONSTANTS.GRVIEW.MODE_EDGE_REROUTE
            self.setCursor(Qt.DragLinkCursor)

    def EndEdgeReRouting(self, item: QGraphicsItem):
        self._sceneManager.EndEdgeReRoute(item)
        self._currentMode = JCONSTANTS.GRVIEW.MODE_DEFAULT
        self.setCursor(Qt.ArrowCursor)

    def CopyGraphicsItems(self):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(f"can only perform copy action in MODE_DEFAULT, current mode {self._currentMode}")
            return
        self._sceneManager.CopyItems()

    def CutGraphicsItems(self):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(f"can only perform cut action in MODE_DEFAULT, current mode {self._currentMode}")
            return
        self._sceneManager.CutItems()

    def PasteGraphicsItems(self):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(f"can only perform paste action in MODE_DEFAULT, current mode {self._currentMode}")
            return
        self._sceneManager.PasteItems(self._mousePosition)

    def FocusSelection(self, focusList: Optional[List[str]] = None):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(f"can only perform paste action in MODE_DEFAULT, current mode {self._currentMode}")
            return

        rect = self._sceneManager.FocusSelection(focusList)

        if JCONSTANTS.GRVIEW.ZOOM_CLAMPED:
            self.centerOn(rect.center())
        else:
            self.fitInView(rect, QtCore.Qt.KeepAspectRatio)

    def SaveFile(self, filename: str):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(f"can only perform paste action in MODE_DEFAULT, current mode {self._currentMode}")
            return

        self._sceneManager.SaveFile(filename=filename)

    def OpenFile(self, filename: str):
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(f"can only perform paste action in MODE_DEFAULT, current mode {self._currentMode}")
            return

        self._sceneManager.OpenFile(filename=filename)

    def GraphicsNodeContextMenu(self):

        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(f"can only perform paste action in MODE_DEFAULT, current mode {self._currentMode}")
            return

        if not self.underMouse():
            logger.debug(f"graphicsview not under mouse")
            return

        self._sceneManager.GraphicsNodeContextMenu(
            self.mapToGlobal(self.mapFromScene(self._mousePosition)), self._mousePosition
        )

    def SearchGraphicsNode(self) -> Optional[JModel]:
        if self._currentMode != JCONSTANTS.GRVIEW.MODE_DEFAULT:
            logger.error(f"can only perform paste action in MODE_DEFAULT, current mode {self._currentMode}")
            return None

        return self._sceneManager.modelStreamer.Serialize()
