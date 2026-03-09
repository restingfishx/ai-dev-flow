#!/bin/bash
# Pre-bash firewall hook - whitelist allowed commands
# 触发时机: Bash 命令执行前
# 输入: JSON 格式的工具调用信息
# 输出: 允许则退出 0，阻止则退出 2 并输出拒绝 JSON

set -e

# 读取 stdin 输入
INPUT=$(cat)

# 解析命令
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# 提取第一个命令（处理管道和链式命令）
FIRST_CMD=$(echo "$COMMAND" | awk '{print $1}')

# 白名单命令
ALLOWED_COMMANDS=(
  "git"
  "npm"
  "npx"
  "node"
  "python"
  "python3"
  "pip"
  "pip3"
  "uv"
  "poetry"
  "docker"
  "docker-compose"
  "kubectl"
  "helm"
  "terraform"
  "ansible"
  "make"
  "cmake"
  "qmake"
  "clang"
  "clang++"
  "gcc"
  "g++"
  "go"
  "rustc"
  "cargo"
  "swift"
  "flutter"
  "dart"
  "javac"
  "java"
  "gradle"
  "mvn"
  "bundle"
  "gem"
  "yarn"
  "pnpm"
  "bun"
  "deno"
  "pnpm"
  "vercel"
  "netlify"
  "gh"
  "curl"
  "wget"
  "tar"
  "unzip"
  "zip"
  "rsync"
  "ssh"
  "scp"
  "chmod"
  "chown"
  "mkdir"
  "rm"
  "cp"
  "mv"
  "cat"
  "echo"
  "printf"
  "ls"
  "cd"
  "pwd"
  "find"
  "grep"
  "awk"
  "sed"
  "jq"
  "yq"
  "xargs"
  "sort"
  "uniq"
  "head"
  "tail"
  "wc"
  "diff"
  "patch"
  "split"
  "x86_64-apple-darwin"
  "aarch64-apple-darwin"
)

# 检查命令是否在白名单中
is_allowed() {
  local cmd="$1"
  for allowed in "${ALLOWED_COMMANDS[@]}"; do
    if [[ "$cmd" == "$allowed" ]]; then
      return 0
    fi
  done
  return 1
}

# 额外允许的命令参数模式
ALLOWED_PATTERNS=(
  "^git "
  "^npm "
  "^npx "
  "^node "
  "^python "
  "^python3 "
  "^pip "
  "^pip3 "
  "^uv "
  "^docker "
  "^docker-compose "
  "^kubectl "
  "^gh "
  "^vercel "
  "^netlify "
  "^make "
  "^clang "
  "^clang\+\+ "
  "^gcc "
  "^g\+\+ "
  "^go "
  "^cargo "
  "^swift "
  "^flutter "
  "^javac "
  "^java "
  "^gradle "
  "^mvn "
  "^bundle "
  "^yarn "
  "^pnpm "
  "^bun "
  "^deno "
)

# 检查命令是否匹配允许的模式
matches_allowed_pattern() {
  local cmd="$1"
  for pattern in "${ALLOWED_PATTERNS[@]}"; do
    if echo "$cmd" | grep -qE "$pattern"; then
      return 0
    fi
  done
  return 1
}

# 检查是否包含危险操作
check_dangerous() {
  local cmd="$1"

  # 危险命令模式
  local DANGEROUS_PATTERNS=(
    "rm -rf /"
    "mkfs"
    "dd if="
    ":(){:|:&};:"
    "chmod 777"
    "chown -R"
    "> /dev/sda"
    "mv /"
    "fork()"
  )

  for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$cmd" | grep -qF "$pattern"; then
      echo "危险命令检测: $pattern"
      return 1
    fi
  done

  return 0
}

# 主逻辑
if is_allowed "$FIRST_CMD" || matches_allowed_pattern "$COMMAND"; then
  if check_dangerous "$COMMAND"; then
    exit 0
  else
    # 危险操作被阻止
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "检测到危险命令操作"
      }
    }'
    exit 2
  fi
else
  # 命令不在白名单中
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "命令不在白名单中: '"$FIRST_CMD"'"
    }
  }'
  exit 2
fi
