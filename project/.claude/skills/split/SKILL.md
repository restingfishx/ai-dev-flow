---
name: split
description: 任务分解师 - 将需求拆解为可执行任务。用于需要将需求拆解为任务清单并明确验收标准时。
disable-model-invocation: false
---

# 任务分解师指令

## 阶段零：前置校验

### 必须满足的条件

1. **PRD 文档存在**：确保 PM 阶段已完成，PRD 文档已生成
2. **架构文档存在**（可选但推荐）：ARCH 阶段的架构文档

### 校验不通过时

- PRD 不存在 → 提示用户先执行 /pm
- 架构文档缺失 → 提示可能影响技术决策，是否继续

---

## 输入

阅读 PRD 和架构文档，理解完整需求。

## 任务拆分

将需求拆解为可执行的任务，每个任务包含：

- **任务ID**: TASK-序号
- **任务描述**: 清晰的描述
- **输入**: 依赖的文件或数据
- **输出**: 产出的文件（必须包含目录路径，见下方目录约定）
- **验收标准**: 可验证的完成条件
- **依赖任务**: 前置任务（如有）
- **依赖产出**: 依赖哪些角色的产出（见下方说明）
- **技术栈**: 必须明确指定，格式为 "技术 + 平台"（如 "Python + 后端", "Swift + iOS"）

### 目录约定

不同技术栈的代码放在不同目录：

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

### 任务依赖产出

每个任务需声明依赖哪些角色的产出：

| 依赖标识 | 说明 | 角色 |
|----------|------|------|
| ARCH | 技术架构、API 定义 | 架构师 |
| DESIGN | 界面设计稿、交互文档 | 设计师 |

#### 依赖判断

- **前端页面任务** → 依赖 DESIGN（需要设计稿）
- **后端 API 任务** → 依赖 ARCH（需要 API 定义）
- **数据库任务** → 依赖 ARCH（需要数据架构）
- **任务拆分任务** → 无依赖（或可选 ARCH）

#### 示例

```json
{
  "tasks": [
    {
      "id": "TASK-001",
      "description": "开发登录页面",
      "tech_stack": "React + Web",
      "input": "docs/design/login.md",
      "output": "frontend/web/src/pages/Login/",
      "depends_on": [],
      "depends_on_outputs": ["DESIGN"],
      "status": "pending"
    },
    {
      "id": "TASK-002",
      "description": "开发登录 API",
      "tech_stack": "Python + 后端",
      "input": "docs/architecture.md",
      "output": "backend/api/python/user/",
      "depends_on": [],
      "depends_on_outputs": ["ARCH"],
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

> **注意**：
> - 数据库设计 → 在 ARCH 阶段完成
> - DevOps → 用户单独操作
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

生成任务清单文件：
- TASKS.md (人类可读)
- tasks.json (程序可读)

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
      "output": "产出的文件",
      "acceptance": "验收标准",
      "depends_on": [],
      "depends_on_outputs": [],
      "tech_stack": "Python",
      "status": "pending",
      "iteration": 0,
      "iterations": []
    }
  ]
}
```

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
