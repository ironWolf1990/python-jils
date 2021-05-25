from typing import Optional
from jeditor.core.constants import JCONSTANTS
from jeditor.core.contentwidget import JNodeContent
from jeditor.core.graphicnode import JGraphicNode
import uuid


class JNodeFactory:
    def __init__(self) -> None:
        pass

    def RegisterNode(self):
        pass

    def CreateNode(
        self,
        nodeId: Optional[str],
        inputMulti,
        outputMulti,
        inputs=1,
        output=1,
        *args,
        **kwargs
    ):
        if nodeId is None:
            nodeId = uuid.uuid4().hex
        node = JGraphicNode(nodeContent=JNodeContent(), nodeId=nodeId)
        for _ in range(inputs):
            socketId = uuid.uuid4().hex
            node.socketManager.AddSocket(
                socketId=socketId,
                type=JCONSTANTS.GRSOCKET.TYPE_INPUT,
                multiConnection=inputMulti,
            )
        for _ in range(output):
            socketId = uuid.uuid4().hex
            node.socketManager.AddSocket(
                socketId=socketId,
                type=JCONSTANTS.GRSOCKET.TYPE_OUTPUT,
                multiConnection=outputMulti,
            )

        return node
