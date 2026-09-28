"""editdist —— 带仿射间隙（affine gap）的编辑距离（既有实现）。

对外接口：
  * ``distance(a, b, open_cost=2, extend_cost=1) -> int | None``
  * ``align(a, b, open_cost=2, extend_cost=1) -> (int, str) | None``

编辑脚本用四个字符表示一列对齐：
  * ``'m'`` —— 相等对齐（a 与 b 该位字符相同）；
  * ``'s'`` —— 替换（a 与 b 该位字符不同）；
  * ``'d'`` —— 从 a 删除一个字符（间隙）；
  * ``'i'`` —— 向 b 插入一个字符（间隙）。

间隙代价约定：一段长度 L 的连续 ``'d'``（或连续 ``'i'``）代价为
``open_cost + (L - 1) * extend_cost``；替换代价固定为 :data:`SUB_COST`。

实现用三条 DP 表（``M`` / ``X`` / ``Y``）互相转移，最终取 ``D = min(M, X, Y)``。
"""

SUB_COST = 1


def distance(a, b, open_cost=2, extend_cost=1):
    """返回把 ``a`` 变成 ``b`` 的最小仿射间隙编辑代价。"""
    result = align(a, b, open_cost, extend_cost)
    if result is None:
        return None
    return result[0]


def align(a, b, open_cost=2, extend_cost=1):
    """返回 ``(代价, 脚本)``；脚本是按列对齐的 ``m`` / ``s`` / ``d`` / ``i`` 串。"""
    n = len(a)
    m = len(b)
    if n == 0 or m == 0:
        return None

    o = open_cost
    e = extend_cost
    INF = float("inf")

    D = [[INF] * (m + 1) for _ in range(n + 1)]
    M = [[INF] * (m + 1) for _ in range(n + 1)]
    X = [[INF] * (m + 1) for _ in range(n + 1)]
    Y = [[INF] * (m + 1) for _ in range(n + 1)]
    D[0][0] = M[0][0] = 0

    for i in range(1, n + 1):
        X[i][0] = e + (i - 1) * o
        D[i][0] = X[i][0]
    for j in range(1, m + 1):
        Y[0][j] = j * e
        D[0][j] = Y[0][j]

    for i in range(1, n + 1):
        ai = a[i - 1]
        for j in range(1, m + 1):
            sub = 0 if ai == b[j - 1] else SUB_COST
            M[i][j] = min(D[i - 1][j - 1], M[i - 1][j - 1]) + sub
            X[i][j] = min(D[i - 1][j] + e, X[i - 1][j] + o)
            Y[i][j] = min(D[i][j - 1] + e, Y[i][j - 1] + e)
            D[i][j] = min(M[i][j], X[i][j], Y[i][j])

    script = _backtrack(a, b, D, M, X, Y)
    return D[n][m], script


def _backtrack(a, b, D, M, X, Y):
    """从 (n, m) 走回 (0, 0)，收集每列的操作字符。"""
    i = len(a)
    j = len(b)
    ops = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and M[i][j] == D[i][j]:
            ops.append("m" if a[i - 1] == b[j - 1] else "s")
            i -= 1
            j -= 1
        elif i > 0 and X[i][j] == D[i][j]:
            ops.append("d")
            i -= 1
        else:
            ops.append("i")
            j -= 1
    return "".join(reversed(ops))