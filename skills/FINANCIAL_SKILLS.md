# 金融分析技能套装
# Financial Analysis Skills Bundle

## 已安装技能

### 1. stock-analysis - 股票分析
- 基本面分析
- 技术面分析
- 估值分析
- 财务健康度评估

### 2. industry-analysis - 行业分析
- 行业趋势分析
- 竞争格局梳理
- 产业链分析
- 政策影响评估

### 3. risk-analysis - 风险分析
- 投资风险识别
- 风险量化评估
- 风险点提取
- 风险预警

### 4. data-interpretation - 数据解读
- 财务数据解读
- 市场数据解读
- 宏观经济数据解读
- 行业数据解读

### 5. financial-toolkit - 财经工具集
- 股票数据获取
- 基本面/技术面分析
- 行业对比
- 自动化分析脚本

## 使用方法

### 命令行工具
```bash
# 分析股票
./skills/financial-toolkit/analyze.sh stock AAPL
./skills/financial-toolkit/analyze.sh stock 000001 cn

# 分析行业
./skills/financial-toolkit/analyze.sh industry "新能源汽车"

# 提取风险
./skills/financial-toolkit/analyze.sh risk '{"pe": 50, "debt_ratio": 0.8}'
```

### Python API
```python
from skills.financial_toolkit.stock_analyzer import analyze_stock, analyze_industry

# 分析股票
result = analyze_stock("AAPL", "us")

# 分析行业
result = analyze_industry("人工智能")
```

## 分析框架

### 股票分析维度
1. **基本面**
   - 盈利能力 (ROE, ROA, 毛利率)
   - 成长性 (营收增长, 利润增长)
   - 财务健康 (负债率, 现金流)
   - 估值水平 (PE, PB, PS)

2. **技术面**
   - 趋势分析
   - 支撑/阻力位
   - 技术指标 (RSI, MACD, 布林带)
   - 成交量分析

3. **风险点**
   - 经营风险
   - 财务风险
   - 行业风险
   - 市场风险

### 行业分析维度
1. 行业概况与定义
2. 市场规模与增长趋势
3. 竞争格局与主要玩家
4. 产业链结构
5. 关键驱动因素
6. 政策环境
7. 风险与挑战
8. 投资机会

## 数据源集成

### 免费数据源
- Yahoo Finance (美股)
- AKShare (A股)
- Tushare (A股, 需API Key)
- Alpha Vantage (全球)

### 付费数据源
- Wind
- Bloomberg
- Refinitiv

## 安装时间
2026-02-22
