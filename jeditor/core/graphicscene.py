from typing import List
from jeditor.constants import JCONSTANTS
from PyQt5 import QtGui, QtWidgets, QtCore
import math


class JGraphicScene(QtWidgets.QGraphicsScene):
    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._InitVariables()

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

    def _InitVariables(self):

        self._colorBackground = QtGui.QColor(JCONSTANTS.GRSCENE.BACKGROUND_COLOR)
        self._colorMajorLine = QtGui.QColor(JCONSTANTS.GRSCENE.MAJOR_LINE_COLOR)
        self._colorMinorLine = QtGui.QColor(JCONSTANTS.GRSCENE.MINOR_LINE_COLOR)

        self._widhtMajorLine: int = JCONSTANTS.GRSCENE.MAJOR_LINE_PEN_WIDTH
        self._widhtMinorLine: int = JCONSTANTS.GRSCENE.MINOR_LINE_PEN_WIDTH
        self._penMajorLine = QtGui.QPen(self._colorMajorLine)
        self._penMinorLine = QtGui.QPen(self._colorMinorLine)

        self._gridSize: int = JCONSTANTS.GRSCENE.GRID_SIZE
        self._lineSpacing: int = JCONSTANTS.GRSCENE.LINE_SPACING
        self._enableGridLines: bool = JCONSTANTS.GRSCENE.GRID_LINES

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)

        if self._enableGridLines:
            self._GridLines(painter, rect)

    def _GridLines(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        # * grid bounds
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        fLeft = left - (left % self._gridSize)
        fTop = top - (top % self._gridSize)

        # * compute lines
        majorLine = [
            QtCore.QLine(x, top, x, bottom)
            for x in range(fLeft, right, self._gridSize * self._lineSpacing)
        ]

        for y in range(fTop, bottom, self._gridSize * self._lineSpacing):
            majorLine.append(QtCore.QLine(left, y, right, y))

        minorLines = [
            QtCore.QLine(x, top, x, bottom) for x in range(fLeft, right, self._gridSize)
        ]

        for y in range(fTop, bottom, self._gridSize):
            minorLines.append(QtCore.QLine(left, y, right, y))

        # * draw lines
        painter.setPen(self._penMajorLine)
        for line in majorLine:
            painter.drawLine(line)

        painter.setPen(self._penMinorLine)
        for line in minorLines:
            painter.drawLine(line)
