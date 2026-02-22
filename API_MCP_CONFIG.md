# 实时数据 API / MCP 技能配置完成
# 配置时间: 2026-02-22

## 已配置 API

### 1. Finnhub
- API Key: d6476nhr01ql6dj2ekegd6476nhr01ql6dj2ekf0
- 功能: 实时报价、公司信息、新闻、同行业对比
- 限制: 60 calls/minute (免费版)

### 2. Twelve Data
- API Key: f5491ce160e64101a960e19eb8363f38
- 功能: 历史数据、技术指标、盈利数据
- 支持: 股票、外汇、加密货币

### 3. Alpha Vantage
- API Key: IUO07N60XUPUHNTL
- 功能: 财务报表、基本面数据、技术指标
- 限制: 25 calls/day (免费版)

### 4. Tavily
- API Key: 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
- 功能: AI 增强搜索、新闻聚合
- 用途: 获取最新市场资讯和分析

## Telegram Bot (备用)
- 用户名: @qiblafestbot
- Token: 8074023086:AAFARIEvDP4q0s9VB2uyp9xPOhlFsI8KCpg
- 状态: 已配置，需重启 Gateway

## MCP 技能功能

### 实时数据
- ✅ 股票实时报价
- ✅ 公司概况信息
- ✅ 市场新闻

### 财务分析
- ✅ 估值指标 (PE/PB/PS/PEG)
- ✅ 盈利能力 (ROE/ROA/毛利率)
- ✅ 成长性分析
- ✅ 财务健康度

### 技术分析
- ✅ 价格历史
- ✅ RSI 指标
- ✅ 移动平均线

### AI 搜索
- ✅ 市场资讯搜索
- ✅ 分析报告聚合

## 使用方法

### Python API
```python
from skills.financial_toolkit.mcp_skills import *

# 获取实时报价
quote = mcp_stock_quote("AAPL")

# 综合分析
analysis = mcp_comprehensive_analysis("TSLA")

# AI 搜索
results = mcp_search("Apple stock outlook 2024")
```

### 命令行
```bash
# 实时报价
./skills/financial-toolkit/mcp.sh quote AAPL

# 综合分析
./skills/financial-toolkit/mcp.sh analyze TSLA

# AI 搜索
./skills/financial-toolkit/mcp.sh search "AI industry trends"
```

### 直接问我
- "查一下 AAPL 的实时价格"
- "分析一下特斯拉的财务状况"
- "搜索一下苹果公司的最新新闻"
