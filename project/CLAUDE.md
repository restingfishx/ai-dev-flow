# 项目开发体系规范

## 核心原则

1. **线性流程**：每个阶段完成后，经用户确认方可进入下一阶段
2. **不懂就问**：遇到任何不确定的问题，必须提问，不得擅自决策
3. **审核机制**：Subagent 完成批量编码后，通过 `/review` 进行人工审核
4. **任务追踪**：所有任务状态记录在 TASKS.md 和 tasks.json 中
5. **链路畅通**：Skill 调度 → Subagent 执行 → 结果回传 → 状态更新

## 角色分工

### 阶段角色（Skill）

| 角色 | 触发命令 | 产出 | 与其他角色关系 |
|------|----------|------|---------------|
| PM | `/pm` | PRD 文档 | - |
| ARCH | `/arch` | 架构设计文档 | 与 DESIGN 并行 |
| DESIGN | `/design` | 界面设计文档 | 与 ARCH 并行 |
| SPLIT | `/split` | 任务清单 | 依赖 PM + (ARCH/DESIGN) |
| DEV | `/dev` | 调度开发 | 依赖产出声明 |
| REVIEW | `/review` | 代码审核 | - |
| OPS | `/deploy` | 部署 | 依赖所有任务完成 |

### 执行角色（Subagent）

自动发现并调度，根据项目技术栈匹配。

## 任务拆分标准

每个任务必须包含：

- 任务ID（TASK-序号）
- 任务描述
- 输入（依赖的文件或数据）
- 输出（产出的文件）
- 验收标准
- 依赖任务（如有）
- 技术栈（如适用）

## 任务状态定义

| 状态 | 说明 | 触发条件 | 自动变更 |
|------|------|----------|----------|
| pending | 待开始 | split 创建任务后 | - |
| blocked | 被阻塞 | 依赖产出未就绪 | ✅ dev 自动设置 |
| in_progress | 开发中 | dev 开始执行 | ✅ 自动 |
| pending_review | 待审核 | dev 完成执行 | ✅ 自动 |
| pending_fix | 待修复 | review 不通过 | ✅ 自动 |
| completed | 已完成 | review 通过 | ✅ 自动 |
| deployed | 已部署 | deploy 成功 | ✅ 自动 |
| deploy_failed | 部署失败 | deploy 失败 | ✅ 自动 |

## 流程链路

```
DEV → in_progress → pending_review → REVIEW → completed → /deploy → deployed
                                      ↓
                                pending_fix → DEV（修复）
```

## 任务迭代机制

支持反复打磨，每次迭代记录：
- 迭代次数
- 使用的 Subagent
- 审核结果
- 反馈内容
- 时间戳

## 开发流程链路

```
PM → PRD

PM → PRD
  ├─→ ARCH（技术架构）→ 架构文档
  └─→ DESIGN（界面设计）→ 设计文档

SPLIT（基于 PRD + ARCH + DESIGN）
         → 任务清单 (TASK-001, TASK-002, ...)
         → 标注每个任务的依赖产出 (ARCH / DESIGN)

DEV TASK-001
  → 检查依赖产出是否就绪
  → 调度对应 Agent
         状态: in_progress → pending_review

REVIEW → 审核反馈
  [通过] → 状态: completed
  [不通过] → 状态: pending_fix, 记录反馈

所有任务 completed → /deploy → 部署
         状态: pending_deploy → deployed
```

### 任务依赖规则

| 任务类型 | 依赖产出 |
|----------|----------|
| 前端页面 | DESIGN |
| 后端 API | ARCH |
| 数据库 | ARCH |
| DevOps | ARCH |

## 重要规则

- 未经用户确认，不得进入下一阶段
- 遇到不明确的问题，必须提问
- 批量编码后统一审核，不逐个 diff 确认
- 扩展技术栈：创建新的 Subagent，无需修改 Skill
