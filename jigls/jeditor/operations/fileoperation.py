from pprint import pprint
from jigls.jeditor.jdantic import JModel
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

    def SaveFile(self, data: JModel, filename: str):

        file = None

        if not os.path.exists(filename):
            logger.info(f"creating new file {filename}")
            file = open(filename, "x")

        assert os.path.exists(filename), logger.error(f"{filename} not found")

        file = open(filename, "w")

        assert file, logger.error(f"file object is None")

        logger.info(f"saving to file {filename}")

        # ! maybe can fix this
        # json.dump(obj=data.json(), fp=file)
        # file.close()

        # ? writting json string to file
        file.write(data.json())
        file.close()

    def OpenFile(self, filename: str) -> JModel:

        if not os.path.exists(filename):
            logger.error(f"{filename} not found")
            raise FileNotFoundError

        logger.info(f"loading from file {filename}")
        with open(filename, "r") as file:
            return JModel.parse_obj(json.load(file))