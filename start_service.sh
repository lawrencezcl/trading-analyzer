#!/bin/bash

# 蔡森技术分析服务启动脚本

echo "=========================================="
echo "   蔡森技术分析服务 - 启动脚本"
echo "=========================================="

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

echo "✅ Python3 已安装"

# 检查依赖
echo "📦 检查依赖..."
pip3 install aiohttp --quiet 2>/dev/null

# 创建日志目录
LOG_DIR="/home/admin/Desktop/Rich/logs"
mkdir -p $LOG_DIR

# 方式1: 直接运行 (前台)
run_foreground() {
    echo "🚀 以前台模式启动服务..."
    echo "📍 日志文件: trading_analyzer.log"
    echo "⏹️  按 Ctrl+C 停止"
    echo "=========================================="
    cd /home/admin/Desktop/Rich
    python3 trading_analyzer_service.py
}

# 方式2: 后台运行 (nohup)
run_background() {
    echo "🚀 以后台模式启动服务..."
    cd /home/admin/Desktop/Rich

    # 检查是否已在运行
    if pgrep -f "trading_analyzer_service.py" > /dev/null; then
        echo "⚠️  服务已在运行中"
        echo "📍 使用 ./start_service.sh stop 来停止"
        exit 1
    fi

    nohup python3 trading_analyzer_service.py >> trading_analyzer.log 2>&1 &
    PID=$!
    echo $PID > trading_analyzer.pid

    sleep 2

    if ps -p $PID > /dev/null; then
        echo "✅ 服务已启动 (PID: $PID)"
        echo "📍 日志文件: trading_analyzer.log"
        echo "📍 PID文件: trading_analyzer.pid"
        echo "⏹️  停止命令: ./start_service.sh stop"
    else
        echo "❌ 服务启动失败，请检查日志"
        tail -20 trading_analyzer.log
    fi
}

# 停止服务
stop_service() {
    echo "⏹️  停止服务..."

    if [ -f trading_analyzer.pid ]; then
        PID=$(cat trading_analyzer.pid)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            echo "✅ 服务已停止 (PID: $PID)"
        else
            echo "⚠️  服务进程不存在"
        fi
        rm trading_analyzer.pid
    else
        # 尝试通过进程名停止
        pkill -f "trading_analyzer_service.py"
        echo "✅ 服务已停止"
    fi
}

# 查看状态
check_status() {
    echo "📊 服务状态:"
    if pgrep -f "trading_analyzer_service.py" > /dev/null; then
        PID=$(pgrep -f "trading_analyzer_service.py")
        echo "✅ 运行中 (PID: $PID)"
        echo ""
        echo "📋 最近日志:"
        tail -10 trading_analyzer.log 2>/dev/null || echo "无日志"
    else
        echo "⏹️  服务未运行"
    fi
}

# 查看日志
view_logs() {
    echo "📋 服务日志 (最后50行):"
    echo "=========================================="
    tail -50 trading_analyzer.log 2>/dev/null || echo "无日志"
}

# 主菜单
case "$1" in
    start)
        run_background
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 2
        run_background
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    fg)
        run_foreground
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs|fg}"
        echo ""
        echo "命令说明:"
        echo "  start   - 后台启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看服务日志"
        echo "  fg      - 前台运行 (调试用)"
        ;;
esac
