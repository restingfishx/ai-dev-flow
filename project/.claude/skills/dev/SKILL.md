---
name: dev
argument-hint: "[task-id]"
description: 开发调度 - 识别技术栈并调度对应开发 Agent。
disable-model-invocation: false
---

# 开发调度指令

参数: $ARGUMENTS

执行 `python .claude/lib/iteration.py check` 获取当前迭代信息。

## 前置校验

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1. GitHub 登录 | `gh auth status` | 未登录则提示 |
| 2. tasks.json | 检查文件存在 | 未创建则提示 |
| 3. 任务状态 | 从 tasks.json 读取 | 必须是 pending/pending_fix/pending_design/pending_arch |
| 4. GitHub 仓库 | `git remote -v` | 未配置则提示 |

---

## 读取任务信息

从 tasks.json 读取：tech_stack, description, acceptance, output, depends_on_outputs, relevant_apis, iterations

---

## 任务预处理

### 1. 进入 Worktree

| 状态 | 处理 |
|------|------|
| pending | 创建 worktree 并进入 |
| pending_fix | 进入 worktree，获取迭代反馈 |
| pending_design/pending_arch | 检查相关目录存在则自动解锁 |

### 2. 依赖检查

`python .claude/skills/split/scripts/tasks.py unlock`

### 3. 更新状态

`python .claude/skills/split/scripts/tasks.py update <task-id> in_progress`

---

## 调度 Subagent

根据 tech_stack 选择对应的 Agent：

```
subagent_type: <对应的 dev-agent-xxx>
prompt:
  - 任务 ID、描述、验收标准
  - 输入/输出目录
  - 依赖产出、相关 API
  - 迭代反馈（pending_fix 时）

  工作目录：worktrees/<task-id>/

  根据主任务状态判断：
  - pending_fix：先读取反馈，理解问题
  - in_progress + 有断点：用 progress.py current 查看，有返回则继续当前子任务
  - in_progress + 无断点：拆分任务后执行

  使用 progress.py 管理子任务：
  - create <id> "<名称>" "<描述>" "<验收标准>"：创建子任务
  - init <task-id> <子任务1> <子任务2> ...：初始化子任务
  - current：查看当前任务
  - next：完成当前，开始下一个
```

### tech_stack 映射表

| tech_stack | subagent_type |
|------------|---------------|
| React + Web | dev-agent-react |
| Vue + Web | dev-agent-vue |
| React Native + 移动端 | dev-agent-react-native |
| Flutter + 移动端 | dev-agent-flutter |
| Electron + 桌面端 | dev-agent-electron |
| Tauri + 桌面端 | dev-agent-tauri |
| Qt + C++ + 桌面端 | dev-agent-qt |
| Python + 后端 | dev-agent-python |
| Node.js + 后端 | dev-agent-nodejs |
| Go + 后端 | dev-agent-go |
| Java + 后端 | dev-agent-java |
| Rust + 后端 | dev-agent-rust |
| Swift + iOS | dev-agent-ios |
| Swift + macOS | dev-agent-macos |
| Kotlin + Android | dev-agent-android |
| DBA | dev-agent-dba |
| DevOps | dev-agent-devops |

---

## 更新状态

开发完成后，更新状态为 pending_review。

---

## 重要规则

- 验证通过才能提交
- 迭代开发基于反馈修改
