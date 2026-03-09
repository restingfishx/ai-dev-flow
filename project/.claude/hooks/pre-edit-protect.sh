#!/bin/bash
# Pre-edit protect hook - protect sensitive files
# 触发时机: Edit/Write 工具执行前
# 输入: JSON 格式的工具调用信息
# 输出: 允许则退出 0，阻止则退出 2 并输出拒绝 JSON

set -e

# 读取 stdin 输入
INPUT=$(cat)

# 解析文件路径
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# 获取当前工作目录
CWD=$(echo "$INPUT" | jq -r '.cwd // .')

# 构建完整路径
if [[ "$FILE_PATH" != /* ]]; then
  FULL_PATH="$CWD/$FILE_PATH"
else
  FULL_PATH="$FILE_PATH"
fi

# 保护的文件模式
PROTECTED_PATTERNS=(
  ".env"
  ".env.local"
  ".env.production"
  ".env.*.local"
  "*.key"
  "*.pem"
  "*.crt"
  "*.p12"
  "*.pfx"
  "credentials.json"
  "secrets.yaml"
  "secrets.yml"
  "secrets.json"
  "id_rsa"
  "id_ed25519"
  "*.secret"
  "*.password"
  ".npmrc"
  ".pypirc"
  ".aws/credentials"
  ".docker/config.json"
  "service-account.json"
  "*.googleusercontent.com"
  "/etc/shadow"
  "/etc/passwd"
  ".ssh/config"
  ".git-credentials"
)

# 额外保护：项目特定敏感文件
PROJECT_PROTECTED=(
  "project/.env"
  "project/.env.local"
  "project/secrets/"
  "project/credentials/"
  "*/.env"
  "*/.env.*"
  "**/secrets/**"
  "**/credentials/**"
)

# 检查文件是否匹配保护模式
is_protected() {
  local file="$1"

  for pattern in "${PROTECTED_PATTERNS[@]}"; do
    # 支持通配符匹配
    if [[ "$pattern" == *\** ]]; then
      local base_pattern="${pattern//\*/.*}"
      if [[ "$file" == $base_pattern ]] || [[ "$file" == *"$pattern"* ]]; then
        return 0
      fi
    else
      if [[ "$file" == *"$pattern"* ]]; then
        return 0
      fi
    fi
  done

  # 检查是否为 gitignored 的敏感文件
  if [ -f "$file" ]; then
    local dir
    dir=$(dirname "$file")
    if [ -f "$dir/.gitignore" ]; then
      local filename
      filename=$(basename "$file")
      if grep -q "$filename" "$dir/.gitignore" 2>/dev/null; then
        # 检查是否包含敏感关键词
        if echo "$filename" | grep -qiE "secret|password|key|token|credential"; then
          return 0
        fi
      fi
    fi
  fi

  return 1
}

# 检查文件内容是否包含敏感信息
check_sensitive_content() {
  local file="$1"

  if [ ! -f "$file" ]; then
    return 0
  fi

  # 检查文件头部是否包含敏感关键词
  local first_lines
  first_lines=$(head -c 1024 "$file" 2>/dev/null || echo "")

  local sensitive_keywords=(
    "-----BEGIN PRIVATE KEY-----"
    "-----BEGIN RSA PRIVATE KEY-----"
    "-----BEGIN OPENSSH PRIVATE KEY-----"
    "aws_access_key_id"
    "aws_secret_access_key"
    "api_key"
    "apikey"
    "password"
    "client_secret"
    "refresh_token"
  )

  for keyword in "${sensitive_keywords[@]}"; do
    if echo "$first_lines" | grep -qi "$keyword"; then
      return 1
    fi
  done

  return 0
}

# 主逻辑
if is_protected "$FULL_PATH"; then
  # 文件受保护，检查是否尝试写入敏感内容
  if [ "$INPUT" != "" ]; then
    # 对于 Write 操作，检查新内容
    local tool_name
    tool_name=$(echo "$INPUT" | jq -r '.tool_name // empty')

    if [ "$tool_name" == "Write" ]; then
      # 检查是否包含敏感内容（如果提供了内容）
      local new_content
      new_content=$(echo "$INPUT" | jq -r '.tool_input.content // empty' 2>/dev/null || echo "")

      if [ -n "$new_content" ]; then
        local sensitive_keywords=(
          "-----BEGIN"
          "PRIVATE KEY"
          "RSA PRIVATE KEY"
          "api[_-]?key"
          "password"
          "secret"
          "token"
          "credential"
        )

        for keyword in "${sensitive_keywords[@]}"; do
          if echo "$new_content" | grep -qiE "$keyword"; then
            jq -n '{
              hookSpecificOutput: {
                hookEventName: "PreToolUse",
                permissionDecision: "deny",
                permissionDecisionReason: "检测到敏感内容，禁止写入: '"$keyword"'"
              }
            }'
            exit 2
          fi
        done
      fi
    fi
  fi

  # 文件受保护但内容安全，允许编辑
  exit 0
else
  # 文件不受保护，检查内容安全
  if check_sensitive_content "$FULL_PATH"; then
    exit 0
  else
    # 文件包含敏感内容
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "文件包含敏感内容，禁止编辑: '"$FULL_PATH"'"
      }
    }'
    exit 2
  fi
fi
