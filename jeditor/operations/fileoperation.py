import json
import logging
from typing import Dict, List, Optional

from jeditor.logger import logger
from PyQt5 import QtCore
import os


logger = logging.getLogger(__name__)


class JFileManager(QtCore.QObject):
    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent=parent)

    def SaveToFile(self, data: Dict, fileName: str):
        file = None
        if not os.path.exists(fileName):
            file = open(fileName, "x")

        assert os.path.exists(fileName), logger.error(f"{fileName} not found")
        file = open(fileName, "w")

        assert file, logger.error(f"file object is None")

        logger.info(f"saving to file {fileName}")
        json.dump(obj=data, fp=file)
        file.close()

    def LoadFromFile(self, fileName: str) -> Dict:

        assert os.path.exists(fileName), logger.error(f"{fileName} not found")

        logger.info(f"loading from file {fileName}")
        with open(fileName, "r") as file:
            return json.load(file)
