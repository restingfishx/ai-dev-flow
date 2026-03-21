# AI 开发流程

这是一个基于claude code，搭建的一套AI软件开发体系，主要特点有：
1. 角色分工明确。每个角色职责和能力更加聚焦，从而使各个环节的产出更加规范和专业。
2. 精细任务拆分。实现对任务的细粒度追踪，便于对某个功能点进行反复打磨（特别是开发编码阶段）。
3. 流程全程可控。有审核、反馈机制，用户掌握流程推进的主动权。

## 命令速查

| 命令 | 产出 |
|------|------|
| `/pm` | PRD 文档 |
| `/arch` | 架构设计 |
| `/design` | 界面设计 |
| `/split` | 任务清单 |
| `/dev TASK-XXX` | 开发 |
| `/review TASK-XXX 通过/不通过` | 审核 |
| `/deploy` | 部署 |
| `/status` | 任务状态 |
| `/iteration create <version>` | 创建迭代 |
| `/iteration switch <version>` | 切换迭代 |
| `/iteration list` | 列出迭代 |
| `/iteration status` | 查看迭代状态 |

## 链路

```
PM → PRD → [ARCH + DESIGN] → SPLIT → DEV → REVIEW → DEPLOY
```

## 迭代模式（可选）

### 什么是迭代模式？

迭代模式将项目分为多个版本（v1.0, v1.1, v2.0），每个迭代有独立的文档和任务。

执行 `python .claude/lib/iteration.py check` 查看当前迭代状态和路径

### 迭代命令

```bash
/iteration create v1.0     # 创建首个迭代
/iteration create v1.1    # 基于 v1.0 创建 v1.1
/iteration switch v1.0    # 切换到 v1.0
/iteration list           # 列出所有迭代
/iteration complete v1.0  # 完成迭代
/iteration status         # 查看当前状态
```

### 路径解析

执行 `python .claude/lib/iteration.py check` 查看实际路径

## 任务状态

```
pending/pending_design/pending_arch → in_progress → pending_review → completed → deployed
                                      ↓
                                 pending_fix → (修复)
```

### 状态说明

| 状态 | 说明 | 触发条件 |
|------|------|----------|
| `pending` | 待开始 | 任务刚创建或依赖已满足 |
| `pending_design` | 等待设计 | 需要 DESIGN 产出但尚未完成 |
| `pending_arch` | 等待架构 | 需要 ARCH 产出但尚未完成 |
| `in_progress` | 开发中 | 开始执行开发 |
| `pending_review` | 待审核 | PR 已创建，等待审核 |
| `pending_fix` | 待修复 | 审核不通过，需要修复 |
| `completed` | 已完成 | 审核通过 |
| `deployed` | 已部署 | 部署成功 |
| `deploy_failed` | 部署失败 | 部署未成功 |

## Worktree

```
worktrees/task-XXX/
```

## 文档

执行 `python .claude/lib/iteration.py check` 获取实际路径


# 通用约定

所有成员必须遵守以下约定：

## 目录约定

| 目录 | 说明 |
|------|------|
| `worktrees/<task-id>/` | Git Worktree 开发目录 |
| `docs/prd.md` | PRD 需求文档 |
| `docs/architecture/` | 架构文档 |
| `docs/design/` | 设计文档 |
| `tasks.json` | 任务清单 |
| `subtasks/` | 子任务目录 |

## 任务 ID 格式

- 格式：`TASK-xxx`（如 TASK-001, TASK-002）

## 任务状态

| 状态 | 说明 |
|------|------|
| `pending` | 待开始 |
| `pending_design` | 等待设计 |
| `pending_arch` | 等待架构 |
| `in_progress` | 开发中 |
| `pending_review` | 待审核 |
| `pending_fix` | 待修复 |
| `completed` | 已完成 |
| `deployed` | 已部署 |
| `deploy_failed` | 部署失败 |

## 脚本约定

| 脚本 | 路径 |
|------|------|
| iteration.py | `.claude/lib/iteration.py` |
| tasks.py | `.claude/skills/split/scripts/tasks.py` |
| progress.py | `.claude/agents/scripts/progress.py` |

## 迭代模式

- 配置文件：`.ai-dev-flow/config.json`
- 标识文件：`.ai-dev-flow/.iteration`（存在表示启用迭代模式）
- 获取迭代信息：`python .claude/lib/iteration.py check`