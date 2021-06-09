from __future__ import annotations
import typing
from jigls.jcore.abstract import JAbstractBase

import logging
from typing import Any, Callable, Dict, List, Optional, Set, Union

from jigls.jcore.ioperation import JOperation
from jigls.jeditor.constants import JCONSTANTS

from jigls.logger import logger

logger = logging.getLogger(__name__)


class INode(JAbstractBase):
    def __init__(self, name: str, uid: Optional[str] = None, exec: bool = True, traceback=False) -> None:
        super().__init__(name, uid=uid, exec=exec, traceback=traceback)
        self._socketList: Set[ISocket] = set()
        self._operationList: Set[JOperation] = set()

    @property
    def socketList(self):
        return self._socketList

    @property
    def operationList(self):
        return self._operationList

    @property
    def data(self) -> Dict[str, Any]:
        return {socket.name: socket.data for socket in self._socketList}

    @property
    def dirty(self) -> bool:
        return any(
            socket.dirty == True for socket in self._socketList if socket.Type == JCONSTANTS.SOCKET.TYPE_INPUT
        )

    def IsDirty(self) -> bool:
        return self.dirty

    def GetSocketByName(self, name: str) -> Optional[ISocket]:
        socket_ = [socket for socket in self._socketList if socket.name == name]
        if len(socket_) == 0:
            logger.error(f"socket {name} does not exsist in list")
            return None
        elif len(socket_) == 1:
            return socket_[0]
        elif len(socket_) > 1:
            logger.error("socket with duplicate names found!")
            return None

    def GetSocketByUid(self, uid: str) -> Optional[ISocket]:
        socket_ = [socket for socket in self._socketList if socket.uid == uid]
        if len(socket_) == 0:
            logger.error(f"socket {uid} does not exsist in list")
            return None
        elif len(socket_) == 1:
            return socket_[0]
        elif len(socket_) > 1:
            logger.error("socket with duplicate uids found!")
            return None

    def AddSocket(self, socket: ISocket) -> None:
        if any(socket.name == socket_.name for socket_ in self._socketList):
            logger.error(f"socket with name {socket.name} already exsists in list")
            return
        if any(socket.uid == socket_.uid for socket_ in self._socketList):
            logger.error(f"socket with uid {socket.uid} already exsists in list")
            return
        self._socketList.add(socket)

    def AddOperation(self, op: JOperation):
        if any(op.name == op_.name for op_ in self._operationList):
            logger.error(f"operation with name {op.name} already exsists in list")
            return

        inputs = set(op.inputs)
        sockets = set([socket.name for socket in self._socketList])
        if not inputs.issubset(sockets):
            logger.error(
                f"for operation with name {op.name}, node {self.name} does not provide all inputs, missing {inputs.difference(sockets)}"
            )
            return

        self._operationList.add(op)

    def Compute(self, operation: JOperation):
        for k, v in operation.Compute(self.data).items():
            socket = self.GetSocketByName(k)
            if socket is not None:
                socket.Set(v)
            elif socket is None:
                logger.error(
                    f"found none socket in function {self.name}:{operation.name}:{operation.fn.__name__}"
                )
            else:
                logger.error(
                    f"output {k} in function {self.name}:{operation.name}:{operation.fn.__name__} not found in socket list"
                )

    def _Compute(self):
        if not self.exec:
            if self.traceback:
                logger.warning(f"node {self.name} is not an execution node")
            return

        if self.IsDirty():
            if self.traceback:
                logger.error(f"node {self.name} unable to compute, socket(s) are dirty")
            return
        if self.operationList is None:
            if self.traceback:
                logger.debug(f"no operation attached to {self.name}")
            return

        for operation in self.operationList:
            if self.traceback:
                logger.info(f"node {self.name} computing {operation}")
            self.Compute(operation)

    def __repr__(self) -> str:
        return f"{super().__repr__()} sockets:{len(self._socketList)} operations:{len(self._operationList)}"


class ISocket(JAbstractBase):
    def __init__(
        self,
        name: str,
        pNode: INode,
        type: int,
        uid: Optional[str] = None,
        exec: bool = True,
        dataType: Callable = bool,
        default: Optional[Any] = None,
        execOnChange: bool = True,
        execOnConnect: bool = True,
        monitorOnChange: bool = False,
        traceback=False,
    ) -> None:
        super().__init__(name, uid=uid, exec=exec, traceback=traceback)

        self._name: str = name
        self._pNode: INode = pNode
        self._type: int = type
        self._dataType: Callable = dataType
        self._data: Optional[Any] = default
        self._default: Optional[Any] = default
        self._execOnChange: bool = execOnChange
        self._execOnConnect: bool = execOnConnect
        self._monitorOnChange: bool = monitorOnChange
        self._connections: Set[ISocket] = set()
        self._dirty: bool = True

    @property
    def pNode(self) -> INode:
        return self._pNode

    @property
    def Type(self):
        return self._type

    @property
    def dataType(self):
        return self._dataType

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: Any) -> None:
        assert type(value) == type(self._dataType())
        self._data = value

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value: Any) -> None:
        assert type(value) == type(self._dataType())
        self._default = value

    @property
    def execOnChange(self):
        return self._execOnChange

    @execOnChange.setter
    def execOnChange(self, value: bool) -> None:
        self._execOnChange = value

    @property
    def execOnConnect(self):
        return self._execOnConnect

    @execOnConnect.setter
    def execOnConnect(self, value: bool) -> None:
        self._execOnConnect = value

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value: bool) -> None:
        self._dirty = value

        for socket in self._connections:
            # ! this check is no longer needed, should be removed
            if self._type == JCONSTANTS.SOCKET.TYPE_INPUT and socket.Type == JCONSTANTS.SOCKET.TYPE_OUTPUT:
                # * this is done, so that propagation doesnt go in reverse direction
                continue
            if self.traceback:
                logger.debug(
                    f"node:{self.pNode.name} sock:{self.name} setting node:{socket.pNode.name} socket:{socket.name} dirty:{socket.dirty} -> {value}"
                )
            socket.dirty = value

    @property
    def monitorOnChange(self):
        return self._monitorOnChange

    @monitorOnChange.setter
    def monitorOnChange(self, value: bool) -> None:
        self._monitorOnChange = value

    @property
    def connections(self) -> typing.Set[ISocket]:
        return self._connections

    def GetConnectionByName(self, name: str) -> List[ISocket]:
        return list(
            filter(
                lambda socket: socket.name == name,
                self._connections,
            )
        )

    def GetConnectionByUid(self, uid: str):
        return list(
            filter(
                lambda socket: socket.uid == uid,
                self._connections,
            )
        )

    def Connect(self, dSocket: Union[List[ISocket], ISocket]):
        if isinstance(dSocket, list):
            for socket in dSocket:
                self._Connect(socket)
        else:
            self._Connect(dSocket)

    def _Connect(self, cSocket: ISocket):

        # * input can connect to input (used for gouping nodes)
        # * output can connect to input
        # * output can connect to output (used for data forwarding)
        if self.Type == JCONSTANTS.SOCKET.TYPE_INPUT and cSocket.Type == JCONSTANTS.SOCKET.TYPE_OUTPUT:
            if self._traceback:
                logger.warning(
                    f"node:{self.pNode.name} sock:{self.name} connect to node:{cSocket.pNode.name} sock:{cSocket.name}, input connect to output. Set() and Dirty() will not be called for this connection"
                )

        if cSocket.dataType() != self.dataType():
            logger.error(
                f"node:{self.pNode.name} sock:{self.name} cannot connect to node:{cSocket.pNode.name} sock:{cSocket.name}, datatype missmatch {self.data} {cSocket.dataType}"
            )
            return

        if len(self.GetConnectionByUid(cSocket.uid)) >= 1:
            logger.error(f"node:{cSocket.pNode.name} sock:{cSocket.name}, already in connection list")
            return

        self._connections.add(cSocket)
        if self.exec and self._execOnConnect:
            cSocket.Set(self.data)

    def Disconnect(self, dSocket: Union[List[ISocket], ISocket]):
        if isinstance(dSocket, list):
            for socket in dSocket:
                self._Disconnect(socket)
        else:
            self._Disconnect(dSocket)

    def _Disconnect(self, cSocket: ISocket):
        if len(self.GetConnectionByUid(cSocket.uid)) == 0:
            logger.error(f"node:{cSocket.pNode.name} sock:{cSocket.name} not found in connection list")

        self._connections.discard(cSocket)
        cSocket.Set(cSocket.default)

    def HasConnection(self, socket: ISocket) -> bool:
        socket_ = self.GetConnectionByUid(socket.uid)
        if len(socket_) >= 1:
            return True
        return False

    def Compute(self):
        if self.exec and self._execOnChange:
            if self.traceback:
                logger.debug(f"{self.pNode.name}:{self.name} triggering compute")
            self._pNode._Compute()

    def Set(self, value):

        if not self.exec:
            if self.traceback:
                logger.debug(f"node:{self._pNode.name} sock:{self._name} is not executable")
            return

        if type(self.dataType()) != type(value):
            self.dirty = True
            if self.traceback:
                logger.debug(f"node:{self._pNode.name} sock:{self._name} set value {value} - is dirty")
        elif self.dirty:
            self.dirty = False

        if self._data == value:
            if self.traceback:
                logger.debug(f"node:{self._pNode.name} sock:{self._name} no change in value")
            return

        if self._monitorOnChange:
            logger.debug(
                f"node:{self._pNode.name} sock:{self._name} dirty: {self.dirty} data:{self._data} -> {value}"
            )

        self._data = value

        for socket in self._connections:
            # ! this check is no longer needed, should be removed
            if self._type == JCONSTANTS.SOCKET.TYPE_INPUT and socket.Type == JCONSTANTS.SOCKET.TYPE_OUTPUT:
                # * this is done, so that propagation doesnt go in reverse direction
                continue
            socket.Set(value)

        if not self.dirty and self.Type != JCONSTANTS.SOCKET.TYPE_OUTPUT:
            self.Compute()

    def Get(self):
        return self._data

    def __repr__(self) -> str:
        return f"{super().__repr__()} name:{self._name} type:{self._type} dataType:{self._dataType} data {self._data} execControl:{self._exec} execOnChange:{self._execOnChange} execOnConnect:{self._execOnConnect} dirty:{self._dirty} connections:{len(self._connections)}"