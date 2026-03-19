# 添加新 Dev Agent 指南

本文档说明如何在项目中添加新的开发 Agent。

## 步骤概览

```
1. 创建 Agent 文件
2. 添加通用模板引用
3. 定义特有能力
4. 更新 dev skill 映射（如需要）
5. 测试验证
```

---

## 步骤 1：创建 Agent 文件

在 `.claude/agents/` 目录下创建新文件：

```bash
# 文件命名规范：dev-agent-[技术栈].md
touch dev-agent-[技术栈].md
```

## 步骤 2：编写 Agent 内容

```markdown
---
name: dev-agent-[技术栈]
description: [技术栈] 开发专家。当需要[具体开发场景]时调用此代理。
tools: Read, Edit, Write, Glob, Grep, Bash
model: sonnet
permissionMode: acceptEdits
---

# [技术栈] 开发 Agent

负责 [技术栈] 的开发工作。

## 特有能力

- 能力 1
- 能力 2
- 能力 3

## 验证方式

完成开发后，必须验证代码可以运行：

```bash
# 验证命令示例
<验证命令>
```

验证通过后才能 git commit。

## 使用场景

当任务涉及 [技术栈] 开发时调度此 Agent。
```

### 关键要素

| 要素 | 说明 |
|------|------|
| `name` | Agent 名称，格式：`dev-agent-[技术栈]`，小写字母+连字符 |
| `description` | 完整句子，说明何时调用此代理，以"当需要...时调用此代理"结尾 |
| `tools` | 最小工具集：`Read, Edit, Write, Glob, Grep, Bash` |
| `model` | 推荐 `sonnet` |
| `permissionMode` | 可选 `acceptEdits` 减少交互提示 |
| `> 引用` | 必须引用通用模板 |
| `## 特有能力` | 该技术栈特有的能力 |
| `## 验证方式` | 必须包含验证命令 |
| `## 使用场景` | 何时使用此 Agent |

## 步骤 3：更新 dev skill 映射（如需要）

如果新技术栈需要被 dev skill 自动识别，编辑 `.claude/skills/dev/SKILL.md`：

在"技术栈选择"表格中添加新映射：

```markdown
| 技术栈关键词 | 调度的 Agent |
|-------------|-------------|
| [关键词] | dev-agent-[技术栈] |
```

---

## 示例：添加 SwiftUI Agent

### 1. 创建文件

```bash
dev-agent-swiftui.md
```

### 2. 编写内容

```markdown
---
name: dev-agent-swiftui
description: SwiftUI 开发 Agent
model: sonnet
---

# SwiftUI 开发 Agent

> 通用机制见 `_template.md`

负责 SwiftUI 界面开发。

## 特有能力

- SwiftUI 声明式 UI
- MVVM 架构
- 状态管理 (@State, @Binding, @ObservedObject)
- 动画与过渡
- 跨平台 (iOS, macOS, watchOS, tvOS)

## 使用场景

当任务涉及 SwiftUI 开发时调度此 Agent。
```

### 3. 更新 dev skill（如需要）

在 dev skill 的映射表中添加：

```markdown
| SwiftUI | dev-agent-swiftui |
```

---

## 验证清单

添加完成后，确认：

- [ ] Agent 文件存在于 `.claude/agents/` 目录
- [ ] 包含通用模板引用 `> 通用机制见 _template.md`
- [ ] 定义了特有能力
- [ ] dev skill 映射已更新（如需要自动识别）
- [ ] 文件格式正确（YAML frontmatter 有效）

---

## 相关文件

| 文件 | 作用 |
|------|------|
| `.claude/agents/_template.md` | 通用模板 |
| `.claude/skills/dev/SKILL.md` | 开发调度逻辑 |
| `.claude/agents/dev-agent-*.md` | 现有 Agent 示例 |
