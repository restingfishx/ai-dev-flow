---
name: review
argument-hint: "[task-id]"
description: 审核员 - 代码审核与 GitHub PR 集成。用于需要审核代码、创建 pull request 或合并变更时。
disable-model-invocation: false
---

# 审核员指令

参数: $ARGUMENTS

## 阶段零：前置校验

### 必须满足的条件

1. **GitHub 登录状态**：
   - 运行 `gh auth status` 检查是否已登录
   - 未登录 → **引导用户先登录 GitHub**
   - 登录后继续

2. **tasks.json 存在**：确保任务清单已创建
3. **任务状态正确**：
   - 状态为 `pending_review`（待审核）
4. **任务存在**：指定的任务 ID 存在于 tasks.json 中
5. **代码已提交**：确认代码已提交到本地分支

### GitHub 登录引导

如果未登录，提示用户：

```
⚠️ GitHub 未登录

请先登录 GitHub：
1. 运行 `gh auth login`
2. 选择 HTTPS 或 SSH
3. 完成认证

登录后请再次触发 /review
```

### 校验不通过时

- 任务清单不存在 → 提示用户先执行 /split
- 状态不是 pending_review → 提示当前状态，询问用户是否继续
- 没有待审核任务 → 提示所有任务状态

---

## 阶段一：代码准备与推送

### 步骤 1：检查当前分支状态

```bash
# 查看当前分支
git branch --show-current

# 查看未提交的更改
git status
```

### 步骤 2：推送代码到远程

如果代码尚未推送：

```bash
# 推送到远程分支
git push -u origin <分支名>
```

### 步骤 3：创建 Pull Request

```bash
# 创建 PR
gh pr create \
  --title "[TASK-XXX] 任务描述" \
  --body "## 任务
描述

## 变更内容
- ...

## 审核要点
请审核以下内容..."
```

---

## 阶段二：GitHub 审核流程

### 步骤 1：创建 PR 后等待用户审核

输出 PR 链接后，提示用户审核：

```
🔍 PR 已创建，请审核

PR 链接：https://github.com/owner/repo/pull/123

请在 GitHub 上进行代码审核：
- 点击 "Add your review" 开始审核
- 选择 "Approve"（通过）或 "Request changes"（需修改）
- 点击 "Submit review" 提交

审核完成后，请回复我：
- "已通过" → 我将自动合并
- "需修改" + 具体问题 → 我将反馈给开发者
```

### 步骤 2：监听审核状态

等待用户回复时，定期检查 PR 状态：

```bash
# 检查当前 PR 状态
gh pr view <pr-number> --json state,mergeable,reviewDecision

# 检查 CI 检查结果
gh pr checks <pr-number>
```

### 步骤 3：处理审核结果

用户回复后，处理结果：

#### 审核通过（Approved）

1. 检查 CI 是否全部通过：
   ```bash
   gh pr checks <pr-number> --fail-fast
   ```

2. CI 通过后自动合并：
   ```bash
   gh pr merge <pr-number> --admin --squash --delete-branch
   ```

3. 输出成功消息

#### 需修改（Changes Requested）

1. 获取审核反馈：
   ```bash
   gh pr view <pr-number> --json comments
   ```

2. 解析反馈内容
3. 更新任务状态为 `pending_fix`
4. 将反馈记录到 tasks.json

#### 用户无响应超时

如果用户超过 5 分钟未响应：
- 提示用户尽快审核
- 保留 PR 链接供用户稍后审核

### 步骤 4：合并后本地操作

合并 PR 后，同步到本地：

```bash
# 切回主分支
git checkout main

# 拉取最新代码
git pull origin main

# 删除已合并的分支（如果远程分支仍存在）
git remote prune origin

# 清理本地分支（可选）
git branch -d <分支名>
```

---

## 阶段三：本地代码审核（备用）

如果无法在 GitHub 上审核，可以本地审核：

### 收集待审代码

获取 Subagent 完成的代码变更。

### 代码审核

从以下维度审核代码：

#### 代码质量
- 代码规范
- 命名清晰
- 复杂度合理

#### 安全检查
- 无安全漏洞
- 无硬编码敏感信息

#### 功能正确性
- 符合需求
- 边界条件处理

#### 最佳实践
- 错误处理
- 性能考虑
- 可维护性

---

## 阶段四：更新任务状态

根据审核结果，更新 tasks.json 中对应任务的状态：

### 审核通过

- 状态变更：`pending_review` → `completed`
- 记录审核结果到迭代历史
- 代码已合并到主分支

### 审核不通过

- 状态变更：`pending_review` → `pending_fix`
- 记录：
  - 审核结果
  - 具体反馈（问题描述 + 修改建议）
  - 时间戳

---

## 输出

### GitHub PR 模式输出

```
🔍 代码审核报告

任务：TASK-001
分支：feature/task-001-xxx
PR：#123

📋 审核流程：
1. ✅ 代码已推送到远程分支
2. ✅ PR 已创建：https://github.com/owner/repo/pull/123
3. ⏳ 等待人工审核...

请在 GitHub 上审核代码，审核完成后通知我：
- 批准 → 我将自动合并
- 需修改 → 请详细说明问题
```

### 本地审核模式输出

```
🔍 代码审核报告

任务：TASK-001
迭代：2

✅ 通过项：
- ...

⚠️ 需修改：
- 问题描述 → 建议修改方案

审核结果：[通过 / 需修改]
```

---

## 重要规则

- 优先使用 GitHub PR 进行代码审核
- 批量审核，不逐个文件确认
- 明确指出问题和建议修改方案
- 审核不通过时，反馈必须具体可执行
- 合并前必须确认 CI 检查通过
