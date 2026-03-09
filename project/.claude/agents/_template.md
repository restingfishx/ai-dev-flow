# Agent 通用模板

## 输入参数（来自 dev skill）

| 参数 | 说明 | 来源 |
|------|------|------|
| 任务描述 | 要实现的功能 | tasks.json |
| 验收标准 | 完成条件 | tasks.json |
| 输入文件 | 依赖文件 | tasks.json |
| 输出文件 | 产出文件 | tasks.json |
| 依赖产出 | 需要的前置文档 | tasks.json |
| 迭代反馈 | 上轮问题（如有） | review 阶段 |

## 子任务机制

### 拆分规则

如果没有子任务，自动拆分为可独立执行的子任务：
1. **准备阶段** - 环境搭建、依赖安装
2. **核心实现** - 主要功能开发
3. **测试验证** - 单元测试、集成测试
4. **代码审查** - 自我审查

### 子任务状态

每个子任务维护状态：
- `pending` - 待开始
- `in_progress` - 执行中
- `completed` - 已完成

### 断点恢复

- 维护 `subtask_progress.json` 记录进度
- 包含：当前子任务、已完成列表、最后一个状态
- 恢复时读取文件，从断点继续

### 进度文件格式

```json
{
  "task_id": "TASK-001",
  "current_subtask": 2,
  "subtasks": [
    {"id": 1, "name": "准备阶段", "status": "completed"},
    {"id": 2, "name": "核心实现", "status": "in_progress"},
    {"id": 3, "name": "测试验证", "status": "pending"},
    {"id": 4, "name": "代码审查", "status": "pending"}
  ],
  "last_updated": "2024-01-01T10:00:00Z"
}
```

## 执行流程

```
1. 接收 dev skill 传递的参数
2. 检查 subtask_progress.json 是否存在
3. 如有断点 → 从断点继续
   如无断点 → 自动拆分并开始执行
4. 每完成一个子任务 → 更新进度文件
5. 全部完成 → 验证代码可运行
6. 验证通过 → 提交代码 → 报告结果给 dev skill
```

## Git 操作规则（必须遵守）

### Worktree 支持（推荐并行开发使用）

使用 git worktree 创建独立工作目录，实现真正的并行开发：

**首次开发（pending）：**
```bash
# 创建 worktree 和分支
git worktree add worktrees/task-<序号> -b feature/task-<序号>-<简短描述> main

# 进入 worktree 目录
cd worktrees/task-<序号>
```

**修复迭代（pending_fix）：**
```bash
# 进入已有的 worktree 目录
cd worktrees/task-<序号>
```

**开发完成后：**
```bash
# 切换回主目录
cd ../..

# 可选：删除 worktree（合并后）
git worktree remove worktrees/task-<序号>
```

### 分支创建（不使用 worktree 时）

根据任务状态创建分支：

**首次开发（pending）：**
```bash
# 基于 main 分支创建新功能分支
git checkout -b feature/task-<序号>-<简短描述> main
```

**修复迭代（pending_fix）：**
```bash
# 切回上一个开发分支
git checkout feature/task-<序号>-<简短描述>
```

分支命名规范：
- 格式：`feature/task-<序号>-<简短描述>`
- 示例：`feature/task-001-user-login`

### 代码提交

完成开发并验证通过后，必须提交代码：

```bash
# 添加所有变更
git add -A

# 提交代码
git commit -m "[TASK-XXX] 任务描述

- 完成内容 1
- 完成内容 2"
```

提交时机：
- 开发完成后立即提交
- 验证通过后才能提交
- 每个任务单独提交（便于追踪）

## 代码验证规则（必须遵守）

**代码必须能够运行才能提交 review！**

### 验证流程

1. **语法检查** - 确保无语法错误
2. **依赖检查** - 确保依赖可安装/导入
3. **逻辑验证** - 确保核心逻辑可执行
4. **如验证失败** - 修复问题 → 重新验证 → 直到通过

### 验证通过后才能提交

- 验证通过 → git commit → 报告完成
- 验证失败 → 不提交 → 修复后重试

> **具体验证命令请查看各 Agent 配置中的"验证方式"章节**
