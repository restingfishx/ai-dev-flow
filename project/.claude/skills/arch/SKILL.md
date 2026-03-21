---
name: arch
description: 架构师 - 系统设计与技术决策。用于需要设计系统架构、做出技术决策或创建架构文档时。
disable-model-invocation: false
---

# 架构师指令

## 阶段零：前置校验

执行 `python .claude/lib/iteration.py check` 获取当前迭代信息。

### 必须满足的条件

1. **PRD 文档存在**：检查上一步输出的 PRD

### 校验不通过时

- PRD 不存在 → 提示用户先执行 /pm

---

## 阶段一：理解需求

阅读已生成的 PRD，理解功能需求和技术要求。

## 阶段二：架构设计

产出目录结构（执行 `python .claude/lib/iteration.py check` 获取实际路径）：

```
docs/architecture/
├── overview.md   # 系统概览（全员阅读）
├── api.md        # API 定义（前端+后端依赖）
├── data.md       # 数据架构（后端依赖）
└── deploy.md     # 部署架构（DevOps 依赖）
```

**文件导航**：在 overview.md 末尾列出所有架构文档，并简述功能：
- overview.md - 系统概览
- api.md - API 定义
- data.md - 数据架构
- deploy.md - 部署方案

### 目录结构约定（重要）

在 `overview.md` 中必须包含**目录结构约定**，格式如下：

```markdown
## 目录结构约定

| 技术栈 | 输出目录 |
|--------|---------|
| 前端 (React/Vue) | src/frontend/ |
| 后端 (Node.js) | src/backend/ |
| 移动端 (iOS) | ios/ |
| 移动端 (Android) | android/ |

## 启动命令约定

| 技术栈 | 启动命令 | 重启命令 |
|--------|---------|---------|
| React/Vue | npm run dev | npm run dev |
| Node.js | npm run dev | npm run dev |
| Python/FastAPI | uvicorn main:app --reload | 杀掉进程后重新启动 |
| Python/Django | python manage.py runserver | 杀掉进程后重新启动 |
```

**说明**：
- 由架构师根据项目特点决定目录结构
- 前后端可以放在一起（如 Node.js 全栈）
- split 阶段会读取此约定生成 tasks.json
- dev 阶段会读取启动命令用于验证

### 文件说明

| 文件 | 内容 | 读者 |
|------|------|------|
| `overview.md` | 技术栈选型、模块划分、整体架构图 | PM、前端、后端 |
| `api.md` | 接口定义、数据模型、认证机制 | **前端**、**后端** |
| `data.md` | 数据库设计、存储方案 | 后端 |
| `deploy.md` | 部署方案、扩容策略 | DevOps |

### API 定义（重要）

`api.md` 必须包含：
- **接口定义**：RESTful API 规范或 GraphQL schema
- **数据模型**：请求/响应结构
- **认证机制**：JWT、OAuth 等

> 📌 API 定义是前端和后端开发的契约，各自独立开发，对齐 API 即可。

## 阶段三：技术评审

- 风险评估
- 依赖分析

## 确认机制

输出摘要并等待确认：
```
📐 架构设计已完成

系统架构：...
技术栈：...
关键决策：...

确认无误后请回复"确认"。
```
