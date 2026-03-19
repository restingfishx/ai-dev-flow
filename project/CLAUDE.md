# AI 开发流程

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

## 链路

```
PM → PRD → [ARCH + DESIGN] → SPLIT → DEV → REVIEW → DEPLOY
```

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

- `docs/prd.md`
- `docs/architecture/`
- `docs/design/`
- `tasks.json`
