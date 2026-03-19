---
name: deploy
argument-hint: "[environment]"
description: 运维 - 应用部署与发布。用于需要部署应用、管理发布或验证部署结果时。
disable-model-invocation: false
---

# 运维指令

参数: $ARGUMENTS

## 阶段零：前置校验

### 必须满足的条件

1. **GitHub 登录状态**（如需 GitHub 操作）：
   - GitHub 登录检查（dev 阶段已处理主要操作，此处仅用于 CI 检查等）
   - 运行 `gh auth status` 检查是否已登录
   - 未登录 → 引导用户登录
   - 登录后继续

2. **tasks.json 存在**：确保任务清单已创建
3. **所有任务已完成**：
   - 所有任务状态为 `completed` 或 `deployed`
   - 无 `pending`、`pending_design`、`pending_arch`、`in_progress`、`pending_review`、`pending_fix` 状态的任务
4. **GitHub 仓库已初始化**（如需推送到远程）：
   - 检查 `git remote -v` 确认远程仓库已配置

### GitHub 登录引导

如果未登录，提示用户：

```
⚠️ GitHub 未登录

请先登录 GitHub：
1. 运行 `gh auth login`
2. 选择 HTTPS 或 SSH
3. 完成认证

登录后请再次触发 /deploy
```

### GitHub 仓库初始化

如果远程仓库未配置，提示用户：

```
⚠️ GitHub 仓库未初始化

请先创建或连接 GitHub 仓库：
1. 本地已有项目 → 运行 `gh repo create` 或手动添加 remote
2. 新项目 → 在 GitHub 创建后添加到本地

完成后请再次触发 /deploy
```

### 校验不通过时

- 存在未完成任务 → 列出所有未完成任务及其状态
- 存在阻塞任务 → 提示需要先解决阻塞

---

## 阶段一：准备部署

### CI 状态检查（如使用 GitHub Actions）

在部署前检查所有相关 PR 的 CI 状态：

```bash
# 检查最近合并的 PR 的 CI 状态
gh run list --limit 5

# 检查特定 PR 的 CI 状态
gh pr checks <pr-number>
```

**如果 CI 未通过**：
- 提示用户 CI 失败的原因
- 暂停部署流程
- 建议用户先修复 CI 问题

### 确认清单

- [ ] 代码已通过审核
- [ ] 所有 CI 检查通过
- [ ] 测试通过
- [ ] 配置文件就绪

## 阶段二：执行部署

根据项目技术栈选择部署方式：

### 静态网站

```bash
# Vercel
vercel --prod

# Netlify
netlify deploy --prod

# GitHub Pages
npm run deploy
```

### Docker 容器

```bash
# 构建镜像
docker build -t <镜像名> .

# 推送镜像
docker push <镜像名>

# 部署到服务器
docker-compose up -d
```

### Kubernetes

```bash
# 应用部署
kubectl apply -f deployment.yaml

# 检查状态
kubectl get pods
```

### Serverless

```bash
# AWS Lambda
serverless deploy --stage prod

# Vercel
vercel --prod
```

### 询问用户

如果不确定使用哪种部署方式，询问用户选择。

## 阶段三：验证

- 健康检查
- 功能验证

## 回滚（如需要）

如遇问题，执行回滚并告警。

## 阶段四：更新状态

根据部署结果，更新 tasks.json 中任务状态：

### 部署成功

- 状态变更：`completed` → `deployed`
- 记录部署时间、版本号

### 部署失败

- 状态变更：`completed` → `deploy_failed`
- 记录错误信息
- 触发回滚（如需要）

### 状态流转

```
completed → deployed
         ↘_ deploy_failed → 回滚
```

## 输出

```
🚀 部署报告

环境：...
状态：成功/失败
版本：...
耗时：...

健康检查：✅/❌
```
