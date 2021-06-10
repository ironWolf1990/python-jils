# from __future__ import annotations
# from jigls.jcore.abstract import JAbstractBase

# import logging
# from typing import Any, Dict, Optional

# from jigls.jeditor.base.socketbase import JBaseSocket
# from jigls.jeditor.jdantic import JGrEdgeModel
# from jigls.logger import logger
# from jigls.jeditor.utils import UniqueIdentifier

# logger = logging.getLogger(__name__)


# class JBaseEdge(JAbstractBase):
#     def __init__(
#         self,
#         name: str,
#         startSocket=JBaseSocket,
#         destnSocket: Optional[JBaseSocket] = None,
#         uid: Optional[str] = None,
#     ) -> None:
#         super().__init__(name, uid=uid)

#         self._startSocket: JBaseSocket = startSocket
#         self._destnSocket: Optional[JBaseSocket] = destnSocket

#         if self._destnSocket is not None:
#             self._startSocket.Connect(self._destnSocket)

#     @property
#     def startSocket(self):
#         return self._startSocket

#     @property
#     def destnSocket(self):
#         return self._destnSocket

#     @destnSocket.setter
#     def destnSocket(self, destnSocket: JBaseSocket) -> None:
#         if destnSocket.AtMaxLimit():
#             logger.error(f"E:{self._uid} D:{destnSocket.uid} max edge limit reached")
#             return None
#         self._destnSocket = destnSocket

#     def DisconnectFromSockets(self):
#         if self._destnSocket is not None:
#             self._startSocket.Disconnect(self._destnSocket)

#     def ReconnectToSockets(self):
#         if self._destnSocket is not None:
#             self._startSocket.Connect(self._destnSocket)

#     def __repr__(self) -> str:
#         return "U:%s S:%s D:%s" % (self.uid, self.startSocket, self.destnSocket)

#     def Serialize(self):
#         pass
#         # return JEdgeModel(
#         #     uid=self.uid,
#         #     startSocket=self.startSocket.uid,
#         #     destnSocket=self.destnSocket.uid,
#         # )

#     @classmethod
#     def Deserialize(cls, uid: str, startSocket: JBaseSocket, destnSocket: JBaseSocket):
#         pass
#         # if startSocket.AtMaxLimit():
#         #     logger.error(
#         #         f"E:{uid} S:{startSocket.uid} D:{destnSocket.uid}, start socket at max conection limit"
#         #     )
#         #     return None
#         # elif destnSocket.AtMaxLimit():
#         #     logger.error(
#         #         f"E:{uid} S:{startSocket.uid} D:{destnSocket.uid}, destn socket at max conection limit"
#         #     )
#         #     return None

#         # return JBaseEdge(uid=uid, startSocket=startSocket, destnSocket=destnSocket)

#     @classmethod
#     def NewEdge(cls, startSocket: JBaseSocket):
#         pass
#         # if startSocket.AtMaxLimit():
#         #     logger.error("error deserializing edge, start socket at max limit")
#         #     return None

#         # return JBaseEdge(startSocket=startSocket)
