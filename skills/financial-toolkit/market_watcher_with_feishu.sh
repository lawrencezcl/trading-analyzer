#!/bin/bash
# 15分钟市场观察任务 - 带飞书通知
# Market Watcher with Feishu Notification

SKILL_DIR="/root/.openclaw/workspace/skills/financial-toolkit"
REPORT_DIR="/root/.openclaw/workspace/market-reports"
FEISHU_USER="ou_07d4bba36107207055c340e833604d0b"

# 运行分析脚本
OUTPUT=$(cd "$SKILL_DIR" && python3 market_watcher.py 2>&1)

# 提取飞书消息
FEISHU_MSG=$(echo "$OUTPUT" | sed -n '/=== FEISHU_MSG_START ===/,/=== FEISHU_MSG_END ===/p' | sed 's/=== FEISHU_MSG_START ===//;s/=== FEISHU_MSG_END ===//')

# 发送飞书消息
if [ -n "$FEISHU_MSG" ]; then
    # 使用 openclaw message 命令发送
    echo "$FEISHU_MSG" | openclaw message send --channel feishu --to "$FEISHU_USER" --stdin 2>/dev/null || true
fi

echo "市场观察报告已生成并发送"
