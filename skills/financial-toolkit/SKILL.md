# 财经分析工具集
# Financial Analysis Toolkit

## 安装依赖
```bash
pip install yfinance pandas numpy matplotlib
```

## 核心功能

### 1. 股票数据获取
```python
import yfinance as yf

def get_stock_data(symbol, period="1y"):
    stock = yf.Ticker(symbol)
    return stock.history(period=period)
```

### 2. 基本面分析
- PE/PB/PS 估值
- ROE/ROA 盈利能力
- 负债率分析
- 现金流分析

### 3. 技术面分析
- 移动平均线
- RSI/MACD
- 布林带
- 成交量分析

### 4. 行业对比
- 同行业公司对比
- 行业平均值
- 行业排名
