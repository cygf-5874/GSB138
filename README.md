# editdist

Python 3 的**带仿射间隙（affine gap）编辑距离**库。既有实现能跑，
但算出来的距离与脚本在若干情形下不对；本次要把它**修对**。

- 语言/依赖：Python 3（标准库，`unittest`），**无第三方依赖**。
- 入口：`src/editdist.py`。
- 自检：`bash scripts/check.sh`（`check/` 是固定验收程序，**勿改**）。
- 既有用例：`python tests/run.py`（unittest，当前全绿）。
- 复现脚本：`python repro.py`（可运行，打印可观察到的症状）。

## 用法

```bash
python tests/run.py                 # 既有用例
python repro.py                     # 复现现象
bash scripts/check.sh               # 固定验收（加 -list / --only <组名> 可过滤）
```

对外接口（签名**不许改**）：

- `distance(a, b, open_cost=2, extend_cost=1) -> int`
  —— 把 `a` 变成 `b` 的最小仿射间隙编辑代价。
- `align(a, b, open_cost=2, extend_cost=1) -> tuple[int, str]`
  —— 返回 `(代价, 编辑脚本)`。
- 模块常量 `SUB_COST = 1`（单字符替换代价）。

**编辑脚本**是一串字符，一列对齐一个字符：

- `m` —— 相等对齐（该列 `a` 与 `b` 的字符相同）；
- `s` —— 替换（该列 `a` 与 `b` 的字符不同），代价 `SUB_COST`；
- `d` —— 从 `a` 删除一个字符（间隙）；
- `i` —— 向 `b` 插入一个字符（间隙）。

**仿射间隙代价**：一段长度 `L` 的连续同类间隙（连续 `d` 或连续 `i`）代价为
`open_cost + (L - 1) * extend_cost`；`L == 0` 不计。`0 < extend_cost < open_cost`。

## 对外契约

1. `align(a, b, o, e)` 返回 `(代价, 脚本)`，`distance(a, b, o, e)` 返回其中的**代价**；
   两者对同一输入必须一致（`distance(...) == align(...)[0]`）。
2. 间隙代价按仿射模型：一段长度 `L >= 1` 的连续间隙 = `o + (L - 1) * e`，其中
   `o = open_cost`、`e = extend_cost`，且 `0 < e < o`；替换代价固定 `SUB_COST == 1`。
3. **脚本与代价自洽**：把 `align` 返回的脚本按上述代价模型**重新计价**，结果必须等于
   返回的代价；且脚本必须是一段合法对齐（把 `a` 逐列变成 `b`）。
4. 并列最优（存在多条同代价最优脚本）时，返回**字典序最小**的那一条；
   比较按脚本字符的 ASCII 码序（`'d' < 'i' < 'm' < 's'`）。同一输入多次调用结果相同。
5. 边界情形必须给出正确结果，不得返回 `None`：
   空串对空串代价为 `0`、脚本为 `""`；全删除（`b == ""`）用 `'d'` 串、全插入（`a == ""`）用 `'i'` 串。
6. **对称性**：代价满足 `distance(a, b, o, e) == distance(b, a, o, e)`（脚本不要求对称）。
7. 结果只由输入决定，与实现内部容器（`list`/`dict`/`set`）的迭代或存储顺序无关。
8. 时间 `O(n·m)`；空间可裁剪到 `O(min(n, m))`，较大的输入不得爆内存。

## 目录

```
src/editdist.py     库代码（既有实现，存在缺陷）
tests/run.py        既有用例（unittest，全绿；只覆盖 e == o 的线性间隙与短串）
repro.py            复现脚本（可运行）
check/check.py      固定验收程序（8 个场景，勿改）
scripts/check.sh    自检入口
```