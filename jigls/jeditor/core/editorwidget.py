# from gui.graphicedge import JigleGraphicEdge
from .scenemanager import JSceneManager
from .graphicview import JGraphicView
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QVBoxLayout, QWidget


class JEditorWidget(QWidget):
    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.initUI()

    def initUI(self):

        # * set layout
        self.layout_ = QVBoxLayout()
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_)

        # * scene manager
        self._sceneManager = JSceneManager()

        # * graphic view here
        self._graphicsView = JGraphicView(self._sceneManager, self)
        self.layout_.addWidget(self._graphicsView)

    @property
    def graphicsScene(self) -> QGraphicsScene:
        return self._sceneManager._graphicsScene

    @property
    def graphicView(self) -> JGraphicView:
        return self._graphicsView

    @property
    def sceneManager(self) -> JSceneManager:
        return self._sceneManager
