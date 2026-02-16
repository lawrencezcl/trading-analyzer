# 蔡森技术分析交易信号服务

基于蔡森经典技术分析理论的 24/7 自动化交易信号分析服务。

## 功能特点

- **24/7 全天候运行**: 自动每30分钟分析一次市场
- **蔡森12形态识别**: W底、M头、头肩底/顶、三角形、圆弧等
- **多品种监控**: 黄金、白银、BTC、ETH、XRP、美股ETF等
- **多时间框架**: 支持1分钟到4小时多周期分析
- **Telegram推送**: 发现交易信号自动推送通知
- **HTML可视化报告**: 生成美观的Web界面报告

## 蔡森技术分析理论

本系统基于蔡森老师的12种经典技术形态：

| 形态 | 信号类型 | 描述 |
|------|----------|------|
| W底 (双底) | 买入 | 两次探底后反弹 |
| M头 (双顶) | 卖出 | 两次冲高后回落 |
| 头肩底 | 买入 | 三次探底，中间最低 |
| 头肩顶 | 卖出 | 三次冲高，中间最高 |
| 上升三角形 | 买入 | 高点持平，低点上移 |
| 下降三角形 | 卖出 | 低点持平，高点下移 |
| 圆弧底 | 买入 | U型底部形态 |
| 圆弧顶 | 卖出 | 倒U型顶部形态 |
| 三重底 | 买入 | 三次相同低点 |
| 三重顶 | 卖出 | 三次相同高点 |
| 旗形/楔形 | 中性 | 短期整理形态 |
| 矩形整理 | 观望 | 横盘震荡区间 |

## 快速开始

### 方式一: Docker 运行 (推荐)

```bash
# 克隆仓库
git clone https://github.com/lawrencezcl/trading-analyzer.git
cd trading-analyzer

# 使用 docker-compose 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式二: 直接运行

```bash
# 克隆仓库
git clone https://github.com/lawrencezcl/trading-analyzer.git
cd trading-analyzer

# 安装依赖
pip install -r requirements.txt

# 启动服务
./start_service.sh start

# 查看状态
./start_service.sh status

# 停止服务
./start_service.sh stop
```

## 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `TWELVE_DATA_API_KEY` | Twelve Data API密钥 | 内置 |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API密钥 | 内置 |
| `TELEGRAM_BOT_TOKEN` | Telegram机器人Token | 需配置 |
| `TELEGRAM_CHAT_ID` | Telegram频道/群组ID | 需配置 |
| `PROXY_URL` | 代理地址 (如需要) | 无 |
| `ANALYSIS_INTERVAL_MINUTES` | 分析间隔(分钟) | 30 |
| `CONFIDENCE_THRESHOLD` | 信号置信度阈值 | 60 |

### 创建 .env 文件

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置
vim .env
```

## 监控品种

| 代码 | 名称 | 类型 |
|------|------|------|
| XAU/USD | 黄金 | 外汇 |
| XAG/USD | 白银 | 外汇 |
| BTC/USD | 比特币 | 加密货币 |
| ETH/USD | 以太坊 | 加密货币 |
| XRP/USD | 瑞波币 | 加密货币 |
| SPY | 标普500ETF | 股票 |
| QQQ | 纳斯达克100ETF | 股票 |
| IWM | 罗素2000ETF | 股票 |

## 查看报告

服务运行后，可通过以下方式查看交易信号：

1. **HTML报告**: 打开 `signals/report.html` 文件
2. **JSON数据**: 查看 `signals/signals_YYYY-MM-DD.json`
3. **Telegram推送**: 配置后自动推送到Telegram

## 服务管理

```bash
# 启动服务
./start_service.sh start

# 停止服务
./start_service.sh stop

# 重启服务
./start_service.sh restart

# 查看状态
./start_service.sh status

# 查看日志
./start_service.sh logs
```

## 目录结构

```
trading-analyzer/
├── trading_analyzer_service.py  # 主服务代码
├── start_service.sh             # 启动脚本
├── Dockerfile                   # Docker配置
├── docker-compose.yml           # Docker Compose配置
├── requirements.txt             # Python依赖
├── README.md                    # 说明文档
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git忽略文件
├── .dockerignore                # Docker忽略文件
└── signals/                     # 信号数据目录
    ├── report.html              # HTML可视化报告
    └── signals_*.json           # JSON格式信号数据
```

## 技术指标

系统使用以下技术指标进行分析：

- **RSI (相对强弱指数)**: 超买超卖判断
- **MACD**: 趋势方向和动能
- **MA (移动平均线)**: MA5, MA10, MA20, MA50, MA200
- **趋势分析**: 多头/空头判断
- **形态识别**: 蔡森12种经典形态

## API 数据源

- [Twelve Data](https://twelvedata.com/) - 外汇和加密货币数据
- [Alpha Vantage](https://www.alphavantage.co/) - 股票ETF数据

## 注意事项

⚠️ **风险提示**: 本系统仅供学习和研究使用，不构成任何投资建议。投资有风险，入市需谨慎。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ by Trading Analyzer Team**
