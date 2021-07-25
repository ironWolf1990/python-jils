import unittest

from jigls.package.ilogic import iAnd, iNot

# https://openbookproject.net/courses/python4fun/logic.html


class TestCore(unittest.TestCase):
    def test_and(self):
        a = iAnd("A1")

        A = a.GetSocketByName("A")
        B = a.GetSocketByName("B")
        assert A is not None
        assert B is not None

        A.Set(True)
        B.Set(False)

        C = a.GetSocketByName("C")
        assert C is not None
        self.assertEqual(C.Get(), False)

    def test_and_not(self):
        a = iAnd("A1")

        A = a.GetSocketByName("A")
        B = a.GetSocketByName("B")
        assert A is not None
        assert B is not None

        A.Set(True)
        B.Set(True)

        C = a.GetSocketByName("C")
        assert C is not None
        self.assertEqual(C.Get(), True)

        n = iNot("N1")
        notA = n.GetSocketByName("A")
        assert notA

        C.Connect(notA)
        B.Set(False)

        self.assertEqual(C.Get(), False)

        notB = n.GetSocketByName("B")
        assert notB is not None
        self.assertEqual(notB.Get(), True)