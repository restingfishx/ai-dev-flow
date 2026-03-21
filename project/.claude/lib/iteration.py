#!/usr/bin/env python3
"""迭代模式路径解析模块

提供迭代模式下的路径解析功能，使各流程能在当前迭代目录下工作。
无配置文件时返回原始路径（向后兼容）。
"""

import json
import os
from pathlib import Path

# 配置文件路径
CONFIG_FILE = ".ai-dev-flow/config.json"
ITERATION_MARKER = ".ai-dev-flow/.iteration"  # 迭代模式标识文件
ROOT_FILES = [".git", "worktrees", ".ai-dev-flow"]


def get_config_path():
    """获取配置文件路径"""
    # 从项目根目录向上查找配置文件
    current = Path.cwd()
    while current != current.parent:
        config_path = current / CONFIG_FILE
        if config_path.exists():
            return config_path
        current = current.parent
    return None


def load_config():
    """加载配置文件"""
    config_path = get_config_path()
    if not config_path:
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def get_current_iteration():
    """获取当前迭代版本

    Returns:
        str: 当前迭代版本（如 "v1.0"），无配置时返回 None
    """
    config = load_config()
    if not config:
        return None
    return config.get("current_iteration")


def is_root_file(path):
    """检查路径是否为根目录文件（不受迭代影响）

    Args:
        path: 要检查的路径

    Returns:
        bool: 是否为根目录文件
    """
    # 处理字符串路径
    if isinstance(path, str):
        path = Path(path)

    # 根目录文件（不带迭代前缀）
    root_files = ROOT_FILES
    return path.parts[0] in root_files if path.parts else False


def is_absolute_path(path):
    """检查是否为绝对路径"""
    if isinstance(path, str):
        return os.path.isabs(path)
    return path.is_absolute()


def resolve_path(relative_path):
    """解析带迭代前缀的路径

    如果存在当前迭代，自动添加迭代目录前缀。
    无迭代配置时返回原始路径。

    Args:
        relative_path: 相对路径（如 "docs/prd.md"）

    Returns:
        str: 解析后的路径（如 "v1.0/docs/prd.md"）
    """
    # 绝对路径、根目录文件、已带迭代前缀的直接返回
    if is_absolute_path(relative_path):
        return relative_path

    path = Path(relative_path)

    # 根目录文件直接返回
    if is_root_file(path):
        return relative_path

    # 已带迭代前缀的直接返回
    if path.parts and path.parts[0].startswith("v"):
        return relative_path

    # 获取当前迭代
    current_iteration = get_current_iteration()
    if not current_iteration:
        return relative_path

    # 拼接迭代路径
    return str(Path(current_iteration) / relative_path)


def get_tasks_file():
    """获取 tasks.json 路径

    Returns:
        str: tasks.json 路径（如 "v1.0/tasks.json"）
    """
    return resolve_path("tasks.json")


def get_docs_dir():
    """获取 docs 目录路径

    Returns:
        str: docs 目录路径（如 "v1.0/docs"）
    """
    return resolve_path("docs")


def get_subtasks_dir():
    """获取 subtasks 目录路径

    Returns:
        str: subtasks 目录路径（如 "v1.0/subtasks"）
    """
    return resolve_path("subtasks")


def get_worktrees_dir():
    """获取 worktrees 目录路径

    Returns:
        str: worktrees 目录路径
    """
    return "worktrees"


def get_root_files():
    """获取根目录文件列表

    Returns:
        list: 不受迭代影响的根目录文件列表
    """
    return ROOT_FILES


def is_iteration_mode():
    """检查是否处于迭代模式

    检查方式：
    1. 标识文件存在（.ai-dev-flow/.iteration）
    2. 配置文件存在且有 current_iteration

    Returns:
        bool: 是否处于迭代模式
    """
    # 检查标识文件
    marker_path = Path(ITERATION_MARKER)
    if marker_path.exists():
        return True

    # 检查配置文件
    return get_current_iteration() is not None


def get_iteration_status():
    """获取迭代状态的详细信息

    Returns:
        dict: 包含 is_active, current_iteration, version_list 等信息
    """
    config = load_config()
    marker_path = Path(ITERATION_MARKER)

    if not config:
        return {
            "is_active": False,
            "current_iteration": None,
            "marker_exists": marker_path.exists(),
            "config_exists": False,
            "versions": []
        }

    return {
        "is_active": is_iteration_mode(),
        "current_iteration": config.get("current_iteration"),
        "marker_exists": marker_path.exists(),
        "config_exists": True,
        "versions": [it["version"] for it in config.get("iterations", [])]
    }


def list_iterations():
    """列出所有迭代

    Returns:
        list: 迭代列表
    """
    config = load_config()
    if not config:
        return []
    return config.get("iterations", [])


# === 便捷函数：检查文件/目录 ===

def check_file_exists(relative_path):
    """检查文件是否存在（自动解析路径）

    Args:
        relative_path: 相对路径

    Returns:
        bool: 文件是否存在
    """
    resolved = resolve_path(relative_path)
    return Path(resolved).exists()


def check_dir_exists(relative_path):
    """检查目录是否存在（自动解析路径）

    Args:
        relative_path: 相对路径

    Returns:
        bool: 目录是否存在
    """
    resolved = resolve_path(relative_path)
    path = Path(resolved)
    return path.exists() and path.is_dir()


# === 便捷函数：获取特定文件/目录路径 ===

def get_prd_path():
    """获取 PRD 文档路径

    Returns:
        str: PRD 文档路径
    """
    return resolve_path("docs/prd.md")


def get_architecture_dir():
    """获取架构目录路径

    Returns:
        str: 架构目录路径
    """
    return resolve_path("docs/architecture")


def get_design_dir():
    """获取设计目录路径

    Returns:
        str: 设计目录路径
    """
    return resolve_path("docs/design")


def get_tasks_path():
    """获取任务清单路径

    Returns:
        str: 任务清单路径
    """
    return resolve_path("tasks.json")


# === 输出函数：用于 CLI 调用 ===

def cmd_check():
    """检查当前迭代状态和路径（供 CLI 调用）"""
    print("=== 迭代状态检查 ===")
    print(f"迭代模式: {'是' if is_iteration_mode() else '否'}")
    print(f"当前版本: {get_current_iteration() or 'N/A'}")
    print()
    print("=== 关键路径 ===")
    print(f"PRD: {get_prd_path()}")
    print(f"架构目录: {get_architecture_dir()}")
    print(f"设计目录: {get_design_dir()}")
    print(f"任务清单: {get_tasks_path()}")
    print()
    print("=== 文件检查 ===")
    print(f"PRD 存在: {'✓' if check_file_exists('docs/prd.md') else '✗'}")
    print(f"架构目录存在: {'✓' if check_dir_exists('docs/architecture') else '✗'}")
    print(f"设计目录存在: {'✓' if check_dir_exists('docs/design') else '✗'}")
    print(f"任务清单存在: {'✓' if check_file_exists('tasks.json') else '✗'}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        cmd_check()
    else:
        print("用法: python iteration.py check")
        print("显示当前迭代状态和关键路径信息")
