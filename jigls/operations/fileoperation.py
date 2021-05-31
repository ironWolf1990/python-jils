from pprint import pprint
from jigls.jdantic import JModel
import json
import logging
from typing import Dict, List, Optional

from jigls.logger import logger
from PyQt5 import QtCore
import os

from pathlib import Path

logger = logging.getLogger(__name__)


class JFileManager(QtCore.QObject):
    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent=parent)

    def SaveToFile(self, data: JModel, fileName: str):
        file = None
        if not os.path.exists(fileName):
            file = open(fileName, "x")

        assert os.path.exists(fileName), logger.error(f"{fileName} not found")
        file = open(fileName, "w")

        assert file, logger.error(f"file object is None")

        logger.info(f"saving to file {fileName}")

        json.dump(obj=data.json(), fp=file)
        file.close()

    def LoadFromFile(self, fileName: str) -> JModel:

        if not os.path.exists(fileName):
            logger.error(f"{fileName} not found")
            raise FileNotFoundError

        logger.info(f"loading from file {fileName}")
        with open(fileName, "r") as file:
            return JModel.parse_raw(json.load(file))