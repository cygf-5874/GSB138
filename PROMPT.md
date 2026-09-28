带仿射间隙的距离算出来偏小。editdist 是 Python 3 的编辑距离库（仅标准库，unittest），自检走 `scripts/check.sh`（`check/` 是固定验收程序，别改），既有用例走 `python tests/run.py`。

`src/editdist.py` 里 `distance` / `align` 已经能跑，既有用例全绿，但算出来的代价与编辑脚本在仿射间隙下不对，`python repro.py` 能把现象复现出来。

任务：把 `src/editdist.py` 修到满足 README「对外契约」一节的 8 条全部语义（脚本字符、仿射间隙代价模型、脚本与代价自洽、并列最优时的确定性、空串与全插入/全删除边界、代价对称性、大输入的空间），既有用例保持全绿，让固定件全过。

验收：
- python -m py_compile src/editdist.py 退出码 0；
- python tests/run.py 全绿；
- bash scripts/check.sh 退出码 0，8 个场景全过（cost 3 + path 2 + edge 2 + determinism 1）。

约束：
1. 不改 `check/`；可以新增模块。
2. 对外函数名与签名不许改；`tests/run.py` 里的用例一条都不许删或改。
3. 只许用 Python 标准库，不许引入任何第三方依赖。
4. 结果不许依赖 list/dict/set 迭代顺序或任何随机源。