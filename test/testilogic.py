import unittest

from jigls.packages.ilogic import iAnd, iNot

# https://openbookproject.net/courses/python4fun/logic.html


class TestCore(unittest.TestCase):
    def test_and(self):
        a = iAnd("A1")
        a.GetSocketByName("A").Set(True)
        a.GetSocketByName("B").Set(False)

        self.assertEqual(a.GetSocketByName("C").Get(), False)

    def test_and_not(self):
        a = iAnd("A1")
        a.GetSocketByName("A").Set(True)
        a.GetSocketByName("B").Set(True)

        self.assertEqual(a.GetSocketByName("C").Get(), True)

        n = iNot("N1")
        notA = n.GetSocketByName("A")
        assert notA

        a.GetSocketByName("C").Connect(notA)
        a.GetSocketByName("B").Set(False)

        self.assertEqual(a.GetSocketByName("C").Get(), False)
        self.assertEqual(n.GetSocketByName("B").Get(), True)