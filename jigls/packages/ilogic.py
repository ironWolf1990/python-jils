from jigls.jcore.ioperation import JOperation
from jigls.jeditor.constants import JCONSTANTS
from jigls.jcore import INode, ISocket


def _iOpNot(a: bool):
    return not a


def _iOpAdd(a: bool, b: bool):
    return a and b


class iGate2Node(INode):
    def __init__(self, name):
        super().__init__(name, traceback=True)
        self.AddSocket(
            ISocket(
                pNode=self,
                name="A",
                type=JCONSTANTS.SOCKET.TYPE_INPUT,
                dataType=bool,
            )
        )
        self.AddSocket(
            ISocket(
                pNode=self,
                name="A",
                type=JCONSTANTS.SOCKET.TYPE_INPUT,
                dataType=bool,
            )
        )
        self.AddSocket(
            ISocket(
                pNode=self,
                name="B",
                type=JCONSTANTS.SOCKET.TYPE_OUTPUT,
                dataType=bool,
            )
        )


class iNot(INode):
    def __init__(self, name, traceback=False):
        super().__init__(name, traceback=traceback)
        self.AddSocket(
            ISocket(
                pNode=self,
                name="A",
                type=JCONSTANTS.SOCKET.TYPE_INPUT,
                dataType=bool,
            )
        )
        self.AddSocket(
            ISocket(
                pNode=self,
                name="B",
                type=JCONSTANTS.SOCKET.TYPE_OUTPUT,
                dataType=bool,
            )
        )
        self.AddOperation(JOperation(name="Not", inputs=["A"], outputs=["B"], fn=_iOpNot))


class iAnd(INode):
    def __init__(self, name, traceback=False):
        super().__init__(name, traceback=traceback)
        self.AddSocket(
            ISocket(
                pNode=self,
                name="A",
                type=JCONSTANTS.SOCKET.TYPE_INPUT,
                dataType=bool,
            )
        )
        self.AddSocket(
            ISocket(
                pNode=self,
                name="B",
                type=JCONSTANTS.SOCKET.TYPE_INPUT,
                dataType=bool,
            )
        )
        self.AddSocket(
            ISocket(
                pNode=self,
                name="C",
                type=JCONSTANTS.SOCKET.TYPE_OUTPUT,
                dataType=bool,
            )
        )
        self.AddOperation(JOperation(name="Not", inputs=["A", "B"], outputs=["C"], fn=_iOpAdd))
