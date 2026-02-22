# MCP 金融数据技能
# MCP Financial Data Skills

## 功能
提供标准化的金融数据接口，支持 MCP (Model Context Protocol)

## 数据源
- Finnhub - 实时报价、公司信息、新闻
- Twelve Data - 历史数据、技术指标
- Alpha Vantage - 财务报表、基本面数据
- Tavily - AI 增强搜索

## API 方法

### 1. 实时报价
```python
mcp_stock_quote(symbol)
```
返回：当前价格、涨跌、高低开收等

### 2. 公司概况
```python
mcp_stock_profile(symbol)
```
返回：公司名称、行业、市值、员工数等

### 3. 财务分析
```python
mcp_financial_analysis(symbol)
```
返回：估值指标、盈利能力、成长性、财务健康度

### 4. 技术分析
```python
mcp_technical_analysis(symbol)
```
返回：RSI、SMA、价格历史

### 5. AI 搜索
```python
mcp_search(query)
```
返回：相关新闻、分析报告

### 6. 综合分析
```python
mcp_comprehensive_analysis(symbol)
```
返回：整合所有维度的完整分析

## 命令行使用
```bash
# 实时报价
python mcp_skills.py quote AAPL

# 公司概况
python mcp_skills.py profile TSLA

# 财务分析
python mcp_skills.py financials MSFT

# 技术分析
python mcp_skills.py technicals NVDA

# AI 搜索
python mcp_skills.py search "Apple stock outlook 2024"

# 综合分析
python mcp_skills.py analyze AMZN
```
