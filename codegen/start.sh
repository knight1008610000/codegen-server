#!/bin/bash
# 代码补全服务器快速启动脚本

set -e

echo "=== 代码补全服务器启动脚本 ==="

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "错误: DEEPSEEK_API_KEY 环境变量未设置"
    echo "请设置环境变量: export DEEPSEEK_API_KEY='your-api-key'"
    exit 1
fi

echo "✓ DeepSeek API密钥已设置"

# 检查依赖
echo "检查Python依赖..."
if ! command -v python &> /dev/null; then
    echo "错误: Python未安装"
    exit 1
fi

# 使用pixi或直接python
if command -v pixi &> /dev/null; then
    echo "使用pixi运行..."
    CMD="pixi run python"
else
    echo "使用系统Python运行..."
    CMD="python"
fi

# 检查Django项目
echo "检查Django项目配置..."
$CMD manage.py check

# 应用数据库迁移
echo "应用数据库迁移..."
$CMD manage.py migrate

# 启动服务器
echo "启动开发服务器..."
echo "服务器地址: http://localhost:8000"
echo "API端点: http://localhost:8000/api/v1/completion"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

$CMD manage.py runserver 0.0.0.0:8000