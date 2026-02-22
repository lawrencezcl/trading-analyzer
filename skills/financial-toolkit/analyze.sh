#!/bin/bash
# 股票分析快捷命令
# Stock Analysis Quick Commands

SKILL_DIR="/root/.openclaw/workspace/skills/financial-toolkit"

# 分析股票
analyze_stock() {
    local symbol=$1
    local market=${2:-us}
    echo "正在分析股票: $symbol ($market)..."
    python3 "$SKILL_DIR/stock_analyzer.py" stock "$symbol"
}

# 分析行业
analyze_industry() {
    local industry=$1
    echo "正在分析行业: $industry..."
    python3 "$SKILL_DIR/stock_analyzer.py" industry "$industry"
}

# 提取风险
extract_risks() {
    local data=$1
    echo "正在提取风险点..."
    python3 "$SKILL_DIR/stock_analyzer.py" risk "$data"
}

# 解读数据
interpret_data() {
    local data_type=$1
    local data=$2
    echo "正在解读数据..."
    python3 "$SKILL_DIR/stock_analyzer.py" interpret "$data_type" "$data"
}

# 主命令
case "$1" in
    stock)
        analyze_stock "$2" "$3"
        ;;
    industry)
        analyze_industry "$2"
        ;;
    risk)
        extract_risks "$2"
        ;;
    interpret)
        interpret_data "$2" "$3"
        ;;
    *)
        echo "用法:"
        echo "  $0 stock <代码> [市场]     - 分析股票"
        echo "  $0 industry <行业名>       - 分析行业"
        echo "  $0 risk '<JSON数据>'       - 提取风险"
        echo "  $0 interpret <类型> '<数据>' - 解读数据"
        ;;
esac
