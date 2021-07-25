from typing import List
from jigls.jeditor.constants import JCONSTANTS
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import QLine, QRectF
import math


class JGraphicScene(QGraphicsScene):
    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.initUI()

        self._penMajorLine.setWidth(self._widhtMajorLine)
        self._penMinorLine.setWidth(self._widhtMinorLine)

        self.setSceneRect(
            -JCONSTANTS.GRSCENE.WIDTH // 2,
            -JCONSTANTS.GRSCENE.HEIGHT // 2,
            JCONSTANTS.GRSCENE.WIDTH,
            JCONSTANTS.GRSCENE.HEIGHT,
        )
        self.setBackgroundBrush(self._colorBackground)

    def SetWidthHeight(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def initUI(self):

        self._colorBackground = QColor(JCONSTANTS.GRSCENE.BACKGROUND_COLOR)
        self._colorMajorLine = QColor(JCONSTANTS.GRSCENE.MAJOR_LINE_COLOR)
        self._colorMinorLine = QColor(JCONSTANTS.GRSCENE.MINOR_LINE_COLOR)

        self._widhtMajorLine: int = JCONSTANTS.GRSCENE.MAJOR_LINE_PEN_WIDTH
        self._widhtMinorLine: int = JCONSTANTS.GRSCENE.MINOR_LINE_PEN_WIDTH
        self._penMajorLine = QPen(self._colorMajorLine)
        self._penMinorLine = QPen(self._colorMinorLine)

        self._gridSize: int = JCONSTANTS.GRSCENE.GRID_SIZE
        self._lineSpacing: int = JCONSTANTS.GRSCENE.LINE_SPACING
        self._enableGridLines: bool = JCONSTANTS.GRSCENE.GRID_LINES

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)

        if self._enableGridLines:
            self._GridLines(painter, rect)

    def _GridLines(self, painter: QPainter, rect: QRectF):
        # * grid bounds
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        fLeft = left - (left % self._gridSize)
        fTop = top - (top % self._gridSize)

        # * compute lines
        majorLine = [
            QLine(x, top, x, bottom) for x in range(fLeft, right, self._gridSize * self._lineSpacing)
        ]

        for y in range(fTop, bottom, self._gridSize * self._lineSpacing):
            majorLine.append(QLine(left, y, right, y))

        minorLines = [QLine(x, top, x, bottom) for x in range(fLeft, right, self._gridSize)]

        for y in range(fTop, bottom, self._gridSize):
            minorLines.append(QLine(left, y, right, y))

        # * draw lines
        painter.setPen(self._penMajorLine)
        for line in majorLine:
            painter.drawLine(line)

        painter.setPen(self._penMinorLine)
        for line in minorLines:
            painter.drawLine(line)
