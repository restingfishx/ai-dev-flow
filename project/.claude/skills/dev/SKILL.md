---
name: dev
argument-hint: "[task-id]"
description: 开发调度 - 识别技术栈并调度对应开发 Agent。
disable-model-invocation: false
---

# 开发调度指令

参数: $ARGUMENTS

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
| pending | 创建 worktree 并进入：`git worktree add worktrees/<task-id> release && cd worktrees/<task-id>` |
| pending_fix | 进入 worktree：`cd worktrees/<task-id>`，获取迭代反馈（从 tasks.json 的 iterations 字段获取最后一次审核不通过的原因） |
| pending_design/pending_arch | 检查 docs/design/ 或 docs/architecture/ 存在则自动解锁 |

### 2. 依赖检查

```bash
python .claude/skills/split/scripts/tasks.py unlock
```

- 依赖已满足 → 继续
- 依赖未满足 → 提示用户

### 3. 更新状态

```bash
python .claude/skills/split/scripts/tasks.py update <task-id> in_progress
```

---

## 调度 Subagent

根据 tech_stack 选择对应的 Agent，使用 Agent 工具调用：

```
subagent_type: <对应的 dev-agent-xxx>
description: 开发 <tech_stack> 任务
prompt: |
  ## 任务信息
  - 任务 ID: <task-id> （格式：TASK-xxx）
  - 主任务状态: <in_progress/pending_fix>
  - 任务描述: <description>
  - 验收标准: <acceptance>
  - 输入文件: <input>
  - 输出目录: <output>
  - 依赖产出: <depends_on_outputs>
  - 相关 API: <relevant_apis>
  - 迭代反馈: <pending_fix 时填写，in_progress 时为空>

  ## 工作目录
  worktrees/<task-id>/

  ## 你需要执行的开发流程

  根据主任务状态和断点状态，判断下一步操作：

  **情况一：主任务状态是 pending_fix**
  - 任务类型：修复bug
  - 必须执行：先读取迭代反馈，理解需要修复的问题
  - 拆分任务后执行：
    ```
    python .claude/agents/scripts/progress.py create <id> "<名称>" "<描述>" "<验收标准>"
    python .claude/agents/scripts/progress.py init <task-id> <子任务1> <子任务2> ...
    ```
  - 注意：init 会追加到现有子任务后面

  **情况二：主任务状态是 in_progress，且有断点（subtasks/subtask-<任务编号>.json 存在）**
  - 任务类型：断点恢复
  - 不需要拆分任务，直接继续执行当前子任务

  **情况三：主任务状态是 in_progress，且无断点**
  - 任务类型：首次开发
  - 拆分任务后执行：
    ```
    python .claude/agents/scripts/progress.py create <id> "<名称>" "<描述>" "<验收标准>"
    python .claude/agents/scripts/progress.py init <task-id> <子任务1> <子任务2> ...
    ```

  ### 断点判断

  判断是否有断点：检查 subtasks/ 目录下是否存在 subtask-xxx.json 文件（xxx是<task-id>，从TASK-xxx中取）

  ## 子任务执行步骤

  1. 查看当前任务：
     ```
     python .claude/agents/scripts/progress.py current
     ```

  2. 执行当前功能点

  3. 完成当前，开始下一个：
     ```
     python .claude/agents/scripts/progress.py next
     ```

  4. 重复步骤 1-3 直到全部完成

  5. subagent 开发完成，退出 worktree
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

## 更新状态并验证

1. 更新状态为 pending_review：
   ```bash
   cd worktrees/<task-id>
   python .claude/skills/split/scripts/tasks.py update <task-id> pending_review
   python .claude/skills/split/scripts/tasks.py iter <task-id> <agent> "待审核" ""
   ```

2. 启动项目验证（从 docs/architecture/overview.md 读取启动命令）

3. 用户确认后，提示：请执行 /review <task-id> 通过/不通过

---

## 重要规则

- 验证通过才能提交
- 迭代开发基于反馈修改
