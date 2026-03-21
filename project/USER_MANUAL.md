# AiDevFlow 用户手册

## 快速开始

### 1. 初始化项目

```bash
# 进入项目目录
cd your-project

# 初始化 Git 仓库（如需要）
git init

# 登录 GitHub（如需要）
gh auth login
```

### 2. 启动开发流程

```
PM 阶段
  ↓
/pm                    # 创建需求文档
  ↓
ARCH + DESIGN 阶段    # 并行执行
  ↓
/arch                  # 创建架构文档
/design                # 创建设计文档
  ↓
SPLIT 阶段
  ↓
/split                 # 拆分任务
  ↓
DEV 阶段
  ↓
/dev TASK-001          # 开始开发
  ↓
REVIEW 阶段
  ↓
/review TASK-001 通过   # 告知审核结果
  ↓
DEPLOY 阶段
  ↓
/deploy                # 部署上线
```

---

## 阶段操作指南

### PM - 需求分析

```bash
/pm
```

输入需求描述，系统自动生成 PRD 文档。

**输出路径**：`docs/prd.md`（迭代模式下为 `{version}/docs/prd.md`）

---

### ARCH - 架构设计

```bash
/arch
```

输入技术选型需求，系统生成架构文档。

**依赖**：需要先完成 PM 阶段。

**输出路径**：`docs/architecture/`（迭代模式下为 `{version}/docs/architecture/`）

---

### DESIGN - 界面设计

```bash
/design
```

输入界面需求，生成设计文档。

**依赖**：需要先完成 PM 阶段。

**输出路径**：`docs/design/`（迭代模式下为 `{version}/docs/design/`）

---

### SPLIT - 任务拆分

```bash
/split
```

基于 PRD + 架构/设计文档，生成任务清单（tasks.json）。

**输出路径**：`tasks.json`（迭代模式下为 `{version}/tasks.json`）

---

### DEV - 开发执行

```bash
/dev TASK-001          # 开发指定任务
```

**开发流程**：
1. 检查 GitHub 登录
2. 创建 Worktree：`worktrees/task-001/`
3. Subagent 开发代码
4. 验证通过后：commit → push → 创建 PR
5. 状态变为 `pending_review`

**修复迭代**：
```bash
/dev TASK-001          # 基于反馈修复
```

---

### REVIEW - 代码审核

```bash
/review TASK-001 通过              # 审核通过
/review TASK-001 不通过 原因        # 审核不通过
```

**审核流程**：
1. 用户在 GitHub 上审核 PR
2. 告诉 Claude 审核结果
3. Claude 更新任务状态

---

### DEPLOY - 部署上线

```bash
/deploy                  # 部署到默认环境
/deploy production       # 部署到生产环境
```

**前置条件**：所有任务状态为 `completed`。

---

## 迭代模式（可选）

### 概述

迭代模式支持管理项目的多个版本，每个版本有独立的文档和任务清单。

### 使用场景

- 需要分多个版本发布功能
- 希望在当前迭代完成后才开始下一个迭代
- 需要保留每个迭代的完整工作记录

### 创建迭代

```bash
/iteration create v1.0     # 创建首个迭代
/iteration create v1.1     # 基于 v1.0 创建 v1.1
```

### 管理迭代

```bash
/iteration list            # 列出所有迭代
/iteration switch v1.0     # 切换到 v1.0
/iteration complete v1.0  # 完成迭代
/iteration status          # 查看当前状态
```

### 路径规则

| 类型 | 路径 | 说明 |
|------|------|------|
| 迭代目录 | `v1.0/`, `v1.1/` | 各迭代独立目录 |
| 文档 | `docs/prd.md` | 自动解析到当前迭代 |
| 任务清单 | `tasks.json` | 自动解析到当前迭代 |
| 根目录 | `worktrees/`, `.git/` | 不受迭代影响 |

---

## 任务状态说明

| 状态 | 说明 | 如何处理 |
|------|------|---------|
| `pending` | 待开始 | 执行 `/dev TASK-XXX` |
| `pending_design` | 等待设计 | 设计完成后自动解锁 |
| `pending_arch` | 等待架构 | 架构完成后自动解锁 |
| `in_progress` | 开发中 | 继续执行 |
| `pending_review` | 待审核 | 执行 `/review TASK-XXX` |
| `pending_fix` | 待修复 | 执行 `/dev TASK-XXX` 修复 |
| `completed` | 已完成 | 等待其他任务 |
| `deployed` | 已部署 | 任务完成 |

---

## 目录结构约定

### 推荐目录结构

```
project/
├── v1.0/                    # 迭代目录（启用迭代模式时）
│   ├── docs/
│   │   ├── prd.md
│   │   ├── architecture/
│   │   └── design/
│   ├── tasks.json
│   └── subtasks/
├── docs/                    # 文档（未启用迭代模式时）
│   ├── prd.md
│   ├── architecture/
│   └── design/
├── tasks.json               # 任务清单（未启用迭代模式时）
├── frontend/                # 前端代码
├── backend/                 # 后端代码
├── ios/                     # iOS 代码
├── android/                 # Android 代码
└── worktrees/               # Git Worktree 目录（不受迭代影响）
    ├── task-001/          # TASK-001 开发目录
    └── task-002/          # TASK-002 开发目录
```

### 技术栈 → 目录映射

| 技术栈 | 输出目录 |
|--------|---------|
| React + Web | `frontend/` |
| Vue + Web | `frontend/` |
| React Native | `frontend/` |
| Flutter | `frontend/` |
| Electron | `frontend/` |
| Tauri | `frontend/` |
| Python | `backend/` |
| Node.js | `backend/` |
| Go | `backend/` |
| Java | `backend/` |
| Rust | `backend/` |
| Swift + iOS | `ios/` |
| Kotlin + Android | `android/` |

---

## 并行开发

### Worktree 并行开发

```bash
# 终端 1 - 开发 TASK-001
git worktree add worktrees/task-001 release
cd worktrees/task-001
# 启动 Claude Code 开发

# 终端 2 - 开发 TASK-002
git worktree add worktrees/task-002 release
cd worktrees/task-002
# 启动 Claude Code 开发
```

每个任务独立目录，互不干扰。

**Worktree 清理**（合并后）：
```bash
git worktree remove worktrees/task-001
```

---

## 常见问题

### Q1：如何查看任务状态？

```bash
/status                  # 查看所有任务状态
/status TASK-001         # 查看指定任务详情
```

### Q2：任务被阻塞怎么办？

- `pending_design`：等待 DESIGN 完成
- `pending_arch`：等待 ARCH 完成

完成后执行 `/dev TASK-XXX` 自动解锁。

### Q3：如何并行开发多个任务？

使用 Worktree：
```bash
git worktree add worktrees/task-001 release
git worktree add worktrees/task-002 release
```
然后在各自目录启动 Claude Code。

### Q4：如何使用迭代模式？

```bash
/iteration create v1.0     # 创建首个迭代
# 然后正常执行各阶段
/pm
/arch
/split
/dev TASK-001
# 完成当前迭代后创建新迭代
/iteration create v1.1
```

---

## GitHub 集成

### 登录

```bash
gh auth login
```

### 查看 PR

```bash
gh pr list
gh pr view 1
```

---

## 最佳实践

1. **每阶段确认后再继续**：不要跳过审核直接进入下一阶段
2. **及时处理反馈**：收到审核反馈后尽快修复
3. **及时告知审核结果**：PR 审核完成后告诉 Claude 结果
4. **迭代模式**：大型项目建议使用迭代模式管理多个版本
