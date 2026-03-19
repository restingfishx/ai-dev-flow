---
name: review
argument-hint: "[task-id] [审核结果]"
description: 审核员 - 代码审核结果处理。用于需要处理代码审核结果时。
disable-model-invocation: false
---

# 审核员指令

参数: $ARGUMENTS

格式：`/review TASK-XXX [通过|不通过] [原因]`

示例：
- `/review TASK-001 通过`
- `/review TASK-001 不通过 代码有安全漏洞`

## 阶段零：前置校验

### 必须满足的条件

1. **tasks.json 存在**：确保任务清单已创建
2. **任务状态正确**：状态为 `pending_review`（待审核）
3. **任务存在**：指定的任务 ID 存在于 tasks.json 中

### 校验不通过时

- 任务清单不存在 → 提示用户先执行 /split
- 状态不是 pending_review → 提示当前状态
- 没有待审核任务 → 使用 `/status` 查看所有任务状态
- **如果用户没有填原因，需要引导他填写原因**

---

## 阶段一：解析审核结果

### 解析用户输入

用户输入格式：
- `通过` → 审核通过
- `不通过 <原因>` → 审核不通过，需要修复

### 解析示例

| 用户输入 | 结果 | 原因 |
|----------|------|------|
| `/review TASK-001 通过` | 通过 | - |
| `/review TASK-001 不通过 代码有bug` | 不通过 | 代码有bug |
| `/review TASK-001` | 提示用户提供结果 | - |

---

## 阶段二：更新任务状态

### 前置：进入 Worktree

```bash
cd worktrees/<task-id>
```

### 审核通过

1. 在 worktree 中提交代码：
   ```bash
   git add -A
   git checkout -b temp/<task-id>
   git commit -m "[<task-id>] <description>"
   ```

2. 推送本地分支并创建 PR：
   ```bash
   # 推送本地分支
   git push -u origin temp/<task-id>

   # 创建 PR（目标：release）
   gh pr create --title "[<task-id>] <description>" --body "## 任务描述\n<description>\n\n## 审核要点\n请审核代码" --base release
   ```

3. 合并 PR 到 release 分支：
   ```bash
   # 切到 release 分支
   git checkout release
   git pull origin release

   # 合并临时分支
   git merge temp/<task-id> --no-edit

   # 推送合并
   git push origin release

   # 删除远程分支（可选）
   git push origin --delete temp/<task-id>
   ```

3. 切回主目录并拉取 release 最新代码：
   ```bash
   cd ../..
   git checkout release
   git pull origin release
   ```

4. 更新任务状态：
   ```bash
   python .claude/skills/split/scripts/tasks.py update <task-id> completed
   python .claude/skills/split/scripts/tasks.py iter <task-id> review "通过" ""
   python .claude/skills/split/scripts/tasks.py unlock
   ```

输出：
```
✅ TASK-001 审核通过
✅ 已合并到 release 分支
✅ 已拉取 release 最新代码
状态已更新：pending_review → completed
🔓 已解锁依赖此任务的其他任务
```

### 审核不通过

继续保持在 worktree 下，更新状态为 pending_fix：

```bash
python .claude/skills/split/scripts/tasks.py update <task-id> pending_fix
python .claude/skills/split/scripts/tasks.py iter <task-id> review "不通过" "<反馈>"
```

输出：
```
🔧 TASK-001 审核不通过
原因：<用户提供的理由>
状态已更新：pending_review → pending_fix
保持在 worktree 下，请执行 /dev TASK-001 进行修复
```

---

## 阶段三：通知用户后续操作

### 审核通过

如果任务还有待审核的其他任务：
```
还有 X 个任务待审核：
- TASK-002: ...
- TASK-003: ...
```

### 审核不通过

```
修复后请再次执行 /review TASK-XXX 告知审核结果
```

---

## 输出格式

### 成功

```
✅ 审核结果已记录

任务：TASK-XXX
结果：通过/不通过
原因：<原因（如有）>
状态：pending_review → completed/pending_fix
```

### 错误

```
❌ 无法处理审核结果

原因：<具体错误>
```

---

## 重要规则

- **只处理用户告知的审核结果**：用户说通过就通过，说不通过就不通过
- **必须明确告知结果**：通过/不通过 + 原因（不通过时）
