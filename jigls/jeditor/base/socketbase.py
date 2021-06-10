from __future__ import annotations
from jigls.jeditor.jdantic import JSocketModel

import typing
from jigls.jcore.ibase import INode, ISocket
import logging
from typing import List, Optional, Union
from jigls.logger import logger

logger = logging.getLogger(__name__)


class JBaseSocket(ISocket):
    def __init__(
        self, name: str, pNode: INode, type: int, uid: Optional[str] = None, multiConnect=True
    ) -> None:
        super().__init__(name=name, pNode=pNode, type=type, uid=uid)
        self._multiConnect = multiConnect

    @property
    def nodeId(self):
        return self.pNode.uid

    @property
    def multiConnect(self):
        return self._multiConnect

    @multiConnect.setter
    def multiConnect(self, value: bool):
        self._multiConnect = value

    def AtMaxLimit(self) -> bool:
        if self._multiConnect:
            return False
        # * can add one edge to single connection type
        elif not self._multiConnect and len(self.connections) == 0:
            return False
        else:
            return True

    def __repr__(self) -> str:
        return f"{super().__repr__()} multiConnect: {self._multiConnect}"

    def Serialize(self) -> JSocketModel:

        """
        name: str
        uid: str
        type: int
        multiConnect: bool
        dataType: Callable
        default: Optional[Any]
        exec: bool
        execOnChange: bool
        execOnConnect: bool
        monitorOnChange: bool
        traceback: bool
        """
        return JSocketModel(
            name=self.name,
            uid=self.uid,
            type=self.Type,
            multiConnect=self.multiConnect,
            dataType=self.dataType.__name__,
            exec=self.exec,
            execOnChange=self.execOnChange,
            execOnConnect=self.execOnConnect,
            monitorOnChange=self.monitorOnChange,
            traceback=self.traceback,
        )

    @classmethod
    def Deserialize(cls, pNode: INode, name: str, uid: str, type: int, multiConnect: bool):
        return JBaseSocket(pNode=pNode, name=name, uid=uid, type=type, multiConnect=multiConnect)
