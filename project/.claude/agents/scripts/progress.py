#!/usr/bin/env python3
"""子任务进度管理脚本"""

import json
import sys
import os
from datetime import datetime

SUBTASKS_DIR = "subtasks"


def ensure_dir():
    """确保 subtasks 目录存在"""
    if not os.path.exists(SUBTASKS_DIR):
        os.makedirs(SUBTASKS_DIR)


def has_subtasks():
    """检查是否存在子任务详情文件（断点判断）"""
    if not os.path.exists(SUBTASKS_DIR):
        return False
    files = [f for f in os.listdir(SUBTASKS_DIR) if f.startswith("subtask-") and f.endswith(".json")]
    return len(files) > 0


def load_subtasks():
    """加载子任务文件（从所有 subtask-xxx.json 合并）"""
    if not has_subtasks():
        return None

    # 收集所有子任务
    all_subtasks = []
    current = 1
    if os.path.exists(SUBTASKS_DIR):
        files = sorted([f for f in os.listdir(SUBTASKS_DIR) if f.startswith("subtask-") and f.endswith(".json")])
        for f in files:
            with open(os.path.join(SUBTASKS_DIR, f), "r", encoding="utf-8") as fp:
                data = json.load(fp)
                all_subtasks.append(data)
                if data.get("status") == "in_progress":
                    current = data.get("id", 1)

    if not all_subtasks:
        return None

    return {
        "task_id": "",
        "subtasks": all_subtasks,
        "current": current
    }


def save_subtasks(data):
    """保存子任务文件（保存到各个 subtask-xxx.json）"""
    if not data or not data.get("subtasks"):
        return
    for st in data["subtasks"]:
        subtask_file = os.path.join(SUBTASKS_DIR, f"subtask-{st['id']:03d}.json")
        with open(subtask_file, "w", encoding="utf-8") as f:
            json.dump(st, f, ensure_ascii=False, indent=2)


def cmd_create(subtask_id, name, description, acceptance):
    """创建子任务详情文件"""
    ensure_dir()
    subtask_file = os.path.join(SUBTASKS_DIR, f"subtask-{subtask_id:03d}.json")
    data = {
        "id": subtask_id,
        "name": name,
        "description": description,
        "acceptance": acceptance,
        "status": "pending",
        "created_at": datetime.now().isoformat() + "Z"
    }
    with open(subtask_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ 已创建子任务详情: {subtask_file}")


def cmd_init(task_id, subtask_ids_or_names):
    """初始化子任务（从 subtasks 目录读取详情）"""
    ensure_dir()

    # 获取已有子任务数量
    existing = load_subtasks()
    if existing and existing.get("task_id") == task_id:
        start_id = len(existing["subtasks"]) + 1
    else:
        start_id = 1
        existing = None

    subtasks = []
    new_subtask_ids = []

    for i, item in enumerate(subtask_ids_or_names):
        subtask_id = start_id + i
        subtask_file = os.path.join(SUBTASKS_DIR, f"subtask-{subtask_id:03d}.json")

        # 读取详情文件（如果存在）
        detail = None
        if os.path.exists(subtask_file):
            with open(subtask_file, "r", encoding="utf-8") as f:
                detail = json.load(f)

        if detail:
            subtasks.append({
                "id": subtask_id,
                "name": detail.get("name", item),
                "status": "pending"
            })
        else:
            # 没有详情文件，使用传入的名称
            subtasks.append({
                "id": subtask_id,
                "name": item,
                "status": "pending"
            })
        new_subtask_ids.append(subtask_id)

    if existing and existing.get("task_id") == task_id:
        # 追加
        existing["subtasks"].extend(subtasks)
        existing["updated_at"] = datetime.now().isoformat() + "Z"
        save_subtasks(existing)
        print(f"✓ 已追加子任务: {task_id}")
        print(f"  原有 {start_id - 1} 个，新增 {len(subtasks)} 个")
    else:
        # 新建
        data = {
            "task_id": task_id,
            "subtasks": subtasks,
            "current": 1,
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z"
        }
        save_subtasks(data)
        print(f"✓ 已创建子任务: {task_id}")
        print(f"  共 {len(subtasks)} 个子任务")
        for i, st in enumerate(subtasks):
            print(f"  {st['id']}. {st['name']}")


def cmd_status():
    """查看进度"""
    data = load_subtasks()
    if not data:
        print("暂无子任务")
        return

    print(f"任务: {data['task_id']}")
    print(f"当前: {data.get('current', 1)}/{len(data['subtasks'])}")
    print("进度:")
    for st in data["subtasks"]:
        icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}.get(st["status"], "?")
        marker = "→" if st["id"] == data.get("current") else " "
        print(f"  {marker} {icon} {st['id']}. {st['name']}")


def cmd_next():
    """完成当前，开始下一个"""
    data = load_subtasks()
    if not data:
        print("✗ 子任务文件不存在")
        return

    current = data.get("current", 1)
    # 标记当前为完成
    for st in data["subtasks"]:
        if st["id"] == current and st["status"] != "completed":
            st["status"] = "completed"
            # 更新详情文件状态
            subtask_file = os.path.join(SUBTASKS_DIR, f"subtask-{current:03d}.json")
            if os.path.exists(subtask_file):
                with open(subtask_file, "r", encoding="utf-8") as f:
                    detail = json.load(f)
                detail["status"] = "completed"
                with open(subtask_file, "w", encoding="utf-8") as f:
                    json.dump(detail, f, ensure_ascii=False, indent=2)
            break

    # 找下一个未完成的
    remaining = [st for st in data["subtasks"] if st["status"] != "completed"]
    if remaining:
        next_id = remaining[0]["id"]
        data["current"] = next_id
        for st in data["subtasks"]:
            if st["id"] == next_id:
                st["status"] = "in_progress"
                break
        # 更新详情文件状态
        subtask_file = os.path.join(SUBTASKS_DIR, f"subtask-{next_id:03d}.json")
        if os.path.exists(subtask_file):
            with open(subtask_file, "r", encoding="utf-8") as f:
                detail = json.load(f)
            detail["status"] = "in_progress"
            with open(subtask_file, "w", encoding="utf-8") as f:
                json.dump(detail, f, ensure_ascii=False, indent=2)
        print(f"✓ 已完成 {current}，开始子任务 {next_id}: {remaining[0]['name']}")
    else:
        data["current"] = len(data["subtasks"]) + 1
        print("✓ 所有子任务已完成！")

    data["updated_at"] = datetime.now().isoformat() + "Z"
    save_subtasks(data)


def cmd_current():
    """获取当前子任务"""
    data = load_subtasks()
    if not data:
        print("{}")
        return

    current = data.get("current", 1)
    for st in data["subtasks"]:
        if st["id"] == current:
            # 尝试读取详情
            subtask_file = os.path.join(SUBTASKS_DIR, f"subtask-{current:03d}.json")
            if os.path.exists(subtask_file):
                with open(subtask_file, "r", encoding="utf-8") as f:
                    detail = json.load(f)
                print(json.dumps(detail, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(st, ensure_ascii=False, indent=2))
            return
    print("{}")


def cmd_update(subtask_id, status):
    """更新子任务状态"""
    data = load_subtasks()
    if not data:
        print("✗ 子任务文件不存在")
        return

    for st in data["subtasks"]:
        if st["id"] == subtask_id:
            st["status"] = status
            data["updated_at"] = datetime.now().isoformat() + "Z"
            save_subtasks(data)
            # 更新详情文件状态
            subtask_file = os.path.join(SUBTASKS_DIR, f"subtask-{subtask_id:03d}.json")
            if os.path.exists(subtask_file):
                with open(subtask_file, "r", encoding="utf-8") as f:
                    detail = json.load(f)
                detail["status"] = status
                with open(subtask_file, "w", encoding="utf-8") as f:
                    json.dump(detail, f, ensure_ascii=False, indent=2)
            print(f"✓ 子任务 {subtask_id}: {st['name']} → {status}")
            return
    print(f"✗ 子任务 {subtask_id} 不存在")


def usage():
    print("""子任务进度管理

用法:
  python progress.py create <id> "<名称>" "<描述>" "<验收标准>"   创建子任务详情
  python progress.py init <task-id> <子任务1> <子任务2> ...      初始化（支持名称或ID）
  python progress.py status                                       查看进度
  python progress.py current                                      当前任务
  python progress.py next                                        完成当前，开始下一个
  python progress.py update <id> <status>                        更新状态
""")


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "create":
        if len(sys.argv) < 6:
            print("用法: python progress.py create <id> <名称> <描述> <验收标准>")
            sys.exit(1)
        cmd_create(int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5])

    elif cmd == "init":
        if len(sys.argv) < 4:
            print("用法: python progress.py init <task-id> <子任务1> <子任务2> ...")
            sys.exit(1)
        cmd_init(sys.argv[2], sys.argv[3:])

    elif cmd == "status":
        cmd_status()

    elif cmd == "current":
        cmd_current()

    elif cmd == "next":
        cmd_next()

    elif cmd == "update":
        if len(sys.argv) < 4:
            print("用法: python progress.py update <id> <status>")
            sys.exit(1)
        cmd_update(int(sys.argv[2]), sys.argv[3])

    else:
        print(f"未知命令: {cmd}")
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
