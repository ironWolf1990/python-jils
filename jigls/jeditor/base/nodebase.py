from __future__ import annotations
from jigls.jcore.ibase import INode, ISocket
from jigls.jeditor.jdantic import JNodeModel
from jigls.jeditor.constants import JCONSTANTS
from jigls.jeditor.base.socketbase import JBaseSocket
import logging
from typing import Dict, List, Optional, OrderedDict, Set

from jigls.jeditor.utils import UniqueIdentifier
from jigls.logger import logger

logger = logging.getLogger(__name__)

from operator import itemgetter, attrgetter


class JBaseNode(INode):
    def __init__(self, name: str, uid: Optional[str] = None) -> None:
        super().__init__(name, uid=uid)

    def InSocketList(self) -> List[JBaseSocket]:
        return list(  # type:ignore
            filter(
                lambda socket: socket.Type == JCONSTANTS.SOCKET.TYPE_INPUT,
                self.socketList,
            )
        )

    def OutSocketList(self) -> List[JBaseSocket]:
        return list(  # type:ignore
            filter(
                lambda socket: socket.Type == JCONSTANTS.SOCKET.TYPE_OUTPUT,
                self._socketList,
            )
        )

    def AddInputSocket(self, name: str, multiConnection: bool = True):
        self.AddSocket(
            JBaseSocket(
                name=name, pNode=self, type=JCONSTANTS.SOCKET.TYPE_INPUT, multiConnect=multiConnection
            )
        )

    def AddOutputSocket(self, name: str, multiConnection: bool = True):
        self.AddSocket(
            JBaseSocket(
                name=name, pNode=self, type=JCONSTANTS.SOCKET.TYPE_OUTPUT, multiConnect=multiConnection
            )
        )

    def __repr__(self) -> str:
        return super().__repr__()

    def Serialize(self):
        return JNodeModel(
            name=self.name,
            uid=self.uid,
            socketList=[
                socket_.Serialize()
                for sockets in (self.InSocketList(), self.OutSocketList())
                for socket_ in sockets
            ],
        )

    @classmethod
    def Deserialize(cls, nodeModel: JNodeModel) -> JBaseNode:

        baseNode = JBaseNode(name=nodeModel.name, uid=nodeModel.uid)

        for socket in nodeModel.socketList:
            baseNode.AddSocket(
                JBaseSocket.Deserialize(
                    pNode=baseNode,
                    name=socket.name,
                    uid=socket.uid,
                    type=socket.type,
                    multiConnect=socket.multiConnect,
                )
            )

        return baseNode
