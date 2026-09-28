#!/usr/bin/env python3
"""editdist 固定验收程序（固定件）。

用法（在仓库根目录）：
  python check/check.py            跑全部场景
  python check/check.py -list      列出全部 `组/名`
  python check/check.py --only <组> 只跑某一组

输出：逐场景 `PASS <组>/<名>` 或 `FAIL <组>/<名>  期望=… 实际=…`，
结尾 `结果：通过 x/N`；全过 exit 0，否则 exit 1；失败不早退。
判据只描述对外可见性质（代价、脚本、对称性、边界），不使用墙钟 / 随机源，
也不依赖 list / dict / set 的迭代顺序。
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, os.pardir, "src"))

from editdist import align, distance  # noqa: E402


def show(value):
    text = repr(value)
    return text if len(text) <= 220 else text[:220] + "…"


def expect_equal(expected, actual, label):
    if expected != actual:
        raise AssertionError("%s：期望=%s 实际=%s" % (label, show(expected), show(actual)))


def expect_true(cond, label, actual):
    if not cond:
        raise AssertionError("%s：实际=%s" % (label, show(actual)))


def replay_cost(script, open_cost, extend_cost):
    """按 README 的仿射间隙模型给脚本重新计价（与库实现无关）。"""
    total = 0
    prev = None
    for op in script:
        if op == "s":
            total += 1
        elif op in ("d", "i"):
            total += open_cost if prev != op else extend_cost
        elif op == "m":
            pass
        else:
            raise AssertionError("脚本含非法字符 %r" % (op,))
        prev = op
    return total


def expect_valid_alignment(a, b, script, label):
    """校验脚本是一段合法对齐：逐列把 a 变成 b，`m` 列字符必须相等。"""
    i = j = 0
    for op in script:
        if op == "m":
            expect_true(i < len(a) and j < len(b) and a[i] == b[j],
                        label + " 的 'm' 列字符应相等", (a, b, script))
            i += 1
            j += 1
        elif op == "s":
            i += 1
            j += 1
        elif op == "d":
            i += 1
        elif op == "i":
            j += 1
        else:
            raise AssertionError("%s：脚本含非法字符 %r" % (label, op))
    expect_equal(len(a), i, label + " 脚本消耗 a 的长度")
    expect_equal(len(b), j, label + " 脚本消耗 b 的长度")


def sc_cost_opening_vs_extending():
    # 长度 1 的间隙按 open_cost 计，不是 extend_cost。
    expect_equal(2, distance("a", "ab", 2, 1), "插入单个字符")
    expect_equal(2, distance("ab", "a", 2, 1), "删除单个字符")
    expect_equal(2, distance("b", "ab", 2, 1), "前缀插入单个字符")
    expect_equal(3, distance("ab", "abc", 3, 1), "open=3 时单字符间隙按 open 计")


def sc_cost_long_gap_run():
    # 一段长度 L 的间隙 = o + (L-1)*e。
    expect_equal(5, distance("x", "xyyyy", 2, 1), "长度 4 的插入间隙")
    expect_equal(5, distance("xyyyy", "x", 2, 1), "长度 4 的删除间隙")
    expect_equal(5, distance("abcdef", "ab", 2, 1), "长度 4 的尾部删除间隙")
    expect_equal(3, distance("abcde", "abc", 2, 1), "长度 2 的删除间隙")


def sc_cost_symmetry():
    fwd = distance("a", "bba", 2, 1)
    bwd = distance("bba", "a", 2, 1)
    expect_equal(3, fwd, "a -> bba")
    expect_equal(3, bwd, "bba -> a")
    expect_equal(fwd, bwd, "代价对称（a/bba）")

    fwd2 = distance("a", "bbaa", 2, 1)
    bwd2 = distance("bbaa", "a", 2, 1)
    expect_equal(4, fwd2, "a -> bbaa")
    expect_equal(4, bwd2, "bbaa -> a")
    expect_equal(fwd2, bwd2, "代价对称（a/bbaa）")


def sc_path_lexicographic_min():
    expect_equal((2, "im"), align("a", "aa", 2, 1), "并列时取字典序最小 a/aa")
    expect_equal((2, "dm"), align("aa", "a", 2, 1), "并列时取字典序最小 aa/a")
    expect_equal((2, "im"), align("b", "ab", 2, 1), "并列时取字典序最小 b/ab")
    expect_equal((3, "mdd"), align("abc", "a", 2, 1), "唯一最优 abc/a")


def sc_path_script_replay():
    for a, b in (("abc", "a"), ("kitten", "sitting"), ("abcdef", "abxd"), ("abcdef", "ab")):
        result = align(a, b, 2, 1)
        expect_true(isinstance(result, tuple) and len(result) == 2,
                    "align 应返回 (代价, 脚本) %s/%s" % (a, b), result)
        cost, script = result
        expect_true(isinstance(script, str), "脚本应为 str %s/%s" % (a, b), script)
        expect_valid_alignment(a, b, script, "对齐 %s/%s" % (a, b))
        expect_equal(cost, replay_cost(script, 2, 1), "脚本重放代价自洽 %s/%s" % (a, b))


def sc_edge_empty_pair():
    expect_equal(0, distance("", "", 2, 1), "空串对空串代价")
    expect_equal((0, ""), align("", "", 2, 1), "空串对空串脚本")


def sc_edge_all_gaps():
    expect_equal(2, distance("a", "", 2, 1), "单字符全删除")
    expect_equal(2, distance("", "a", 2, 1), "单字符全插入")
    expect_equal(4, distance("abc", "", 2, 1), "全删除长度 3")
    expect_equal(4, distance("", "abc", 2, 1), "全插入长度 3")
    expect_equal((4, "ddd"), align("abc", "", 2, 1), "全删除脚本")
    expect_equal((4, "iii"), align("", "abc", 2, 1), "全插入脚本")


def sc_determinism_stable():
    runs_a = [align("a", "aa", 2, 1) for _ in range(5)]
    expect_equal([(2, "im")] * 5, runs_a, "a/aa 多次调用结果稳定")

    runs_b = [align("aa", "a", 2, 1) for _ in range(5)]
    expect_equal([(2, "dm")] * 5, runs_b, "aa/a 多次调用结果稳定")

    expect_equal(2, distance("a", "aa", 2, 1), "distance 与稳定脚本一致")


SCENARIOS = [
    ("cost", "opening-vs-extending", "长度 1 的间隙按 open 计", sc_cost_opening_vs_extending),
    ("cost", "long-gap-run", "长间隙按 o+(L-1)e 计", sc_cost_long_gap_run),
    ("cost", "symmetry", "代价对称", sc_cost_symmetry),
    ("path", "lexicographic-min", "并列最优取字典序最小脚本", sc_path_lexicographic_min),
    ("path", "script-replay", "脚本与代价自洽且为合法对齐", sc_path_script_replay),
    ("edge", "empty-pair", "空串对空串", sc_edge_empty_pair),
    ("edge", "all-gaps", "全插入 / 全删除边界", sc_edge_all_gaps),
    ("determinism", "stable-tie-breaking", "多次调用结果确定", sc_determinism_stable),
]


def main(argv):
    list_only = "-list" in argv or "--list" in argv
    only = None
    if "--only" in argv:
        idx = argv.index("--only")
        if idx + 1 >= len(argv):
            sys.stderr.write("--only 缺少取值\n")
            return 2
        only = argv[idx + 1]

    if list_only:
        for group, name, _expect, _run in SCENARIOS:
            sys.stdout.write("%s/%s\n" % (group, name))
        return 0

    passed = 0
    ran = 0
    for group, name, expect, run in SCENARIOS:
        if only is not None and group != only:
            continue
        ran += 1
        label = "%s/%s" % (group, name)
        try:
            run()
            passed += 1
            sys.stdout.write("PASS %s\n" % label)
        except Exception as exc:  # noqa: BLE001
            detail = "%s: %s" % (type(exc).__name__, exc)
            sys.stdout.write("FAIL %s  期望=%s 实际=%s\n" % (label, expect, show(detail)))

    if ran == 0:
        sys.stdout.write("结果：通过 0/0（没有匹配的场景：--only %s）\n" % only)
        return 1

    sys.stdout.write("结果：通过 %d/%d\n" % (passed, ran))
    return 0 if passed == ran else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))