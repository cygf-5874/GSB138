"""editdist 既有用例（unittest）。

起点：本文件全部通过 —— 只覆盖 **`e == o` 的线性间隙**与短串，且**不**对并列最优时的
具体脚本下断言。**勿改本文件。**
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))

from editdist import SUB_COST, align, distance  # noqa: E402


class LegacyTests(unittest.TestCase):
    def test_sub_cost_constant(self):
        self.assertEqual(SUB_COST, 1)

    def test_identical(self):
        self.assertEqual(distance("kitten", "kitten", 1, 1), 0)

    def test_classic_kitten_sitting(self):
        self.assertEqual(distance("kitten", "sitting", 1, 1), 3)

    def test_two_substitutions(self):
        self.assertEqual(distance("flaw", "lawn", 1, 1), 2)

    def test_gap_run_linear_cost(self):
        self.assertEqual(distance("abcd", "ab", 1, 1), 2)
        self.assertEqual(distance("ab", "abcd", 1, 1), 2)

    def test_symmetric_unit_cost(self):
        self.assertEqual(distance("saturday", "sunday", 1, 1), 3)
        self.assertEqual(distance("sunday", "saturday", 1, 1), 3)

    def test_default_costs(self):
        self.assertEqual(distance("abc", "abc"), 0)
        self.assertEqual(distance("abc", "abd"), 1)

    def test_align_returns_cost_and_script(self):
        cost, script = align("abc", "abd", 1, 1)
        self.assertEqual(cost, 1)
        self.assertIsInstance(script, str)
        # 脚本必须是一段合法对齐：每列消耗 a 与/或 b 各一字符。
        self.assertEqual(script.count("m") + script.count("s") + script.count("d"), len("abc"))
        self.assertEqual(script.count("m") + script.count("s") + script.count("i"), len("abd"))

    def test_distance_matches_align(self):
        for a, b in (("kitten", "sitting"), ("flaw", "lawn"), ("abcdef", "abxd")):
            cost, _script = align(a, b, 1, 1)
            self.assertEqual(distance(a, b, 1, 1), cost)


if __name__ == "__main__":
    unittest.main(verbosity=2)