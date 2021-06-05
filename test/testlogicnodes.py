import unittest

from jigls.packages.logic import And, HalfAdder, Not, Xor

# https://openbookproject.net/courses/python4fun/logic.html


class TestCore(unittest.TestCase):
    def test_and(self):
        a = And("A1")
        # a.C.monitorOnChange = True
        a.A.Set(True)
        a.B.Set(True)
        self.assertEqual(a.C.Get(), True)

    def test_and_not(self):
        a = And("A1")
        # a.C.monitorOnChange = True
        a.A.Set(True)
        a.B.Set(True)
        self.assertEqual(a.C.Get(), True)

        n = Not("N1")
        a.C.Connect(n.A)
        # n.B.monitorOnChange = True
        a.B.Set(False)
        self.assertEqual(a.C.Get(), False)
        self.assertEqual(n.B.Get(), True)

    def test_xor(self):
        o1 = Xor("XOR")
        # o1.C.monitorOnChange = True
        o1.A.Set(False)
        o1.B.Set(False)
        self.assertEqual(o1.C.Get(), False)

        o1.B.Set(True)
        self.assertEqual(o1.C.Get(), True)

        o1.A.Set(True)
        self.assertEqual(o1.C.Get(), False)

    def test_halfadder(self):
        h1 = HalfAdder("H1")
        # h1.S.monitorOnChange = True
        # h1.C.monitorOnChange = True
        h1.A.Set(False)
        self.assertEqual(h1.C.Get(), False)

        h1.B.Set(False)
        self.assertEqual(h1.S.Get(), False)

        h1.B.Set(True)
        self.assertEqual(h1.S.Get(), True)

        h1.A.Set(True)
        self.assertEqual(h1.S.Get(), False)
        self.assertEqual(h1.C.Get(), True)
