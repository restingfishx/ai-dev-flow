---
name: dev
argument-hint: "[task-id]"
description: 开发调度 - 识别技术栈并调度对应开发 Agent。用于需要开始开发任务或调度开发 Agent 实现功能时。
disable-model-invocation: false
---

# 开发调度指令

参数: $ARGUMENTS

## 阶段零：前置校验

### 必须满足的条件

1. **GitHub 登录状态**：
   - 运行 `gh auth status` 检查是否已登录
   - 未登录 → **引导用户先登录 GitHub**
   - 登录后继续

2. **tasks.json 存在**：确保任务清单已创建
3. **任务状态正确**：
   - 状态为 `pending`（首次开发）或 `pending_fix`（修复迭代）
4. **任务存在**：指定的任务 ID 存在于 tasks.json 中
5. **依赖产出已就绪**：
   - 如果任务依赖 `DESIGN` → 检查设计文档是否存在
   - 如果任务依赖 `ARCH` → 检查架构文档是否存在

### GitHub 登录引导

如果未登录，提示用户：

```
⚠️ GitHub 未登录

请先登录 GitHub：
1. 运行 `gh auth login`
2. 选择 HTTPS 或 SSH
3. 完成认证

登录后请再次触发 /dev
```

### 依赖检查规则

从 tasks.json 中读取任务的 `depends_on_outputs` 字段，根据声明的依赖类型检查：

| 依赖 | 检查内容 |
|------|----------|
| DESIGN | docs/design/ 目录存在，设计文档就绪 |
| ARCH | docs/architecture.md 存在 |

> **注意**：`depends_on_outputs` 字段由 /split 阶段生成，声明任务依赖哪些角色的产出（DESIGN 或 ARCH）。

### 依赖未就绪时的自动处理

如果依赖产出不存在：
- **自动更新状态**：`pending` → `blocked`
- **记录阻塞原因**：在任务的 `block_reason` 字段记录缺少的依赖
- **提示用户**：告知任务已被阻塞，需要先完成相应产出

---

## 阻塞任务处理

### 阻塞状态

当任务依赖的产出未就绪时：
- 状态自动变为 `blocked`
- 记录阻塞原因：`{"blocked_by": "DESIGN", "reason": "设计文档不存在"}`

### 解锁流程

1. 用户完成 DESIGN 或 ARCH 阶段
2. 重新触发 /dev
3. 系统检查依赖已就绪
4. **自动更新状态**：`blocked` → `pending`

---

## 阶段一：读取任务信息

从 tasks.json 中读取任务信息：
- 技术栈（split 阶段已确定）
- 任务描述
- 验收标准
- 当前状态

### 技术栈来源

技术栈在 /split 阶段已经确定，直接使用 task 中的 `tech_stack` 字段：
- "Python + 后端" → dev-agent-python
- "Swift + iOS" → dev-agent-ios
- 以此类推

### 检查迭代状态

如果任务状态为 `pending_fix`：
- 读取上一次的审核反馈
- 将反馈内容作为开发上下文传递给 Subagent

### GitHub 仓库检查

检查本地仓库是否已关联远程仓库：

```bash
git remote -v
```

如果未配置：
- 提示用户先连接或创建 GitHub 仓库
- 不继续执行开发

> **注意**：分支创建和代码提交由 Subagent 执行。

## 阶段二：调度 Subagent

根据 tasks.json 中指定的技术栈，直接调度对应的 Subagent：

| tech_stack 字段 | 调度的 Agent |
|-----------------|-------------|
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

## 阶段三：执行开发

### 传递给 Subagent 的参数

dev 必须将以下信息完整传递给 Subagent：

| 参数 | 来源 | 说明 |
|------|------|------|
| 任务描述 | tasks.json | 要做什么 |
| 验收标准 | tasks.json | 做到什么程度 |
| 输入文件 | tasks.json | 依赖什么 |
| 输出文件 | tasks.json | 产出什么 |
| 依赖产出 | tasks.json | 需要哪些前置文档 |
| 迭代反馈 | 上轮 review | 如果是修复迭代，传递具体问题 |

### 子任务处理逻辑

#### 情况1：无子任务

Subagent 收到任务后，**自动拆分**为可执行的子任务：
- 拆分粒度：每个子任务可独立完成
- 边执行边记录：每完成一个子任务，记录进度

#### 情况2：有子任务

Subagent 收到任务后：
- 读取已保存的子任务进度
- 从最后一个未完成的子任务继续

### 开发前

- 状态变更：`pending` → `in_progress`
- 记录开始时间

### 开发中：代码验证

> 代码验证由 Subagent 执行，见 `_template.md` 中的"代码验证规则"

Subagent 必须验证代码能够运行后才能提交。

### 开发后

- 状态变更：`in_progress` → `pending_review`
- 迭代次数 +1

### 迭代场景

如果存在上一轮反馈：
- 将反馈内容和修改要求明确告知 Subagent
- Subagent 基于反馈进行修改

## 阶段四：更新状态

开发完成后更新 tasks.json：
- 状态变更：`in_progress` → `pending_review`
- 迭代次数 +1

## 阶段五：多任务并行处理

### 并行开发规则

如果存在多个 `pending` 状态的任务，可以并行开发：

#### 并行触发方式

用户可以同时触发多个 /dev：
```
/dev TASK-001
/dev TASK-002
```

#### 分支隔离

每个任务使用独立分支或独立 worktree：
- TASK-001 → worktrees/task-001/ 或 feature/task-001-xxx
- TASK-002 → worktrees/task-002/ 或 feature/task-002-yyy

分支之间互不干扰。

#### Worktree 并行开发（推荐）

推荐使用 git worktree 实现真正的并行开发：

```bash
# 任务 1
/dev TASK-001

# 任务 2（在新终端会话中）
cd your-project
git worktree add worktrees/task-002 -b feature/task-002-xxx
cd worktrees/task-002
# 然后启动新的 Claude Code 会话
```

**Worktree 优势**：
- 每个任务有独立目录，不会相互干扰
- 可以同时在多个终端会话中开发
- 切换分支无需来回切换

#### 合并顺序

合并时需注意依赖关系：
- 如果任务之间有依赖 → 按依赖顺序合并
- 如果任务之间无依赖 → 可以任意顺序合并

### 任务依赖处理

如果 tasks.json 中定义了 `depends_on`：
- 必须等待依赖任务完成（状态为 `completed`）
- 才能开始当前任务

---

## 重要规则

- 技术栈在 /split 阶段确定，/dev 阶段直接使用，不再重新识别
- 遇到不确定问题，必须提问
- 批量编码后统一审核
- 迭代开发时，必须基于反馈内容进行修改
- 每个任务独立分支，避免相互干扰
