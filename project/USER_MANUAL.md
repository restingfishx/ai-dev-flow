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
/dev TASK-001          # 开始开发第一个任务
  ↓
REVIEW 阶段
  ↓
/review TASK-001       # 审核代码
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

---

### ARCH - 架构设计

```bash
/arch
```

输入技术选型需求，系统生成架构文档。

**依赖**：需要先完成 PM 阶段。

---

### DESIGN - 界面设计

```bash
/design
```

输入界面需求，生成设计文档。

**依赖**：需要先完成 PM 阶段。

---

### SPLIT - 任务拆分

```bash
/split
```

基于 PRD + 架构/设计文档，生成任务清单（tasks.json）。

---

### DEV - 开发执行

```bash
/dev TASK-001          # 开发指定任务
```

**首次开发**：
- 检查任务状态为 `pending`
- 检查依赖产出是否就绪
- 创建功能分支
- 调度对应技术栈的 Agent

**修复迭代**：
- 检查任务状态为 `pending_fix`
- 切回之前的分支
- 基于反馈修复问题

**断线恢复**：
- 新会话执行 `/dev TASK-001`
- 系统自动检测 `in_progress` 状态
- 从断点继续执行

---

### REVIEW - 代码审核

```bash
/review TASK-001
```

**审核流程**：
1. 代码推送到远程分支
2. 创建 PR
3. 用户在 GitHub 审核
4. 审核通过 → 自动合并
5. 审核不通过 → 反馈给开发者

**定时检查 PR 状态**（可选）：
```
/loop 5m 检查 PR #123 状态
```

---

### DEPLOY - 部署上线

```bash
/deploy                  # 部署到默认环境
/deploy production       # 部署到生产环境
```

**前置条件**：所有任务状态为 `completed`。

---

## 任务状态说明

| 状态 | 说明 | 如何处理 |
|------|------|---------|
| `pending` | 待开始 | 执行 `/dev TASK-XXX` |
| `blocked` | 被阻塞 | 检查依赖产出是否就绪 |
| `in_progress` | 开发中 | 继续执行或断线恢复 |
| `pending_review` | 待审核 | 执行 `/review TASK-XXX` |
| `pending_fix` | 待修复 | 执行 `/dev TASK-XXX` 修复 |
| `completed` | 已完成 | 等待其他任务 |
| `deployed` | 已部署 | 任务完成 |

---

## 断线恢复指南

### 场景 1：开发中断

**现象**：正在开发时 Claude Code 崩溃/关闭

**恢复方法**：
```bash
# 新会话启动后
cd your-project
/claude

# 继续开发
/dev TASK-001
```

系统会自动检测任务状态为 `in_progress`，从断点继续。

---

### 场景 2：审核中断

**现象**：PR 已创建但未完成审核

**恢复方法**：
```bash
# 新会话启动后
/review TASK-001
```

系统会检查 PR 状态，继续审核流程。

---

### 场景 3：部署中断

**现象**：部署过程中断

**恢复方法**：
```bash
# 检查部署状态
git status
docker ps

# 手动检查服务是否正常运行
# 如需重新部署
/deploy
```

---

## 目录结构约定

不同技术栈的代码放在不同目录，避免混合在一起。

### 推荐目录结构

```
project/
├── docs/                    # 项目文档
│   ├── PRD.md              # 需求文档
│   ├── architecture.md      # 架构文档
│   └── design/              # 设计文档
├── frontend/                # 前端代码
│   ├── web/               # Web 端 (React/Vue)
│   │   ├── src/
│   │   └── package.json
│   ├── mobile/            # 移动端 (React Native/Flutter)
│   └── desktop/           # 桌面端 (Electron/Tauri)
├── backend/                # 后端代码
│   ├── api/               # API 服务
│   │   ├── python/        # Python (FastAPI/Django/Flask)
│   │   ├── go/            # Go
│   │   ├── nodejs/        # Node.js
│   │   └── java/          # Java
│   └── services/         # 其他服务
├── mobile/                  # 移动端原生代码
│   ├── ios/               # Swift (iOS)
│   └── android/           # Kotlin (Android)
├── worktrees/               # Git Worktree 目录（并行开发用）
│   ├── task-001/         # TASK-001 的开发目录
│   └── task-002/         # TASK-002 的开发目录
└── shared/                 # 共享代码
    ├── types/             # 类型定义
    └── utils/            # 工具函数
```

### 技术栈 → 目录映射

| 技术栈 | 输出目录 |
|--------|---------|
| React + Web | `frontend/web/` |
| Vue + Web | `frontend/web/` |
| React Native + 移动端 | `frontend/mobile/` |
| Flutter + 移动端 | `frontend/mobile/` |
| Electron + 桌面端 | `frontend/desktop/` |
| Tauri + 桌面端 | `frontend/desktop/` |
| Python + 后端 | `backend/api/python/` |
| Node.js + 后端 | `backend/api/nodejs/` |
| Go + 后端 | `backend/api/go/` |
| Java + 后端 | `backend/api/java/` |
| Rust + 后端 | `backend/api/rust/` |
| Swift + iOS | `mobile/ios/` |
| Kotlin + Android | `mobile/android/` |
| Qt + C++ + 桌面端 | `desktop/qt/` |

### 在任务中指定输出目录

在 `/split` 阶段生成任务时，每个任务的"输出"字段应包含具体路径：

```json
{
  "id": "TASK-001",
  "description": "开发用户登录 API",
  "tech_stack": "Python + 后端",
  "output": "backend/api/python/user/login.py",
  "status": "pending"
}
```

---

## 常见问题

### Q1：任务被阻塞怎么办？

检查任务状态是否为 `blocked`，查看阻塞原因。完成依赖产出后，状态会自动恢复。

### Q2：如何查看当前任务列表？

查看 `tasks.json` 文件，或询问：
```
当前有哪些任务？
```

### Q3：如何并行开发多个任务？

**方式一：单个会话（串行）**
```
/dev TASK-001
/dev TASK-002
```

**方式二：Worktree 并行（推荐）**

```bash
# 终端 1 - 开发 TASK-001
git worktree add worktrees/task-001 -b feature/task-001-xxx main
cd worktrees/task-001
# 启动 Claude Code 开发 TASK-001

# 终端 2 - 开发 TASK-002
git worktree add worktrees/task-002 -b feature/task-002-xxx main
cd worktrees/task-002
# 启动 Claude Code 开发 TASK-002
```

每个任务使用独立 worktree 目录，真正并行开发，互不干扰。

**Worktree 清理**（合并后）：
```bash
git worktree remove worktrees/task-001
```

### Q4：如何取消正在执行的任务？

当前不支持直接取消。等待当前子任务完成，或新建会话继续其他任务。

### Q5：如何查看代码审核结果？

1. GitHub PR 链接
2. 询问 Claude：
```
PR 审核结果是什么？
```

---

## GitHub 集成

### 登录

```bash
gh auth login
```

### 创建仓库

```bash
# 本地已有项目
gh repo create

# 新建仓库
gh repo create my-project --public
```

### 查看 PR

```bash
# 列出 PR
gh pr list

# 查看 PR 状态
gh pr view 1
```

---

## 最佳实践

1. **每阶段确认后再继续**：不要跳过审核直接进入下一阶段
2. **及时处理反馈**：收到审核反馈后尽快修复
3. **保持会话活跃**：长时间任务使用 `/loop` 定时检查
4. **定期同步代码**：开发完成后及时提交，避免丢失
