"""repro.py —— 复现 editdist 可观察到的症状（直接运行：``python repro.py``）。

本脚本只把「实际算出来的结果」与「README『对外契约』要求的期望值」并排打印出来；
它不判断、不修复，也不涉及内部实现。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from editdist import align, distance  # noqa: E402


def replay_cost(script, open_cost, extend_cost):
    """按 README 的仿射间隙模型给一段脚本重新计价。"""
    total = 0
    prev = None
    for op in script:
        if op == "s":
            total += 1
        elif op in ("d", "i"):
            total += open_cost if prev != op else extend_cost
        prev = op
    return total


# (a, b, o, e, 契约期望的代价)
COST_CASES = [
    ("a", "ab", 2, 1, 2),
    ("abc", "a", 2, 1, 3),
    ("x", "xyyyy", 2, 1, 5),
    ("a", "bba", 2, 1, 3),
    ("", "abc", 2, 1, 4),
    ("abc", "", 2, 1, 4),
]


def main():
    print("== distance ==")
    for a, b, o, e, want in COST_CASES:
        try:
            got = distance(a, b, o, e)
        except Exception as exc:  # noqa: BLE001
            got = "%s: %s" % (type(exc).__name__, exc)
        mark = "OK" if got == want else "不符"
        print("distance(%r, %r, %d, %d) = %r   （契约期望 %d）  %s" % (a, b, o, e, got, want, mark))

    print()
    print("== 代价对称性 ==")
    for a, b in (("a", "bba"), ("a", "bbaa")):
        print("distance(%r, %r) = %r   distance(%r, %r) = %r"
              % (a, b, distance(a, b, 2, 1), b, a, distance(b, a, 2, 1)))

    print()
    print("== align：代价与脚本是否自洽 ==")
    for a, b in (("abc", "a"), ("abcdef", "ab")):
        got = align(a, b, 2, 1)
        if isinstance(got, tuple):
            cost, script = got
            rc = replay_cost(script, 2, 1)
            print("align(%r, %r) = (%r, %r)  脚本重放代价 = %d  自洽 = %s"
                  % (a, b, cost, script, rc, cost == rc))
        else:
            print("align(%r, %r) = %r" % (a, b, got))


if __name__ == "__main__":
    main()