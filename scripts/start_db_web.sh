#!/bin/bash
# 启动 sqlite-web 管理界面
# 用法: ./scripts/start_db_web.sh [端口号]
# 默认端口: 9898

PORT=${1:-9898}
DB_FILE="channel/web/web_chat.db"

# 检查是否安装了 sqlite-web
if ! command -v sqlite_web &> /dev/null; then
    echo "未找到 sqlite-web，正在安装..."
    pip install sqlite-web
fi

if [ ! -f "$DB_FILE" ]; then
    echo "错误: 找不到数据库文件 $DB_FILE"
    echo "请确保你在项目根目录下运行此脚本"
    exit 1
fi

echo "=================================================="
echo "正在启动数据库Web管理界面..."
echo "数据库: $DB_FILE"
echo "地址: http://0.0.0.0:$PORT"
echo "请确保云服务器防火墙已放行 $PORT 端口"
echo "=================================================="

sqlite_web "$DB_FILE" --port "$PORT" --host 0.0.0.0 --no-browser
