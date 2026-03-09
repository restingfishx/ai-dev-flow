#!/usr/bin/env bash
set -euo pipefail

# 配置 - 只同步 project 目录
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)/project"
TARGET_DIR="${1:-.}"

# 排除文件
EXCLUDE_DIRS=(
    ".git"
    "node_modules"
    "__pycache__"
    ".venv"
)

# 构建 rsync 排除参数
EXCLUDE_ARGS=()
for dir in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_ARGS+=("--exclude=$dir")
done

echo "=== 文件同步脚本 ==="
echo "源目录: $SOURCE_DIR"
echo "目标目录: $TARGET_DIR"
echo ""

# 检查源目录存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo "错误: 源目录不存在: $SOURCE_DIR"
    exit 1
fi

# 检查目标目录存在
if [ ! -d "$TARGET_DIR" ]; then
    read -p "目标目录不存在，是否创建? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    mkdir -p "$TARGET_DIR"
fi

# 同步文件
echo "正在同步文件..."
rsync -av \
    "${EXCLUDE_ARGS[@]}" \
    --delete \
    "$SOURCE_DIR/" "$TARGET_DIR/"

echo ""
echo "同步完成!"
