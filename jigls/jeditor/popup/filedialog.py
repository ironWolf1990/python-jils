from jigls.jeditor.constants import JCONSTANTS
from typing import Optional
from PyQt5.QtWidgets import QFileDialog


class JFileDialog:
    @staticmethod
    def GetSaveFileName(parent=None) -> Optional[str]:
        fileName, _ = QFileDialog.getSaveFileName(
            parent,
            "J-Editor: save model file",
            ".",
            f"Jigls Model (*.{JCONSTANTS.MODEL.EXTENSION})",
            options=QFileDialog.DontUseNativeDialog,
        )
        return fileName if fileName else None

    @staticmethod
    def GetOpenFileName(parent=None) -> Optional[str]:
        fileName, _ = QFileDialog.getOpenFileName(
            parent,
            "J-Editor: open model file",
            f"./{JCONSTANTS.MODEL.DEFAULT_SAVE_PATH}",
            f"Jigls Model (*.{JCONSTANTS.MODEL.EXTENSION})",
            options=QFileDialog.DontUseNativeDialog,
        )
        return fileName if fileName else None
