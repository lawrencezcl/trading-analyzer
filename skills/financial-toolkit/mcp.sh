#!/bin/bash
# MCP 金融数据快捷命令
# MCP Financial Data Quick Commands

SKILL_DIR="/root/.openclaw/workspace/skills/financial-toolkit"

case "$1" in
    quote|价格)
        python3 "$SKILL_DIR/mcp_skills.py" quote "$2"
        ;;
    profile|概况)
        python3 "$SKILL_DIR/mcp_skills.py" profile "$2"
        ;;
    financials|财务)
        python3 "$SKILL_DIR/mcp_skills.py" financials "$2"
        ;;
    technicals|技术)
        python3 "$SKILL_DIR/mcp_skills.py" technicals "$2"
        ;;
    search|搜索)
        shift
        python3 "$SKILL_DIR/mcp_skills.py" search "$@"
        ;;
    analyze|分析)
        python3 "$SKILL_DIR/mcp_skills.py" analyze "$2"
        ;;
    *)
        echo "MCP 金融数据工具"
        echo ""
        echo "用法:"
        echo "  $0 quote <股票代码>       - 实时报价"
        echo "  $0 profile <股票代码>      - 公司概况"
        echo "  $0 financials <股票代码>   - 财务分析"
        echo "  $0 technicals <股票代码>   - 技术分析"
        echo "  $0 search <查询内容>      - AI 搜索"
        echo "  $0 analyze <股票代码>      - 综合分析"
        echo ""
        echo "示例:"
        echo "  $0 quote AAPL"
        echo "  $0 analyze TSLA"
        echo "  $0 search \"Apple stock outlook 2024\""
        ;;
esac
