#!/bin/bash
# Post-edit quality check hook
# 触发时机: Edit/Write 工具执行成功后
# 输入: JSON 格式的工具调用信息
# 输出: 退出码 0 表示继续，2 表示阻止

set -e

# 读取 stdin 输入
INPUT=$(cat)

# 解析文件路径和工具名
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
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

# 检查文件是否存在
if [ ! -f "$FULL_PATH" ]; then
  exit 0
fi

# 获取文件扩展名
EXTENSION="${FULL_PATH##*.}"
FILENAME=$(basename "$FULL_PATH")

# 检查文件大小的异常情况（可能存在问题）
FILE_SIZE=$(stat -f%z "$FULL_PATH" 2>/dev/null || stat -c%s "$FULL_PATH" 2>/dev/null || echo "0")

# 超过 1MB 的文件跳过检查
if [ "$FILE_SIZE" -gt 1048576 ]; then
  exit 0
fi

# 质量检查函数
check_quality() {
  local file="$1"
  local ext="$2"
  local name="$3"

  # 根据文件类型执行不同的检查
  case "$ext" in
    js|jsx|ts|tsx)
      # JavaScript/TypeScript 检查
      if command -v npx &> /dev/null; then
        # 检查基本语法（可选，耗时）
        # npx --yes acorn --silent "$file" 2>/dev/null || true
        :
      fi
      ;;

    py)
      # Python 检查
      if command -v python3 &> /dev/null; then
        # 检查语法
        python3 -m py_compile "$file" 2>/dev/null || {
          echo "Python 语法错误"
          return 1
        }
      fi
      ;;

    json)
      # JSON 检查
      if command -v jq &> /dev/null; then
        jq empty "$file" 2>/dev/null || {
          echo "JSON 格式错误"
          return 1
        }
      fi
      ;;

    yaml|yml)
      # YAML 检查
      if command -v python3 &> /dev/null; then
        python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null || {
          echo "YAML 格式错误"
          return 1
        }
      elif command -v yq &> /dev/null; then
        yq '.' "$file" > /dev/null 2>&1 || {
          echo "YAML 格式错误"
          return 1
        }
      fi
      ;;

    md)
      # Markdown 检查（可选）
      # 检查常见的 Markdown 语法问题
      if command -v python3 &> /dev/null; then
        # 检查未闭合的代码块
        local code_block_count
        code_block_count=$(grep -c '```' "$file" 2>/dev/null || echo "0")
        if [ $((code_block_count % 2)) -ne 0 ]; then
          echo "警告: Markdown 代码块未闭合"
        fi
      fi
      ;;

    sh|bash|zsh)
      # Shell 脚本检查
      if command -v bash &> /dev/null; then
        bash -n "$file" 2>/dev/null || {
          echo "Shell 脚本语法错误"
          return 1
        }
      fi
      ;;

    go)
      # Go 检查
      if command -v gofmt &> /dev/null; then
        gofmt -l "$file" 2>/dev/null | grep -q . && {
          echo "Go 代码格式不符合 gofmt 标准"
          return 1
        }
      fi
      ;;

    rs)
      # Rust 检查
      if command -v rustfmt &> /dev/null; then
        rustfmt --check "$file" 2>/dev/null || {
          echo "Rust 代码格式不符合 rustfmt 标准"
          return 1
        }
      fi
      ;;

    java)
      # Java 检查
      if command -v javac &> /dev/null; then
        javac -Xlint:none "$file" 2>/dev/null || {
          echo "Java 编译错误"
          return 1
        }
      fi
      ;;

    swift)
      # Swift 检查
      if command -v swiftc &> /dev/null; then
        swiftc -parse "$file" 2>/dev/null || {
          echo "Swift 语法错误"
          return 1
        }
      fi
      ;;
  esac

  return 0
}

# 执行质量检查
if check_quality "$FULL_PATH" "$EXTENSION" "$FILENAME"; then
  # 检查通过
  exit 0
else
  # 检查失败，输出警告但不阻止（PostToolUse 不支持阻止）
  # 这里只记录日志，不阻止操作
  exit 0
fi
