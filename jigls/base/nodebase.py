from jigls.jdantic import JNodeModel
from jigls.constants import JCONSTANTS
from jigls.base.socketbase import JBaseSocket
import logging
from typing import Dict, List, Optional, OrderedDict, Set

from jigls.utils import UniqueIdentifier
from jigls.logger import logger

logger = logging.getLogger(__name__)

from operator import itemgetter, attrgetter, mul


class JBaseNode(object):
    def __init__(
        self,
        name: str,
        uid: Optional[str] = None,
        isExec: bool = False,
        ticker: Optional[float] = None,
    ):

        self._name: str = name
        self._uid: str = UniqueIdentifier() if uid is None else uid
        self._dirty: bool = False
        self._isExec: bool = isExec
        self._ticker: Optional[float] = ticker
        self._socketList: Set[JBaseSocket] = set()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def uid(self) -> str:
        return self._uid

    @property
    def dirty(self) -> bool:
        return self._dirty

    @dirty.setter
    def dirty(self, value: bool) -> None:
        self._dirty = value

    @property
    def isExec(self) -> bool:
        return self._isExec

    @isExec.setter
    def isExec(self, value: bool) -> None:
        self._isExec = value

    @property
    def ticker(self) -> Optional[float]:
        return self._ticker

    @ticker.setter
    def ticker(self, value: Optional[float]) -> None:
        self._ticker = value

    @property
    def socketList(self) -> List[JBaseSocket]:
        return list(self._socketList)

    @property
    def inSocketList(self) -> List[JBaseSocket]:
        return list(
            filter(
                lambda socket: socket.type == JCONSTANTS.SOCKET.TYPE_INPUT,
                self._socketList,
            )
        )

    @property
    def outSocketList(self) -> List[JBaseSocket]:
        return list(
            filter(
                lambda socket: socket.type == JCONSTANTS.SOCKET.TYPE_OUTPUT,
                self._socketList,
            )
        )

    def AddInputSocket(self, name: str, multiConnection: bool = True):
        if len(self.GetSocketByName(name)) >= 1:
            logger.error(f"socket name {name} already present")
            return

        self._socketList.add(
            JBaseSocket(
                name=name,
                index=len(self.socketList) + 1,
                nodeID=self.uid,
                type=JCONSTANTS.SOCKET.TYPE_INPUT,
                multiConnection=multiConnection,
                uid=None,
            )
        )

    def AddOutputSocket(self, name: str, multiConnection: bool = True):
        if len(self.GetSocketByName(name)) >= 1:
            logger.error(f"socket name {name} already present")
            return

        self._socketList.add(
            JBaseSocket(
                name=name,
                index=len(self.socketList) + 1,
                nodeID=self.uid,
                type=JCONSTANTS.SOCKET.TYPE_OUTPUT,
                multiConnection=multiConnection,
                uid=None,
            )
        )

    def GetSocketByName(self, name: str) -> List[JBaseSocket]:
        return list(
            filter(
                lambda socket: socket.name == name,
                self._socketList,
            )
        )

    def GetSocketByUID(self, uid: str) -> List[JBaseSocket]:
        return list(
            filter(
                lambda socket: socket.uid == uid,
                self._socketList,
            )
        )

    def _compute(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self) -> str:
        return "nm:%s uid:%s iS(s):%s oS(s):%s" % (
            self.name,
            self.uid,
            len(self.inSocketList),
            len(self.outSocketList),
        )

    def Serialize(self):
        return JNodeModel(
            name=self.name,
            uid=self.uid,
            socketList=[socket.Serialize() for socket in self.socketList],
        )

    @classmethod
    def Deserialize(cls, nodeModel: JNodeModel):

        baseNode = JBaseNode(name=nodeModel.name, uid=nodeModel.uid.hex)

        for socket in sorted(
            list(
                filter(
                    lambda socket: socket.type == JCONSTANTS.SOCKET.TYPE_INPUT,
                    nodeModel.socketList,
                )
            ),
            key=attrgetter("index"),
        ):
            baseNode._socketList.add(
                JBaseSocket(
                    name=socket.name,
                    uid=socket.uid.hex,
                    nodeID=socket.nodId.hex,
                    index=socket.index,
                    type=socket.type,
                    multiConnection=socket.multiConnection,
                )
            )

        for socket in sorted(
            list(
                filter(
                    lambda socket: socket.type == JCONSTANTS.SOCKET.TYPE_OUTPUT,
                    nodeModel.socketList,
                )
            ),
            key=attrgetter("index"),
        ):
            baseNode._socketList.add(
                JBaseSocket(
                    name=socket.name,
                    uid=socket.uid.hex,
                    nodeID=socket.nodId.hex,
                    index=socket.index,
                    type=socket.type,
                    multiConnection=socket.multiConnection,
                )
            )

        return baseNode
