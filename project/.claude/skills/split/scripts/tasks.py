#!/usr/bin/env python3
"""tasks.json 操作脚本"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

TASKS_FILE = "tasks.json"


def load_tasks():
    """加载 tasks.json"""
    if not os.path.exists(TASKS_FILE):
        return {"version": "1.0", "generated_at": "", "tasks": []}

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(data):
    """保存 tasks.json"""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cmd_init():
    """初始化 tasks.json"""
    data = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat() + "Z",
        "tasks": []
    }
    save_tasks(data)
    print(f"✓ 已创建 {TASKS_FILE}")


def cmd_add(task_id, description, tech_stack, output, input_file="", acceptance="",
           depends_on=None, depends_on_outputs=None, relevant_apis=None):
    """添加任务"""
    data = load_tasks()

    # 检查任务 ID 是否已存在
    for task in data["tasks"]:
        if task["id"] == task_id:
            print(f"✗ 任务 {task_id} 已存在")
            return

    task = {
        "id": task_id,
        "description": description,
        "tech_stack": tech_stack,
        "output": output,
        "input": input_file,
        "acceptance": acceptance,
        "depends_on": depends_on or [],
        "depends_on_outputs": depends_on_outputs or [],
        "relevant_apis": relevant_apis or [],
        "status": "pending",
        "iteration": 0,
        "iterations": []
    }

    data["tasks"].append(task)
    save_tasks(data)
    print(f"✓ 已添加任务 {task_id}: {description}")


def cmd_batch():
    """批量添加任务（从 stdin 读取 JSON 数组）"""
    import sys
    data = load_tasks()

    # 从 stdin 读取 JSON
    input_data = sys.stdin.read()
    if not input_data.strip():
        print("✗ 请从 stdin 输入 JSON 数组")
        return

    try:
        tasks = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f"✗ JSON 解析失败: {e}")
        return

    if not isinstance(tasks, list):
        print("✗ 输入必须是 JSON 数组")
        return

    # 添加每个任务
    for task in tasks:
        task_id = task.get("id")
        if not task_id:
            print("✗ 任务缺少 id 字段")
            continue

        # 检查是否已存在
        exists = any(t["id"] == task_id for t in data["tasks"])
        if exists:
            print(f"⏭ 跳过 {task_id}: 已存在")
            continue

        # 设置默认值
        # 任务初始状态都为 pending，依赖检查在 unlock 时处理
        task.setdefault("status", "pending")
        task.setdefault("iteration", 0)
        task.setdefault("iterations", [])
        task.setdefault("depends_on", [])
        task.setdefault("depends_on_outputs", [])
        task.setdefault("relevant_apis", [])

        data["tasks"].append(task)
        print(f"✓ 已添加任务 {task_id}")

    save_tasks(data)
    print(f"\n✓ 共添加 {len(data['tasks'])} 个任务")


def cmd_status(task_id=None):
    """查看任务状态"""
    data = load_tasks()

    if not data["tasks"]:
        print("暂无任务")
        return

    if task_id:
        # 查看指定任务
        for task in data["tasks"]:
            if task["id"] == task_id:
                print(f"{task['id']}: {task['description']}")
                print(f"  状态: {task['status']}")
                print(f"  技术栈: {task['tech_stack']}")
                print(f"  输出: {task['output']}")
                return
        print(f"✗ 任务 {task_id} 不存在")
    else:
        # 查看所有任务
        print("任务列表:")
        for task in data["tasks"]:
            status_icon = {
                "pending": "⏳",
                "pending_design": "🎨",
                "pending_arch": "🏗️",
                "in_progress": "🔄",
                "pending_review": "👀",
                "pending_fix": "🔧",
                "completed": "✅",
                "deployed": "🚀",
                "blocked": "❌"
            }.get(task["status"], "?")

            print(f"  {status_icon} {task['id']}: {task['description']} [{task['status']}]")


def cmd_update_status(task_id, new_status):
    """更新任务状态"""
    data = load_tasks()

    for task in data["tasks"]:
        if task["id"] == task_id:
            task["status"] = new_status
            save_tasks(data)
            print(f"✓ {task_id}: {task['status']} → {new_status}")
            return

    print(f"✗ 任务 {task_id} 不存在")


def cmd_add_iteration(task_id, subagent, review_result, feedback):
    """添加迭代记录"""
    data = load_tasks()

    for task in data["tasks"]:
        if task["id"] == task_id:
            iteration = {
                "iteration": task["iteration"] + 1,
                "subagent": subagent,
                "review_result": review_result,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat() + "Z"
            }
            task["iterations"].append(iteration)
            task["iteration"] = iteration["iteration"]
            save_tasks(data)
            print(f"✓ {task_id}: 已添加迭代记录 #{iteration['iteration']}")
            return

    print(f"✗ 任务 {task_id} 不存在")


def cmd_get(task_id):
    """获取任务详情"""
    data = load_tasks()

    for task in data["tasks"]:
        if task["id"] == task_id:
            print(json.dumps(task, ensure_ascii=False, indent=2))
            return

    print(f"✗ 任务 {task_id} 不存在")


def cmd_unlock():
    """检查并解锁依赖已满足的任务"""
    data = load_tasks()

    unlocked = []
    blocked = []  # 记录仍被阻塞的任务
    for task in data["tasks"]:
        # 只检查 pending 状态的任务
        if task["status"] != "pending":
            continue

        # 检查 depends_on 字段
        depends_on = task.get("depends_on", [])
        if not depends_on:
            # 没有依赖的任务，保持 pending 状态
            continue

        # 检查所有依赖任务是否都已完成
        all_deps_completed = True
        unmet_deps = []
        for dep_id in depends_on:
            dep_task = next((t for t in data["tasks"] if t["id"] == dep_id), None)
            if not dep_task:
                all_deps_completed = False
                unmet_deps.append(f"{dep_id}(不存在)")
            elif dep_task["status"] not in ["completed", "deployed"]:
                all_deps_completed = False
                unmet_deps.append(f"{dep_id}({dep_task['status']})")

        # 如果所有依赖都已完成，保持 pending 状态（可执行）
        # 如果有依赖未完成，标记为被阻塞
        if all_deps_completed:
            unlocked.append(task["id"])
        else:
            blocked.append(f"{task['id']}: 等待 {', '.join(unmet_deps)}")

    # 显示结果
    if unlocked:
        print(f"✓ 可执行任务: {', '.join(unlocked)}")
    if blocked:
        print(f"⏳ 被阻塞任务:")
        for b in blocked:
            print(f"  - {b}")
    if not unlocked and not blocked:
        print("没有需要处理的任务")


def cmd_check_deps(task_id):
    """检查任务依赖状态"""
    data = load_tasks()

    task = next((t for t in data["tasks"] if t["id"] == task_id), None)
    if not task:
        print(f"✗ 任务 {task_id} 不存在")
        return

    depends_on = task.get("depends_on", [])
    if not depends_on:
        print(f"任务 {task_id} 没有依赖")
        return

    print(f"任务 {task_id} 的依赖状态:")
    for dep_id in depends_on:
        dep_task = next((t for t in data["tasks"] if t["id"] == dep_id), None)
        if dep_task:
            status_icon = {
                "pending": "⏳",
                "pending_design": "🎨",
                "pending_arch": "🏗️",
                "in_progress": "🔄",
                "pending_review": "👀",
                "pending_fix": "🔧",
                "completed": "✅",
                "deployed": "🚀",
                "blocked": "❌"
            }.get(dep_task["status"], "?")

            print(f"  {status_icon} {dep_id}: {dep_task['status']}")
        else:
            print(f"  ❌ {dep_id}: 不存在")


def usage():
    """显示用法"""
    print("""tasks.json 操作脚本

用法:
  python tasks.py init                    初始化 tasks.json
  python tasks.py add <id> <描述> <技术栈> <输出目录>  添加任务
  python tasks.py batch < json              批量添加任务
  python tasks.py status [task-id]        查看任务状态
  python tasks.py update <id> <状态>      更新任务状态
  python tasks.py iter <id> <agent> <结果> <反馈>  添加迭代记录
  python tasks.py get <id>                获取任务详情
  python tasks.py list                    列出所有任务
  python tasks.py unlock                  检查并解锁依赖已满足的任务
  python tasks.py deps <id>               检查任务依赖状态

示例:
  python tasks.py init
  python tasks.py add TASK-001 "开发登录页面" React "frontend/"
  cat tasks.json | python tasks.py batch
  python tasks.py status
  python tasks.py update TASK-001 in_progress
  python tasks.py iter TASK-001 dev-agent-react "不通过" "代码有bug"
  python tasks.py get TASK-001
  python tasks.py unlock
  python tasks.py deps TASK-002
""")


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        cmd_init()

    elif cmd == "add":
        if len(sys.argv) < 5:
            print("用法: python tasks.py add <id> <描述> <技术栈> <输出目录>")
            sys.exit(1)
        cmd_add(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "")

    elif cmd == "batch":
        cmd_batch()

    elif cmd == "status":
        cmd_status(sys.argv[2] if len(sys.argv) > 2 else None)

    elif cmd == "list":
        cmd_status()

    elif cmd == "update":
        if len(sys.argv) < 4:
            print("用法: python tasks.py update <id> <状态>")
            sys.exit(1)
        cmd_update_status(sys.argv[2], sys.argv[3])

    elif cmd == "iter":
        if len(sys.argv) < 6:
            print("用法: python tasks.py iter <id> <agent> <结果> <反馈>")
            sys.exit(1)
        cmd_add_iteration(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("用法: python tasks.py get <id>")
            sys.exit(1)
        cmd_get(sys.argv[2])

    elif cmd == "unlock":
        cmd_unlock()

    elif cmd == "deps":
        if len(sys.argv) < 3:
            print("用法: python tasks.py deps <id>")
            sys.exit(1)
        cmd_check_deps(sys.argv[2])

    else:
        print(f"未知命令: {cmd}")
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
