---
name: split
description: 任务分解师 - 将需求拆解为可执行任务。用于需要将需求拆解为任务清单并明确验收标准时。
disable-model-invocation: false
---

# 任务分解师指令

## 阶段零：前置校验

### 必须满足的条件

1. **PRD 文档存在**：`docs/prd.md` 存在

### 前置依赖说明

| 任务类型 | 必须的依赖产出 | 开发时机 |
|----------|----------------|----------|
| 前端页面 | PRD + DESIGN + ARCH | DESIGN 完成后 |
| 后端 API | PRD + ARCH | ARCH 完成后 |
| 数据库 | PRD + ARCH | ARCH 完成后 |

### 软阻塞机制

为避免任务过早阻塞，采用**软阻塞**机制：

1. **DESIGN 未完成时**：
   - 前端任务状态设为 `pending_design`（等待设计）
   - 后端任务正常拆分，状态为 `pending`

2. **ARCH 未完成时**：
   - 所有任务状态设为 `pending_arch`
   - 等待 ARCH 完成后，状态自动变为 `pending`

3. **任务依赖处理**：
   - 所有任务初始状态为 `pending`
   - 调用 `unlock` 命令时，检查依赖是否满足
   - 依赖未满足的任务，在 unlock 时显示被阻塞

4. **自动解锁**：
   - 当 DESIGN 或 ARCH 完成后，用户触发 `/dev TASK-XXX`
   - 系统自动检测依赖就绪，将 `pending_design` → `pending`
   - 当依赖任务完成时，调用 `python tasks.py unlock` 自动解锁

### 校验不通过时

- PRD 不存在 → 提示用户先执行 /pm

---

## 输入

阅读 PRD 和架构文档，理解完整需求。

### API 提取规则

从 `docs/architecture/api.md` 中提取任务相关的 API：
- 读取完整的 API 定义
- 根据任务描述，筛选相关的 API
- 提取格式：`{path, method, description}`，不包含完整请求/响应结构

> 这样做可以减少 token 消耗，完整定义在原文件中，Subagent 需要时可读取。

## 任务拆分

将需求拆解为可执行的任务，每个任务包含：

- **任务ID**: TASK-序号
- **任务描述**: 清晰的描述
- **输入**: 依赖的文件或数据
- **输出**: 产出的文件（必须使用下方目录约定中的路径，如 frontend/、backend/）
- **验收标准**: 可验证的完成条件
- **依赖任务**: 前置任务（如有）
- **依赖产出**: 依赖哪些角色的产出（见下方说明）
- **技术栈**: 必须明确指定，格式为 "技术 + 平台"（如 "Python + 后端", "Swift + iOS"）
- **相关 API**: 任务涉及的 API 摘要（从 api.md 提取）

### 目录约定（从 arch 输出读取）

目录结构由架构师在 arch 阶段定义，存储在 `docs/architecture/overview.md` 中。

split 执行时：
1. 读取 `docs/architecture/overview.md`
2. 提取"目录结构约定"表格
3. 使用表格中的路径作为 output

如果 overview.md 中没有目录约定，才使用默认约定：

| 技术栈 | 输出目录 |
|--------|---------|
| 前端 (React/Vue) | `frontend/` |
| 后端 (Python/Go/Java/Rust) | `backend/` |
| 移动端 (iOS/Android) | `ios/` 或 `android/` |
| 桌面端 | `desktop/` |

### 任务依赖产出

每个任务需声明依赖哪些角色的产出：

| 依赖标识 | 说明 | 检查路径 |
|----------|------|----------|
| ARCH | 技术架构、API 定义 | `docs/architecture/` 目录 |
| DESIGN | 界面设计稿、交互文档 | `docs/design/` 目录 |

#### 架构文件细分

ARCH 目录包含多个文件，DEV 阶段按需检查：

| 任务类型 | 需要的 ARCH 文件 |
|----------|-----------------|
| 前端 | `api.md` |
| 后端 | `api.md` + `data.md` |
| DevOps | `deploy.md` |

#### 依赖判断

- **前端页面任务** → 依赖 DESIGN + ARCH（设计稿 + API 定义）
- **后端 API 任务** → 依赖 ARCH（API 定义）
- **数据库任务** → 依赖 ARCH（数据架构）
- **任务拆分任务** → 无依赖（或可选 ARCH）

> 📌 前端与后端可并行开发，共享 ARCH 输出的 API 定义作为契约。

#### 示例

```json
{
  "tasks": [
    {
      "id": "TASK-001",
      "description": "开发登录页面",
      "tech_stack": "React + Web",
      "input": "docs/design/login.md",
      "output": "frontend/（从 arch 的目录约定中读取）",
      "depends_on": [],
      "depends_on_outputs": ["DESIGN", "ARCH"],
      "relevant_apis": [
        {"path": "/api/login", "method": "POST", "description": "用户登录"},
        {"path": "/api/logout", "method": "POST", "description": "用户登出"}
      ],
      "status": "pending"
    },
    {
      "id": "TASK-002",
      "description": "开发登录 API",
      "tech_stack": "Python + 后端",
      "input": "docs/architecture.md",
      "output": "backend/（从 arch 的目录约定中读取）",
      "depends_on": [],
      "depends_on_outputs": ["ARCH"],
      "relevant_apis": [
        {"path": "/api/login", "method": "POST", "description": "用户登录"}
      ],
      "status": "pending"
    }
  ]
}
```

### 技术栈选择

拆分任务时，必须明确每个任务的技术栈。从以下选项选择：

| 技术栈 | 调度的 Agent |
|--------|-------------|
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

> **注意**：
> - 数据库设计 → 在 ARCH 阶段完成
> - 测试 → 由 Subagent 在开发过程中执行

### 任务示例

```
TASK-001: 开发用户登录 API
  技术栈: Python + 后端
  Agent: dev-agent-python

TASK-002: 开发 iOS 登录页面
  技术栈: Swift + iOS
  Agent: dev-agent-ios

TASK-003: 编写单元测试
  技术栈: 测试
  Agent: test-agent
```

## 输出

使用脚本生成任务清单。

### 步骤

1. **初始化**：
   ```bash
   python .claude/skills/split/scripts/tasks.py init
   ```

2. **生成任务列表**：分析 PRD 和架构文档，确定任务列表

3. **批量添加任务**（推荐）：
   ```bash
   python .claude/skills/split/scripts/tasks.py batch < tasks.json
   ```

   > tasks.json 格式：JSON 数组，每个元素包含任务字段

4. **确认**：
   ```bash
   python .claude/skills/split/scripts/tasks.py status
   ```

### 使用脚本操作

```bash
# 初始化
python .claude/skills/split/scripts/tasks.py init

# 添加任务
python .claude/skills/split/scripts/tasks.py add TASK-001 "开发登录页面" React "frontend/"

# 查看状态
python .claude/skills/split/scripts/tasks.py status

# 查看详情
python .claude/skills/split/scripts/tasks.py get TASK-001
```

### tasks.json 格式

```json
{
  "version": "1.0",
  "generated_at": "2024-01-01T10:00:00Z",
  "tasks": [
    {
      "id": "TASK-001",
      "description": "任务描述",
      "input": "依赖的文件",
      "output": "frontend/ 或 backend/（必须使用目录约定中的路径）",
      "acceptance": "验收标准",
      "depends_on": [],
      "depends_on_outputs": [],
      "tech_stack": "Python",
      "relevant_apis": [
        {
          "path": "/api/login",
          "method": "POST",
          "description": "用户登录"
        }
      ],
      "status": "pending",
      "iteration": 0,
      "iterations": []
    }
  ]
}
```

> **Token 优化**：`relevant_apis` 字段只在 tasks.json 中存储任务涉及的 API 摘要（路径、方法、描述），不包含完整定义。完整 API 定义在 `docs/architecture/api.md` 中，由 Subagent 按需读取。

### 任务状态说明

| 状态 | 说明 | 可执行 |
|------|------|--------|
| `pending` | 等待开发（依赖已就绪） | ✅ |
| `pending_design` | 等待 DESIGN 完成 | ❌ |
| `pending_arch` | 等待 ARCH 完成 | ❌ |
| `in_progress` | 开发中 | ❌ |
| `pending_review` | 待审核 | ❌ |
| `pending_fix` | 需修复（审核不通过） | ✅ |
| `completed` | 已完成 | ❌ |
| `deployed` | 已部署 | ❌ |
| `deploy_failed` | 部署失败 | ❌ |

### 迭代记录格式

每次迭代后，任务增加迭代记录：

```json
{
  "iteration": 1,
  "subagent": "dev-agent-python",
  "review_result": "不通过",
  "feedback": "代码有安全漏洞，需要修复 X 和 Y",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## 确认机制

输出任务清单并等待确认：
```
📋 任务清单已生成

共 X 个任务：
- TASK-001: ...
- TASK-002: ...

确认无误后请回复"确认"。
```
