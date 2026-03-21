# Iteration - 迭代管理

## 用途

用于管理项目迭代版本，支持创建、切换、列出和完成迭代。

## 路径约定

- 配置文件：`.ai-dev-flow/config.json`
- 迭代标识：`.ai-dev-flow/.iteration`（迭代模式启用时存在）
- 迭代目录：`v1.0/`, `v1.1/`, `v2.0/` 等
- 根目录文件（不受迭代影响）：`.git`, `worktrees`, `.ai-dev-flow`

## 工作原理

迭代模式通过以下文件管理版本：
- `.ai-dev-flow/config.json` - 配置文件
  - `current_iteration`: 当前活跃的迭代版本
  - `iterations`: 所有迭代的列表及状态
- `.ai-dev-flow/.iteration` - 迭代模式标识文件（启用时自动创建）

路径解析模块 `.claude/lib/iteration.py` 会自动检测迭代模式：
1. 检查标识文件是否存在
2. 检查配置文件是否有 current_iteration

检测到任一条件满足时，自动将相对路径解析到当前迭代目录下：
- `docs/prd.md` → `v1.0/docs/prd.md`（当前迭代为 v1.0 时）
- `tasks.json` → `v1.0/tasks.json`
- `worktrees/` → `worktrees/`（根目录文件，不受迭代影响）

## 可用命令

### 创建迭代

```
/iteration create <version>
```

基于最新迭代创建新版本。首次创建时从根目录复制现有文件结构。

示例：
- `/iteration create v1.0` - 创建首个迭代
- `/iteration create v1.1` - 基于 v1.0 创建 v1.1

### 列出迭代

```
/iteration list
```

列出所有迭代及其状态。

### 切换迭代

```
/iteration switch <version>
```

切换当前活跃迭代。切换后所有流程将在新迭代目录下工作。

### 完成迭代

```
/iteration complete [version]
```

标记迭代为完成状态。省略版本号时完成当前迭代。

### 查看当前状态

```
/iteration status
```

显示当前迭代状态。

## 迭代状态

- `pending`: 初始状态
- `in_progress`: 进行中
- `completed`: 已完成

## 注意事项

1. 首次使用需先创建迭代：`/iteration create v1.0`
2. 根目录文件（如 `worktrees/`）不受迭代影响，始终在项目根目录
3. 切换迭代后，之前迭代的工作目录仍然保留
4. 建议每个迭代完成后再创建下一个迭代
