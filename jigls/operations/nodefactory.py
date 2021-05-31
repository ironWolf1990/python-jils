from jigls.base.nodebase import JBaseNode
from typing import Optional
from jigls.constants import JCONSTANTS
from jigls.ui.graphicnode import JGraphicsNode
import uuid


class JNodeFactory:
    def __init__(self) -> None:
        pass

    def RegisterNode(self):
        pass

    def CreateNode(self, inputMulti, outputMulti, inputs=2, output=1, *args, **kwargs):

        base = JBaseNode("base node")
        for i in range(inputs):
            base.AddInputSocket(
                name=f"in{i}",
                multiConnection=inputMulti,
            )
        for _ in range(output):
            base.AddOutputSocket(
                name="out1",
                multiConnection=outputMulti,
            )
        node = JGraphicsNode(base)

        return node
