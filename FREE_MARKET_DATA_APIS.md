# 免费市场数据 API / MCP / Skills 汇总
# Free Market Data Services

## 一、已配置的 API (当前使用)

### 1. Finnhub
- **网址:** https://finnhub.io
- **免费额度:** 60 calls/minute
- **覆盖品种:**
  - ✅ 标普500 (SPY)
  - ✅ 纳斯达克100 (QQQ)
  - ✅ 个股、ETF
  - ❌ 黄金、白银 (有限)
- **特点:** 实时报价、新闻、基本面数据

### 2. Twelve Data
- **网址:** https://twelvedata.com
- **免费额度:** 800 calls/day
- **覆盖品种:**
  - ✅ 股票 (全球)
  - ✅ 外汇
  - ✅ 加密货币
  - ⚠️ 指数 (部分)
- **特点:** 技术指标、历史数据

### 3. Alpha Vantage
- **网址:** https://www.alphavantage.co
- **免费额度:** 25 calls/day
- **覆盖品种:**
  - ✅ 股票 (美股)
  - ✅ 外汇
  - ✅ 加密货币
- **特点:** 财务报表、技术指标

---

## 二、推荐的免费 API

### 股票指数类

#### 4. Yahoo Finance (非官方)
- **Python库:** `yfinance`
- **免费:** 完全免费
- **覆盖:**
  - ✅ 标普500 (^GSPC)
  - ✅ 纳斯达克100 (^NDX)
  - ✅ 德国DAX (^GDAXI)
  - ✅ 日经225 (^N225)
  - ✅ 全球主要指数
- **特点:** 数据全面，延迟15-20分钟
- **安装:** `pip install yfinance`

#### 5. Indices-API
- **网址:** https://indices-api.com
- **开源:** 是
- **覆盖:**
  - ✅ S&P 500
  - ✅ NASDAQ
  - ✅ Dow Jones
  - ✅ 全球主要指数
- **特点:** 轻量级，专门做指数

### 贵金属类

#### 6. GoldAPI.io
- **网址:** https://www.goldapi.io
- **免费额度:** 100 calls/day
- **覆盖:**
  - ✅ 黄金 (XAU)
  - ✅ 白银 (XAG)
  - ✅ 铂金 (XPT)
  - ✅ 钯金 (XPD)
- **特点:** 100%实时， FOREX数据

#### 7. Metals-API
- **网址:** https://metals-api.com
- **免费额度:** 100 calls/month
- **覆盖:**
  - ✅ 黄金
  - ✅ 白银
  - ✅ 其他贵金属
- **特点:** 历史数据+实时

#### 8. MetalPriceAPI
- **网址:** https://metalpriceapi.com
- **免费额度:** 100 calls/day
- **覆盖:**
  - ✅ XAU, XAG, XPT, XPD
- **特点:** 多货币报价

### 综合类

#### 9. Marketstack
- **网址:** https://marketstack.com
- **免费额度:** 1000 calls/month
- **覆盖:**
  - ✅ 全球股票
  - ✅ 指数
  - ✅ ETF
- **特点:** 实时+历史数据

#### 10. FCS API
- **网址:** https://fcsapi.com
- **免费额度:** 有免费层
- **覆盖:**
  - ✅ 股票 (125000+)
  - ✅ 外汇
  - ✅ 加密货币
  - ✅ 商品

---

## 三、ClawHub Skills

### 已发现的 Skills

| Skill | 功能 | 适用性 |
|-------|------|--------|
| openclaw-aisa-finance-stock-equity-crypto-market-price-data | 股票+加密货币实时价格 | ⭐⭐⭐ |
| openclaw-aisa-market-pulse | 市场脉搏 (股票+加密货币) | ⭐⭐⭐ |
| stock-analysis | 股票分析 | ⭐⭐ |
| stock-watcher | 股票监控 | ⭐⭐ |
| tushare-finance | A股数据 (需Tushare账号) | ⭐ (A股) |
| finnhub-pro | Finnhub专业版 | ⭐⭐⭐ |
| market-analysis-cn | 中国市场分析 | ⭐ (A股) |

---

## 四、推荐配置方案

### 方案1: 完全免费 (推荐)
| 品种 | API | 备注 |
|------|-----|------|
| SPX, NQ, DAX, JP225 | Yahoo Finance (yfinance) | 免费，数据全 |
| XAU, XAG | GoldAPI.io | 100次/天 |
| 技术指标 | Twelve Data | 800次/天 |
| 基本面 | Finnhub | 60次/分钟 |

### 方案2: 稳定优先
| 品种 | API | 费用 |
|------|-----|------|
| 所有品种 | Twelve Data | 免费层 |
| 贵金属 | Metals-API | 免费层 |
| 备用 | Alpha Vantage | 免费层 |

---

## 五、需要申请的 API Key

1. **GoldAPI.io** - 用于黄金白银
   - 网址: https://www.goldapi.io
   - 注册即可获取

2. **Twelve Data** - 用于技术指标
   - 网址: https://twelvedata.com
   - 注册即可获取

3. **Metals-API** - 贵金属备选
   - 网址: https://metals-api.com
   - 注册即可获取

---

## 六、当前系统状态

| API | 状态 | 用途 |
|-----|------|------|
| Finnhub | ✅ 已配置 | 股票实时报价 |
| Twelve Data | ✅ 已配置 | 技术指标 |
| Alpha Vantage | ✅ 已配置 | 基本面数据 |
| Yahoo Finance | ⚠️ 可用 | 指数数据 (待集成) |
| GoldAPI.io | ❌ 未配置 | 黄金白银行情 |

---

## 七、下一步建议

1. **立即申请:** GoldAPI.io (黄金白银)
2. **备用方案:** 集成 yfinance (Yahoo Finance)
3. **ClawHub:** 尝试安装 openclaw-aisa-market-pulse

需要我帮你申请 GoldAPI.io 或集成 yfinance 吗？
