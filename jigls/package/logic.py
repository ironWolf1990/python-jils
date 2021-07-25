from jigls.jeditor.constants import JCONSTANTS
from jigls.jcore import INode, ISocket


class Gate2Node(INode):
    def __init__(self, name):
        INode.__init__(self, name)
        self.A = ISocket(
            pNode=self,
            name="A",
            type=JCONSTANTS.SOCKET.TYPE_INPUT,
            dataType=bool,
        )
        self.B = ISocket(
            pNode=self,
            name="B",
            type=JCONSTANTS.SOCKET.TYPE_INPUT,
            dataType=bool,
        )
        self.C = ISocket(
            pNode=self,
            name="C",
            type=JCONSTANTS.SOCKET.TYPE_OUTPUT,
            dataType=bool,
        )


class Not(INode):
    def __init__(self, name):
        INode.__init__(self, name)
        self.A = ISocket(
            pNode=self,
            name="A",
            type=JCONSTANTS.SOCKET.TYPE_INPUT,
            dataType=bool,
        )
        self.B = ISocket(
            pNode=self,
            name="B",
            type=JCONSTANTS.SOCKET.TYPE_OUTPUT,
            dataType=bool,
        )

    def _Compute(self):
        self.B.Set(not self.A.data)


class And(Gate2Node):
    def __init__(self, name):
        Gate2Node.__init__(self, name)

    def _Compute(self):
        self.C.Set(self.A.data and self.B.data)


class Or(Gate2Node):
    def __init__(self, name):
        Gate2Node.__init__(self, name)

    def _Compute(self):
        self.C.Set(self.A.data or self.B.data)


class Xor(Gate2Node):
    def __init__(self, name):
        Gate2Node.__init__(self, name)
        self.A1 = And("A1")
        self.A2 = And("A2")
        self.I1 = Not("I1")
        self.I2 = Not("I2")
        self.O1 = Or("O1")
        self.A.Connect([self.A1.A, self.I2.A])
        self.B.Connect([self.I1.A, self.A2.A])
        self.I1.B.Connect([self.A1.B])
        self.I2.B.Connect([self.A2.B])
        self.A1.C.Connect([self.O1.A])
        self.A2.C.Connect([self.O1.B])
        self.O1.C.Connect([self.C])


class HalfAdder(INode):  # One bit adder, A,B in. Sum and Carry out
    def __init__(self, name):
        INode.__init__(self, name)
        self.A = ISocket(
            pNode=self,
            name="A",
            type=JCONSTANTS.SOCKET.TYPE_INPUT,
            dataType=bool,
            execOnConnect=False,
        )
        self.B = ISocket(
            pNode=self,
            name="B",
            type=JCONSTANTS.SOCKET.TYPE_INPUT,
            dataType=bool,
            execOnConnect=False,
        )
        self.S = ISocket(
            pNode=self,
            name="S",
            type=JCONSTANTS.SOCKET.TYPE_OUTPUT,
            dataType=bool,
            execOnConnect=False,
        )
        self.C = ISocket(
            pNode=self,
            name="C",
            type=JCONSTANTS.SOCKET.TYPE_OUTPUT,
            dataType=bool,
            execOnConnect=False,
        )
        self.X1 = Xor("X1")
        self.A1 = And("A1")
        self.A.Connect([self.X1.A, self.A1.A])
        self.B.Connect([self.X1.B, self.A1.B])
        self.X1.C.Connect([self.S])
        self.A1.C.Connect([self.C])


def bit(x, bit):
    return x[bit] == "1"
