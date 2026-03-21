---
name: status
description: 任务状态查看 - 查看当前任务清单状态。用于需要了解任务进度、查看哪些任务可以开始或被阻塞时。
disable-model-invocation: false
argument-hint: "[task-id]"
---

# 任务状态查看指令

参数: $ARGUMENTS

执行 `python .claude/lib/iteration.py check` 获取当前迭代信息。

## 阶段一：读取任务清单

使用脚本查看任务状态：

```bash
# 查看所有任务
python .claude/skills/split/scripts/tasks.py status

# 查看指定任务
python .claude/skills/split/scripts/tasks.py status TASK-001

# 查看任务详情
python .claude/skills/split/scripts/tasks.py get TASK-001
```

## 阶段二：分析任务状态

### 统计各类状态

统计以下状态的任务数量：
- `pending` - 可执行任务
- `pending_design` - 等待 DESIGN
- `pending_arch` - 等待 ARCH
- `in_progress` - 开发中
- `pending_review` - 待审核
- `pending_fix` - 需修复
- `completed` - 已完成
- `deployed` - 已部署

### 检查依赖产出

使用 iteration 模块动态检查目录：
```bash
python .claude/lib/iteration.py check
```

## 阶段三：输出状态报告

### 任务状态看板

输出格式：

```
📋 任务状态看板

总任务数: X

✅ 可执行 (pending): X
⏳ 等待设计 (pending_design): X
🏗️ 等待架构 (pending_arch): X
🔄 开发中 (in_progress): X
👀 待审核 (pending_review): X
🔧 需修复 (pending_fix): X
✅ 已完成 (completed): X
🚀 已部署 (deployed): X

---

依赖产出状态:
📐 ARCH: ✅ 已完成 / ❌ 未完成
🎨 DESIGN: ✅ 已完成 / ❌ 未完成
```

### 详细任务列表

按状态分组显示任务：

```
## ✅ 可执行任务
- TASK-001: 登录页面开发
- TASK-002: 用户 API 开发

## ⏳ 等待设计
- TASK-003: 首页开发 (阻塞原因: 等待 DESIGN)

## ⏳ 等待架构
- TASK-004: 支付模块 (阻塞原因: 等待 ARCH)
```

### 指定任务详情

如果传入了 task-id 参数：

```
## TASK-XXX 详情

描述: ...
技术栈: ...
状态: pending_design
阻塞原因: 等待 DESIGN 完成
依赖产出:
  - DESIGN: ❌ 不存在
  - ARCH: ✅ 存在
```

## 重要规则

- 任务状态为 `pending_design` 时，告诉用户可以先开发后端任务
- 任务状态为 `pending_arch` 时，告诉用户 ARCH 尚未完成
- 运行 `python tasks.py unlock` 查看任务依赖状态（脚本会自动解析迭代路径）
