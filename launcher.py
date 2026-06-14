#!/usr/bin/env python3
"""
Project Launcher - 统一入口，从根目录浏览并启动各子项目。

用法:
    python launcher.py              # 交互式菜单
    python launcher.py <关键词>     # 直接启动匹配的项目
    python launcher.py --list       # 仅列出所有项目
"""

import os
import sys
import subprocess
import importlib.util

# ── 项目注册表 ─────────────────────────────────────────────────────
# 每个项目: (目录名, 显示名, 用途说明, 入口类型, 入口文件, 依赖状态)
#   入口类型: "script" | "notebook" | "gui"
#   依赖状态: "light" (标准库/常见) | "heavy" (需额外安装) | "special" (环境要求特殊)

PROJECTS = [
    {
        "dir": "todo_app",
        "name": "Todo App",
        "desc": "命令行待办事项管理（增删改查）",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
    {
        "dir": "expense_tracker_project",
        "name": "Expense Tracker",
        "desc": "个人支出记录与统计",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
    {
        "dir": "AI Snake Game",
        "name": "AI Snake Game",
        "desc": "基于 AI 的贪吃蛇游戏",
        "type": "gui",
        "entry": "main.py",
        "dep": "heavy",
    },
    {
        "dir": "Youtube-video-downloader-project",
        "name": "YouTube Downloader",
        "desc": "YouTube 视频下载工具（GUI）",
        "type": "gui",
        "entry": "main.py",
        "dep": "heavy",
    },
    {
        "dir": "Python-OCR",
        "name": "Python OCR",
        "desc": "图片文字识别（OCR）",
        "type": "script",
        "entry": "main.py",
        "dep": "heavy",
    },
    {
        "dir": "Car-game-project",
        "name": "Car Game",
        "desc": "命令行文字驾驶小游戏",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
    {
        "dir": "Check-your-weight-project",
        "name": "Weight Checker",
        "desc": "BMI / 体重健康评估",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
    {
        "dir": "gif_generator",
        "name": "GIF Generator",
        "desc": "图片序列合成 GIF",
        "type": "script",
        "entry": "main.py",
        "dep": "heavy",
    },
    {
        "dir": "hagman-game-project",
        "name": "Hangman Game",
        "desc": "经典猜字母 Hangman 游戏",
        "type": "script",
        "entry": "Hangman-Game.py",
        "dep": "light",
    },
    {
        "dir": "Heart-disease-prediction-project",
        "name": "Heart Disease Prediction",
        "desc": "心脏病预测（Jupyter Notebook，含数据集）",
        "type": "notebook",
        "entry": "main.ipynb",
        "dep": "heavy",
    },
    {
        "dir": "life-game",
        "name": "Game of Life",
        "desc": "Conway 生命游戏模拟",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
    {
        "dir": "LoanPricePredictor",
        "name": "Loan Price Predictor",
        "desc": "贷款价格预测（Jupyter Notebook）",
        "type": "notebook",
        "entry": "main.ipynb",
        "dep": "heavy",
    },
    {
        "dir": "Morsecode-project",
        "name": "Morse Code",
        "desc": "摩尔斯电码编解码工具",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
    {
        "dir": "Music-Playlist-Generator",
        "name": "Music Playlist Generator",
        "desc": "音乐播放列表生成器（Jupyter Notebook）",
        "type": "notebook",
        "entry": "main.ipynb",
        "dep": "heavy",
    },
    {
        "dir": "object-detection",
        "name": "Object Detection",
        "desc": "目标检测（需摄像头 + OpenCV）",
        "type": "script",
        "entry": "main.py",
        "dep": "special",
    },
    {
        "dir": "Pattern",
        "name": "Pattern Printer",
        "desc": "各种字符图案打印",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
    {
        "dir": "Shape-project",
        "name": "Shape Drawer",
        "desc": "几何图形绘制（turtle 或文本）",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
    {
        "dir": "Tic-Tac-Toe-project",
        "name": "Tic-Tac-Toe",
        "desc": "井字棋游戏",
        "type": "script",
        "entry": "main.py",
        "dep": "light",
    },
]

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── 工具函数 ────────────────────────────────────────────────────────

DEP_LABELS = {
    "light": "[依赖轻]",
    "heavy": "[依赖重]",
    "special": "[环境特殊]",
}

TYPE_LABELS = {
    "script": "脚本",
    "notebook": "Notebook",
    "gui": "GUI 程序",
}


def print_header():
    print()
    print("=" * 62)
    print("        Project Launcher  —  选择项目即可运行")
    print("=" * 62)


def print_project_table(projects):
    """以表格形式打印项目列表。"""
    print()
    print(f"  {'序号':<5} {'项目名':<26} {'用途':<30} {'类型':<10} {'状态'}")
    print("  " + "-" * 88)
    for i, p in enumerate(projects, 1):
        dep_tag = DEP_LABELS.get(p["dep"], "")
        type_tag = TYPE_LABELS.get(p["type"], p["type"])
        print(f"  {i:<5} {p['name']:<26} {p['desc']:<30} {type_tag:<10} {dep_tag}")


def find_project(keyword):
    """模糊匹配项目（目录名 / 显示名 / 描述），返回匹配列表。"""
    kw = keyword.lower()
    results = []
    for p in PROJECTS:
        haystack = f"{p['dir']} {p['name']} {p['desc']}".lower()
        if kw in haystack:
            results.append(p)
    return results


def check_entry(p):
    """检查入口文件是否存在，返回 (ok, message)。"""
    path = os.path.join(ROOT, p["dir"], p["entry"])
    if not os.path.isfile(path):
        return False, f"入口文件缺失: {path}"
    return True, path


def warn_dependencies(p):
    """对 heavy/special 项目给出警告提示。"""
    if p["dep"] == "heavy":
        print(f"\n  [!] 注意: {p['name']} 依赖较重，请确保已安装所需包:")
        req_file = os.path.join(ROOT, p["dir"], "requirements.txt")
        if os.path.isfile(req_file):
            print(f"      pip install -r {os.path.relpath(req_file, ROOT)}")
        else:
            print("      请查看项目目录中的依赖说明。")
    elif p["dep"] == "special":
        print(f"\n  [!] 注意: {p['name']} 有特殊环境要求（如硬件/系统库），")
        print("      请确认环境就绪后再运行。")


def run_project(p):
    """启动指定项目。"""
    ok, msg = check_entry(p)
    if not ok:
        print(f"\n  [x] {msg}")
        return

    entry_path = msg
    project_dir = os.path.join(ROOT, p["dir"])

    if p["type"] == "notebook":
        print(f"\n  启动 Jupyter Notebook: {os.path.relpath(entry_path, ROOT)}")
        print("  (如果未安装 jupyter，请先: pip install jupyter)\n")
        cmd = [sys.executable, "-m", "jupyter", "notebook", entry_path]
    else:
        print(f"\n  运行: {os.path.relpath(entry_path, ROOT)}")
        cmd = [sys.executable, entry_path]

    warn_dependencies(p)
    print()

    try:
        subprocess.run(cmd, cwd=project_dir)
    except FileNotFoundError:
        print(f"\n  [x] 无法启动，请确认 Python 环境正确。")
    except KeyboardInterrupt:
        print("\n  (项目已中断)")


# ── 交互式菜单 ──────────────────────────────────────────────────────

def interactive_menu():
    """主交互循环。"""
    while True:
        print_header()
        print_project_table(PROJECTS)
        print()
        print("  输入 序号 运行项目 | 输入 q 退出 | 输入 r 返回此菜单")
        print()

        try:
            choice = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  再见！")
            break

        if not choice:
            continue
        if choice.lower() in ("q", "quit", "exit"):
            print("  再见！")
            break
        if choice.lower() == "r":
            continue

        # 数字选择
        try:
            idx = int(choice)
        except ValueError:
            # 尝试模糊搜索
            results = find_project(choice)
            if len(results) == 1:
                run_project(results[0])
                input("\n  按 Enter 返回菜单...")
                continue
            elif len(results) > 1:
                print(f"\n  找到 {len(results)} 个匹配项目:")
                for i, p in enumerate(results, 1):
                    print(f"    {i}. {p['name']} — {p['desc']}")
                print("  请输入更精确的关键词或序号。")
                input("\n  按 Enter 返回菜单...")
                continue
            else:
                print(f"\n  [x] 无效输入 '{choice}'，请输入序号或 q 退出。")
                input("\n  按 Enter 返回菜单...")
                continue

        if 1 <= idx <= len(PROJECTS):
            run_project(PROJECTS[idx - 1])
            input("\n  按 Enter 返回菜单...")
        else:
            print(f"\n  [x] 序号超出范围，请输入 1-{len(PROJECTS)}。")
            input("\n  按 Enter 返回菜单...")


# ── 命令行直跑 ──────────────────────────────────────────────────────

def direct_run(keyword):
    """根据关键词直接运行项目。"""
    results = find_project(keyword)
    if not results:
        print(f"\n  [x] 未找到匹配 '{keyword}' 的项目。")
        print("  运行 python launcher.py --list 查看所有项目。\n")
        sys.exit(1)
    elif len(results) == 1:
        run_project(results[0])
    else:
        print(f"\n  找到 {len(results)} 个匹配项目，请更精确:")
        for p in results:
            print(f"    - {p['name']}  ({p['dir']})")
        print()
        sys.exit(1)


def list_projects():
    """列出所有项目。"""
    print_project_table(PROJECTS)
    print()


# ── 入口 ────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args:
        interactive_menu()
    elif args[0] in ("--list", "-l"):
        list_projects()
    elif args[0] in ("--help", "-h"):
        print(__doc__)
    else:
        keyword = " ".join(args)
        direct_run(keyword)


if __name__ == "__main__":
    main()
