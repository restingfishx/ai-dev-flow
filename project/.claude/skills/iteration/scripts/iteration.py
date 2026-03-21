#!/usr/bin/env python3
"""迭代管理脚本"""

import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# 添加 lib 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib"))

# 配置文件
CONFIG_FILE = ".ai-dev-flow/config.json"
CONFIG_DIR = ".ai-dev-flow"
ITERATION_MARKER = ".ai-dev-flow/.iteration"  # 迭代模式标识

# 根目录文件（不受迭代影响）
ROOT_FILES = [".git", "worktrees", ".ai-dev-flow"]


def ensure_config_dir():
    """确保配置目录存在"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    """保存配置文件"""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    # 创建/更新迭代模式标识文件
    create_marker()


def create_marker():
    """创建迭代模式标识文件"""
    marker_path = Path(ITERATION_MARKER)
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(f"# 迭代模式标识 - 由 iteration.py 自动管理\n")
        f.write(f"updated_at: {datetime.now().isoformat()}Z\n")


def remove_marker():
    """移除迭代模式标识文件"""
    marker_path = Path(ITERATION_MARKER)
    if marker_path.exists():
        os.remove(marker_path)


def get_current_iteration():
    """获取当前迭代"""
    config = load_config()
    if not config:
        return None
    return config.get("current_iteration")


def get_latest_iteration():
    """获取最新迭代"""
    config = load_config()
    if not config or not config.get("iterations"):
        return None
    iterations = config["iterations"]
    # 按版本号排序（简单处理 v1.0, v1.1, v2.0）
    sorted_iters = sorted(iterations, key=lambda x: x["version"], reverse=True)
    return sorted_iters[0]["version"] if sorted_iters else None


def cmd_create(version):
    """创建新迭代"""
    # 验证版本格式
    if not version.startswith("v"):
        print(f"✗ 版本号必须以 v 开头（如 v1.0）")
        return

    config = load_config()
    if config:
        # 检查版本是否已存在
        for it in config.get("iterations", []):
            if it["version"] == version:
                print(f"✗ 迭代 {version} 已存在")
                return

        # 基于最新迭代创建
        latest = get_latest_iteration()
        if latest:
            print(f"✓ 基于 {latest} 创建 {version}...")
            copy_iteration_files(latest, version)
        else:
            print(f"✓ 首次创建 {version}，从根目录复制文件...")
            copy_root_files(version)

        # 更新配置
        if "iterations" not in config:
            config["iterations"] = []
        config["iterations"].append({
            "version": version,
            "status": "in_progress",
            "created_at": datetime.now().isoformat() + "Z",
            "parent": latest
        })
        config["current_iteration"] = version
    else:
        # 首次创建
        print(f"✓ 首次创建迭代 {version}，从根目录复制文件...")
        copy_root_files(version)

        config = {
            "current_iteration": version,
            "iterations": [{
                "version": version,
                "status": "in_progress",
                "created_at": datetime.now().isoformat() + "Z",
                "parent": None
            }]
        }

    save_config(config)
    print(f"✓ 已创建迭代 {version} 并设为当前迭代")


def copy_iteration_files(from_version, to_version):
    """复制迭代文件"""
    from_dir = Path(from_version)
    to_dir = Path(to_version)

    if not from_dir.exists():
        return

    # 创建目标目录
    to_dir.mkdir(parents=True, exist_ok=True)

    # 复制非根目录的文件
    for item in from_dir.iterdir():
        if item.name in ROOT_FILES:
            continue
        dest = to_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


def copy_root_files(to_version):
    """从根目录复制文件到迭代目录"""
    to_dir = Path(to_version)
    to_dir.mkdir(parents=True, exist_ok=True)

    # 复制常见文档目录和文件
    items_to_copy = ["docs", "tasks.json", "subtasks"]
    for item_name in items_to_copy:
        item = Path(item_name)
        if item.exists():
            dest = to_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)


def cmd_list():
    """列出所有迭代"""
    config = load_config()
    if not config:
        print("暂无迭代")
        return

    current = config.get("current_iteration")
    print("迭代列表:")
    print("-" * 50)

    for it in config.get("iterations", []):
        version = it["version"]
        status = it.get("status", "unknown")
        marker = "→" if version == current else " "
        status_icon = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅"
        }.get(status, "?")

        print(f"  {marker} {status_icon} {version} [{status}]")

        if it.get("parent"):
            print(f"      来自: {it['parent']}")


def cmd_switch(version):
    """切换当前迭代"""
    config = load_config()
    if not config:
        print("✗ 配置文件不存在，请先创建迭代")
        return

    # 检查版本是否存在
    found = False
    for it in config.get("iterations", []):
        if it["version"] == version:
            found = True
            if it.get("status") == "completed":
                print(f"⚠ 迭代 {version} 已完成，切换后将无法修改")
            break

    if not found:
        print(f"✗ 迭代 {version} 不存在")
        return

    config["current_iteration"] = version
    save_config(config)
    print(f"✓ 已切换到迭代 {version}")


def cmd_complete(version=None):
    """完成迭代"""
    config = load_config()
    if not config:
        print("✗ 配置文件不存在")
        return

    # 如果未指定版本，使用当前迭代
    if not version:
        version = config.get("current_iteration")
        if not version:
            print("✗ 当前没有活跃迭代")
            return

    # 检查版本是否存在
    found = False
    for it in config.get("iterations", []):
        if it["version"] == version:
            it["status"] = "completed"
            it["completed_at"] = datetime.now().isoformat() + "Z"
            found = True
            break

    if not found:
        print(f"✗ 迭代 {version} 不存在")
        return

    save_config(config)
    print(f"✓ 已完成迭代 {version}")


def cmd_status():
    """查看当前迭代状态"""
    config = load_config()
    marker_path = Path(ITERATION_MARKER)

    if not config:
        print("当前未启用迭代模式")
        print(f"标识文件: {ITERATION_MARKER} {'✓' if marker_path.exists() else '✗'}")
        print("使用 /iteration create v1.0 创建首个迭代")
        return

    current = config.get("current_iteration")
    print(f"当前迭代: {current}")
    print(f"配置文件: {CONFIG_FILE}")
    print(f"标识文件: {ITERATION_MARKER} {'✓' if marker_path.exists() else '✗'}")
    print()

    # 迭代详情
    print("迭代详情:")
    for it in config.get("iterations", []):
        if it["version"] == current:
            status = it.get("status", "unknown")
            status_icon = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅"
            }.get(status, "?")
            print(f"  状态: {status_icon} {status}")
            print(f"  创建时间: {it.get('created_at', 'N/A')}")
            if it.get("completed_at"):
                print(f"  完成时间: {it['completed_at']}")
            if it.get("parent"):
                print(f"  来自: {it['parent']}")


def usage():
    print("""迭代管理

用法:
  python iteration.py create <version>    创建迭代
  python iteration.py list                  列出所有迭代
  python iteration.py switch <version>     切换当前迭代
  python iteration.py complete [version]   完成迭代
  python iteration.py status               查看当前状态

示例:
  python iteration.py create v1.0
  python iteration.py create v1.1
  python iteration.py list
  python iteration.py switch v1.0
  python iteration.py complete v1.0
  python iteration.py status
""")


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "create":
        if len(sys.argv) < 3:
            print("用法: python iteration.py create <version>")
            sys.exit(1)
        cmd_create(sys.argv[2])

    elif cmd == "list":
        cmd_list()

    elif cmd == "switch":
        if len(sys.argv) < 3:
            print("用法: python iteration.py switch <version>")
            sys.exit(1)
        cmd_switch(sys.argv[2])

    elif cmd == "complete":
        cmd_complete(sys.argv[2] if len(sys.argv) > 2 else None)

    elif cmd == "status":
        cmd_status()

    else:
        print(f"未知命令: {cmd}")
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
