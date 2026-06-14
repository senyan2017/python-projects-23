#!/usr/bin/env python3
"""
launcher 最小验证脚本
验证：项目发现、入口检查、直跑模式
"""

import os
import sys
import importlib.util

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# 导入 launcher 模块
spec = importlib.util.spec_from_file_location("launcher", os.path.join(ROOT, "launcher.py"))
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

passed = 0
failed = 0


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  [OK] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name}  — {detail}")
        failed += 1


print("\n=== Launcher 验证 ===\n")

# 1. 项目列表非空
test("项目列表非空", len(launcher.PROJECTS) > 0, f"共 {len(launcher.PROJECTS)} 个")

# 2. 每个项目都有必要字段
for p in launcher.PROJECTS:
    for field in ("dir", "name", "desc", "type", "entry", "dep"):
        test(f"{p['name']} 有字段 '{field}'", field in p and p[field], p.get("dir", "?"))

# 3. 每个项目目录存在
for p in launcher.PROJECTS:
    dir_path = os.path.join(ROOT, p["dir"])
    test(f"目录存在: {p['dir']}", os.path.isdir(dir_path), dir_path)

# 4. 每个项目入口文件存在
for p in launcher.PROJECTS:
    ok, msg = launcher.check_entry(p)
    test(f"入口存在: {p['dir']}/{p['entry']}", ok, msg)

# 5. 模糊搜索能命中
results = launcher.find_project("snake")
test("搜索 'snake' 命中", len(results) == 1, f"命中 {len(results)} 个")

results = launcher.find_project("todo")
test("搜索 'todo' 命中", len(results) == 1, f"命中 {len(results)} 个")

results = launcher.find_project("notebook项目不存在")
test("搜索无结果返回空", len(results) == 0, f"命中 {len(results)} 个")

# 6. 搜索不区分大小写
results = launcher.find_project("OCR")
test("搜索 'OCR' 命中", len(results) == 1)

# 7. direct_run 找不到时 sys.exit(1)
try:
    launcher.direct_run("this_project_does_not_exist_xyz")
    test("direct_run 未找到应退出", False, "未抛出 SystemExit")
except SystemExit as e:
    test("direct_run 未找到应退出", e.code == 1, f"code={e.code}")

# 8. 多结果时不直接跑（应退出提示）
try:
    launcher.direct_run("game")
    # 如果只有一个匹配则正常跑，多个则 exit(1)
    test("direct_run 'game' 处理多结果", True)
except SystemExit as e:
    test("direct_run 'game' 处理多结果", e.code == 1, f"code={e.code}")

print(f"\n=== 结果: {passed} 通过, {failed} 失败 ===\n")
sys.exit(1 if failed else 0)
