#!/usr/bin/env python3
"""
蔡森技术分析交易信号服务
24/7运行，每30分钟分析一次，发送交易信号到Telegram
支持代理和本地存储
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import os
import ssl

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 配置区域 ====================

# API密钥
TWELVE_DATA_API_KEY = "f5491ce160e64101a960e19eb8363f38"
ALPHA_VANTAGE_API_KEY = "IUO07N60XUPUHNTL"

# Telegram配置
TELEGRAM_BOT_TOKEN = "8450500469:AAHQ_uqLZ0Qf1U9Ff5V-_5OHu7Arn8_2o6Y"
TELEGRAM_CHAT_ID = "@jht1983_bot"

# 代理设置 (如需要，设置为 "http://127.0.0.1:7890" 等)
PROXY_URL = None  # 设置为 None 表示不使用代理

# 分析间隔 (分钟)
ANALYSIS_INTERVAL_MINUTES = 30

# 信号置信度阈值 (低于此值不发送通知)
CONFIDENCE_THRESHOLD = 60

# 分析品种配置
SYMBOLS = {
    # 贵金属
    "XAU/USD": {"name": "黄金", "type": "forex", "api": "twelvedata"},
    "XAG/USD": {"name": "白银", "type": "forex", "api": "twelvedata"},
    # 加密货币
    "BTC/USD": {"name": "比特币", "type": "crypto", "api": "twelvedata"},
    "ETH/USD": {"name": "以太坊", "type": "crypto", "api": "twelvedata"},
    "XRP/USD": {"name": "瑞波币", "type": "crypto", "api": "twelvedata"},
    # 股指ETF
    "SPY": {"name": "标普500ETF", "type": "stock", "api": "alphavantage"},
    "QQQ": {"name": "纳斯达克100ETF", "type": "stock", "api": "alphavantage"},
    "IWM": {"name": "罗素2000ETF", "type": "stock", "api": "alphavantage"},
}

# ==================== 数据类 ====================

@dataclass
class TradingSignal:
    """交易信号数据类"""
    symbol: str
    name: str
    current_price: float
    signal: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    pattern: str  # 蔡森形态
    entry_zone: str
    target: str
    stop_loss: str
    timeframe: str
    indicators: Dict
    timestamp: str

    def to_dict(self):
        return asdict(self)

# ==================== 技术分析器 ====================

class TechnicalAnalyzer:
    """蔡森技术分析器"""

    def __init__(self, proxy_url: str = None):
        self.session = None
        self.proxy_url = proxy_url

    async def init_session(self):
        if self.session is None:
            connector = None
            if self.proxy_url:
                connector = aiohttp.TCPConnector(ssl=False)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_price_twelvedata(self, symbol: str) -> Optional[float]:
        """从Twelve Data获取价格"""
        await self.init_session()
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "price" in data:
                        return float(data["price"])
                else:
                    logger.warning(f"Twelve Data API返回 {response.status} for {symbol}")
        except asyncio.TimeoutError:
            logger.warning(f"Twelve Data API超时 for {symbol}")
        except Exception as e:
            logger.error(f"Twelve Data API error for {symbol}: {e}")
        return None

    async def get_price_alphavantage(self, symbol: str) -> Optional[Dict]:
        """从Alpha Vantage获取价格"""
        await self.init_session()
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Global Quote" in data:
                        quote = data["Global Quote"]
                        return {
                            "price": float(quote.get("05. price", 0)),
                            "open": float(quote.get("02. open", 0)),
                            "high": float(quote.get("03. high", 0)),
                            "low": float(quote.get("04. low", 0)),
                            "volume": int(quote.get("06. volume", 0)),
                            "change_pct": quote.get("10. change percent", "0%")
                        }
        except asyncio.TimeoutError:
            logger.warning(f"Alpha Vantage API超时 for {symbol}")
        except Exception as e:
            logger.error(f"Alpha Vantage API error for {symbol}: {e}")
        return None

    async def get_klines_twelvedata(self, symbol: str, interval: str = "1h", outputsize: int = 48) -> Optional[List]:
        """从Twelve Data获取K线数据"""
        await self.init_session()
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={TWELVE_DATA_API_KEY}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "values" in data:
                        return data["values"]
        except Exception as e:
            logger.error(f"Twelve Data Klines error for {symbol}: {e}")
        return None

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50.0

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        if len(gains) < period:
            return 50.0

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)

    def calculate_macd(self, prices: List[float]) -> Dict:
        """计算MACD"""
        if len(prices) < 26:
            return {"macd": 0, "signal": 0, "histogram": 0}

        def ema(data, period):
            multiplier = 2 / (period + 1)
            ema_val = sum(data[:period]) / period
            for price in data[period:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return ema_val

        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd_line = ema12 - ema26
        signal_line = macd_line * 0.8
        histogram = macd_line - signal_line

        return {
            "macd": round(macd_line, 4),
            "signal": round(signal_line, 4),
            "histogram": round(histogram, 4)
        }

    def calculate_ma(self, prices: List[float], period: int) -> float:
        """计算移动平均线"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return round(sum(prices[-period:]) / period, 2)

    def identify_pattern(self, prices: List[float], rsi: float, macd: Dict) -> Dict:
        """蔡森12形态识别"""
        if len(prices) < 20:
            return {"pattern": "数据不足", "signal": "HOLD", "confidence": 0}

        current_price = prices[-1]
        ma5 = self.calculate_ma(prices, 5)
        ma10 = self.calculate_ma(prices, 10)
        ma20 = self.calculate_ma(prices, 20)

        high_20 = max(prices[-20:])
        low_20 = min(prices[-20:])

        trend = "UP" if current_price > ma20 else "DOWN"
        rsi_signal = "OVERSOLD" if rsi < 30 else ("OVERBOUGHT" if rsi > 70 else "NEUTRAL")
        macd_signal = "BULLISH" if macd["histogram"] > 0 else "BEARISH"

        pattern = ""
        signal = "HOLD"
        confidence = 50

        # 蔡森形态识别逻辑
        # 1. W底 (双底)
        if len(prices) >= 20:
            recent_low = min(prices[-20:-10])
            older_low = min(prices[-30:-20]) if len(prices) >= 30 else recent_low
            if abs(recent_low - older_low) / older_low < 0.02 and rsi < 40:
                pattern = "W底(双底)"
                signal = "BUY"
                confidence = 70

        # 2. M头 (双顶)
        if len(prices) >= 20 and pattern == "":
            recent_high = max(prices[-20:-10])
            older_high = max(prices[-30:-20]) if len(prices) >= 30 else recent_high
            if abs(recent_high - older_high) / older_high < 0.02 and rsi > 60:
                pattern = "M头(双顶)"
                signal = "SELL"
                confidence = 70

        # 3. 上升三角形
        if current_price > ma5 > ma10 > ma20 and macd_signal == "BULLISH" and pattern == "":
            pattern = "上升三角形"
            signal = "BUY"
            confidence = 65

        # 4. 下降三角形
        if current_price < ma5 < ma10 < ma20 and macd_signal == "BEARISH" and pattern == "":
            pattern = "下降三角形"
            signal = "SELL"
            confidence = 65

        # 5. RSI超卖反弹
        if rsi < 30 and pattern == "":
            pattern = "RSI超卖反弹"
            signal = "BUY"
            confidence = 60

        # 6. RSI超买回落
        if rsi > 70 and pattern == "":
            pattern = "RSI超买回落"
            signal = "SELL"
            confidence = 60

        # 7. 头肩底 (简化判断)
        if len(prices) >= 30 and pattern == "":
            mid_price = prices[-15]
            if mid_price < prices[-20] and mid_price < prices[-10] and rsi < 45:
                pattern = "头肩底"
                signal = "BUY"
                confidence = 68

        # 8. 头肩顶 (简化判断)
        if len(prices) >= 30 and pattern == "":
            mid_price = prices[-15]
            if mid_price > prices[-20] and mid_price > prices[-10] and rsi > 55:
                pattern = "头肩顶"
                signal = "SELL"
                confidence = 68

        # 默认矩形整理
        if pattern == "":
            pattern = "矩形整理"
            signal = "HOLD"
            confidence = 40

        return {
            "pattern": pattern,
            "signal": signal,
            "confidence": confidence,
            "trend": trend,
            "rsi_signal": rsi_signal,
            "macd_signal": macd_signal,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20
        }

    async def analyze_symbol(self, symbol: str, config: Dict) -> Optional[TradingSignal]:
        """分析单个品种"""
        try:
            # 获取价格
            if config["api"] == "twelvedata":
                price = await self.get_price_twelvedata(symbol)
                klines = await self.get_klines_twelvedata(symbol)
                price_data = {"price": price, "change_pct": "N/A"}
            else:
                price_data = await self.get_price_alphavantage(symbol)
                price = price_data["price"] if price_data else None
                klines = None

            if not price:
                logger.warning(f"无法获取 {symbol} 价格")
                return None

            # 获取K线价格列表
            if klines:
                prices = [float(k["close"]) for k in reversed(klines)]
            else:
                prices = [price] * 50

            # 计算指标
            rsi = self.calculate_rsi(prices)
            macd = self.calculate_macd(prices)

            # 形态识别
            pattern_result = self.identify_pattern(prices, rsi, macd)

            # 计算支撑阻力
            high_20 = max(prices[-20:]) if len(prices) >= 20 else price
            low_20 = min(prices[-20:]) if len(prices) >= 20 else price

            # 计算入场区间和目标
            if pattern_result["signal"] == "BUY":
                entry_zone = f"{low_20:.2f} - {price:.2f}"
                target = f"{price * 1.02:.2f} / {price * 1.05:.2f}"
                stop_loss = f"{low_20 * 0.98:.2f}"
            elif pattern_result["signal"] == "SELL":
                entry_zone = f"{price:.2f} - {high_20:.2f}"
                target = f"{price * 0.98:.2f} / {price * 0.95:.2f}"
                stop_loss = f"{high_20 * 1.02:.2f}"
            else:
                entry_zone = f"{low_20:.2f} - {high_20:.2f}"
                target = "观望"
                stop_loss = "N/A"

            return TradingSignal(
                symbol=symbol,
                name=config["name"],
                current_price=price,
                signal=pattern_result["signal"],
                confidence=pattern_result["confidence"],
                pattern=pattern_result["pattern"],
                entry_zone=entry_zone,
                target=target,
                stop_loss=stop_loss,
                timeframe="1H",
                indicators={
                    "rsi": rsi,
                    "macd": macd,
                    "ma5": pattern_result["ma5"],
                    "ma10": pattern_result["ma10"],
                    "ma20": pattern_result["ma20"],
                    "trend": pattern_result["trend"]
                },
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

        except Exception as e:
            logger.error(f"分析 {symbol} 时出错: {e}")
            return None

# ==================== Telegram通知器 ====================

class TelegramNotifier:
    """Telegram通知器"""

    def __init__(self, bot_token: str, chat_id: str, proxy_url: str = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.proxy_url = proxy_url
        self.session = None

    async def init_session(self):
        if self.session is None:
            connector = None
            if self.proxy_url:
                connector = aiohttp.TCPConnector(ssl=False)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def send_message(self, message: str) -> bool:
        """发送消息到Telegram"""
        await self.init_session()
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info("✅ Telegram消息发送成功")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"❌ Telegram发送失败 [{response.status}]: {error}")
                    return False
        except asyncio.TimeoutError:
            logger.error("❌ Telegram发送超时 - 请检查网络或设置代理")
            return False
        except Exception as e:
            logger.error(f"❌ Telegram发送错误: {e}")
            return False

    def format_signal_message(self, signals: List[TradingSignal], threshold: int = 60) -> Optional[str]:
        """格式化交易信号消息"""
        # 过滤出有明确信号的
        active_signals = [s for s in signals if s.signal != "HOLD" and s.confidence >= threshold]

        if not active_signals:
            return None

        message = f"""🔔 <b>蔡森技术分析交易信号</b>
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━

"""

        for sig in active_signals:
            signal_emoji = "🟢" if sig.signal == "BUY" else "🔴"
            signal_text = "买入" if sig.signal == "BUY" else "卖出"

            message += f"""<b>{sig.name} ({sig.symbol})</b>
{signal_emoji} <b>信号: {signal_text}</b>
📊 置信度: {sig.confidence}%
📈 当前价格: {sig.current_price:.4f}
🔸 蔡森形态: {sig.pattern}
📍 入场区间: {sig.entry_zone}
🎯 目标位: {sig.target}
🛑 止损位: {sig.stop_loss}

📋 技术指标:
  • RSI: {sig.indicators['rsi']}
  • MACD: {'金叉' if sig.indicators['macd']['histogram'] > 0 else '死叉'}
  • 趋势: {'多头' if sig.indicators['trend'] == 'UP' else '空头'}

"""

        message += """━━━━━━━━━━━━━━━━━━━━
⚠️ <i>免责声明: 仅供参考，不构成投资建议</i>
📝 蔡森技术分析系统 | 24/7自动监控
"""

        return message

    def format_market_overview(self, signals: List[TradingSignal]) -> str:
        """格式化市场概览"""
        message = f"""📊 <b>市场技术概览</b>
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━

"""
        for sig in signals:
            signal_emoji = "🟢" if sig.signal == "BUY" else ("🔴" if sig.signal == "SELL" else "⚪")
            trend_emoji = "📈" if sig.indicators['trend'] == "UP" else "📉"

            message += f"""{sig.name}: {sig.current_price:.4f}
{signal_emoji} {sig.signal} ({sig.confidence}%) | {trend_emoji} {sig.pattern}
RSI: {sig.indicators['rsi']} | MACD: {'+' if sig.indicators['macd']['histogram'] > 0 else '-'}

"""

        next_time = (datetime.now() + timedelta(minutes=ANALYSIS_INTERVAL_MINUTES)).strftime('%H:%M')
        message += f"""━━━━━━━━━━━━━━━━━━━━
⏰ 下次分析: {next_time}"""

        return message

# ==================== 信号存储器 ====================

class SignalStorage:
    """信号本地存储"""

    def __init__(self, storage_dir: str = "signals"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_signals(self, signals: List[TradingSignal]):
        """保存信号到本地文件"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = os.path.join(self.storage_dir, f"signals_{date_str}.json")

        data = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "signals": [s.to_dict() for s in signals]
        }

        # 追加模式
        existing = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = [existing]
            except:
                existing = []

        existing.append(data)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 信号已保存到 {filename}")

    def get_today_signals(self) -> List:
        """获取今日信号"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = os.path.join(self.storage_dir, f"signals_{date_str}.json")

        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def generate_html_report(self, signals: List[TradingSignal]) -> str:
        """生成HTML报告"""
        now = datetime.now()

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="1800">
    <title>蔡森技术分析交易信号 - {now.strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 20px; }}
        .header h1 {{ color: #ffd700; font-size: 2em; margin-bottom: 10px; }}
        .header .time {{ color: #888; }}
        .stats {{ display: flex; justify-content: center; gap: 30px; margin-top: 15px; flex-wrap: wrap; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ color: #888; font-size: 0.9em; }}
        .buy {{ color: #00ff88; }}
        .sell {{ color: #ff6b6b; }}
        .hold {{ color: #ffd93d; }}

        .signals-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .signal-card {{ background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); transition: transform 0.3s; }}
        .signal-card:hover {{ transform: translateY(-5px); border-color: rgba(255,255,255,0.3); }}
        .signal-card.buy-signal {{ border-left: 4px solid #00ff88; }}
        .signal-card.sell-signal {{ border-left: 4px solid #ff6b6b; }}
        .signal-card.hold-signal {{ border-left: 4px solid #ffd93d; }}

        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .symbol-name {{ font-size: 1.3em; font-weight: bold; }}
        .signal-badge {{ padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em; }}
        .signal-badge.buy {{ background: rgba(0,255,136,0.2); color: #00ff88; }}
        .signal-badge.sell {{ background: rgba(255,107,107,0.2); color: #ff6b6b; }}
        .signal-badge.hold {{ background: rgba(255,217,61,0.2); color: #ffd93d; }}

        .price {{ font-size: 1.8em; font-weight: bold; margin-bottom: 10px; }}
        .pattern {{ color: #00d4ff; margin-bottom: 15px; }}
        .confidence-bar {{ background: rgba(255,255,255,0.1); border-radius: 10px; height: 20px; margin: 10px 0; overflow: hidden; }}
        .confidence-fill {{ height: 100%; border-radius: 10px; transition: width 0.5s; }}
        .confidence-fill.high {{ background: linear-gradient(90deg, #00ff88, #00d4ff); }}
        .confidence-fill.medium {{ background: linear-gradient(90deg, #ffd93d, #ff9f43); }}
        .confidence-fill.low {{ background: linear-gradient(90deg, #ff6b6b, #ee5a5a); }}

        .details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }}
        .detail-item {{ background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; }}
        .detail-label {{ color: #888; font-size: 0.8em; }}
        .detail-value {{ font-weight: bold; margin-top: 3px; }}

        .indicators {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); }}
        .indicator-row {{ display: flex; justify-content: space-between; margin: 5px 0; }}

        .footer {{ text-align: center; padding: 20px; color: #666; margin-top: 30px; }}
        .alert {{ background: rgba(255,107,107,0.2); border: 1px solid #ff6b6b; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 蔡森技术分析交易信号</h1>
            <div class="time">更新时间: {now.strftime('%Y-%m-%d %H:%M:%S')} | 下次更新: {(now + timedelta(minutes=30)).strftime('%H:%M')}</div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value buy">{len([s for s in signals if s.signal == 'BUY'])}</div>
                    <div class="stat-label">买入信号</div>
                </div>
                <div class="stat">
                    <div class="stat-value sell">{len([s for s in signals if s.signal == 'SELL'])}</div>
                    <div class="stat-label">卖出信号</div>
                </div>
                <div class="stat">
                    <div class="stat-value hold">{len([s for s in signals if s.signal == 'HOLD'])}</div>
                    <div class="stat-label">持有/观望</div>
                </div>
            </div>
        </div>
"""

        # 添加活跃信号警告
        active_signals = [s for s in signals if s.signal != 'HOLD' and s.confidence >= 60]
        if active_signals:
            html += f"""
        <div class="alert">
            ⚠️ <strong>活跃交易信号</strong>: {', '.join([f"{s.name} ({s.signal})" for s in active_signals])}
        </div>
"""

        html += """
        <div class="signals-grid">
"""

        for sig in signals:
            signal_class = f"{sig.signal.lower()}-signal"
            confidence_class = "high" if sig.confidence >= 70 else ("medium" if sig.confidence >= 50 else "low")

            html += f"""
            <div class="signal-card {signal_class}">
                <div class="card-header">
                    <div class="symbol-name">{sig.name}</div>
                    <div class="signal-badge {sig.signal.lower()}">{sig.signal}</div>
                </div>
                <div class="price">${sig.current_price:,.4f}</div>
                <div class="pattern">🔸 蔡森形态: {sig.pattern}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill {confidence_class}" style="width: {sig.confidence}%"></div>
                </div>
                <small>置信度: {sig.confidence}%</small>

                <div class="details">
                    <div class="detail-item">
                        <div class="detail-label">📍 入场区间</div>
                        <div class="detail-value">{sig.entry_zone}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">🎯 目标位</div>
                        <div class="detail-value">{sig.target}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">🛑 止损位</div>
                        <div class="detail-value">{sig.stop_loss}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">⏱️ 时间框架</div>
                        <div class="detail-value">{sig.timeframe}</div>
                    </div>
                </div>

                <div class="indicators">
                    <div class="indicator-row">
                        <span>RSI:</span>
                        <span>{sig.indicators['rsi']:.2f}</span>
                    </div>
                    <div class="indicator-row">
                        <span>MACD:</span>
                        <span>{'金叉 📈' if sig.indicators['macd']['histogram'] > 0 else '死叉 📉'}</span>
                    </div>
                    <div class="indicator-row">
                        <span>趋势:</span>
                        <span>{'多头 🟢' if sig.indicators['trend'] == 'UP' else '空头 🔴'}</span>
                    </div>
                </div>
            </div>
"""

        html += f"""
        </div>

        <div class="footer">
            <p>🔄 页面每30分钟自动刷新 | 蔡森技术分析系统 v1.0</p>
            <p>⚠️ 本系统仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
        </div>
    </div>
</body>
</html>"""

        # 保存HTML报告
        html_file = os.path.join(self.storage_dir, "report.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"📊 HTML报告已生成: {html_file}")
        return html_file

# ==================== 主服务类 ====================

class TradingAnalyzerService:
    """交易分析服务主类"""

    def __init__(self):
        self.analyzer = TechnicalAnalyzer(proxy_url=PROXY_URL)
        self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, proxy_url=PROXY_URL)
        self.storage = SignalStorage()
        self.running = False
        self.analysis_count = 0

    async def analyze_all(self) -> List[TradingSignal]:
        """分析所有品种"""
        signals = []

        for symbol, config in SYMBOLS.items():
            signal = await self.analyzer.analyze_symbol(symbol, config)
            if signal:
                signals.append(signal)
                logger.info(f"分析 {config['name']}: {signal.signal} ({signal.confidence}%)")

            # 避免API限流
            await asyncio.sleep(1.5)

        return signals

    async def run_analysis_cycle(self):
        """执行一次分析周期"""
        self.analysis_count += 1
        logger.info("=" * 50)
        logger.info(f"开始分析周期 #{self.analysis_count}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)

        # 分析所有品种
        signals = await self.analyze_all()

        if not signals:
            logger.warning("未获取到任何分析数据")
            return

        # 保存信号到本地
        self.storage.save_signals(signals)

        # 生成HTML报告
        self.storage.generate_html_report(signals)

        # 发送交易信号通知 (仅发送有明确信号的)
        signal_message = self.notifier.format_signal_message(signals, CONFIDENCE_THRESHOLD)
        if signal_message:
            success = await self.notifier.send_message(signal_message)
            if not success:
                logger.warning("Telegram发送失败，请查看本地HTML报告: signals/report.html")

        # 发送市场概览
        overview = self.notifier.format_market_overview(signals)
        await self.notifier.send_message(overview)

        logger.info(f"分析周期完成，共分析 {len(signals)} 个品种")
        logger.info(f"📊 查看HTML报告: file://{os.path.abspath('signals/report.html')}")

    async def start(self):
        """启动服务"""
        self.running = True
        logger.info("🚀 蔡森技术分析服务启动")
        logger.info(f"📡 监控品种: {len(SYMBOLS)} 个")
        logger.info(f"⏰ 分析间隔: {ANALYSIS_INTERVAL_MINUTES} 分钟")
        logger.info(f"📊 信号阈值: {CONFIDENCE_THRESHOLD}%")
        logger.info(f"💾 信号存储: signals/")
        if PROXY_URL:
            logger.info(f"🌐 使用代理: {PROXY_URL}")

        # 发送启动通知
        startup_msg = f"""🚀 <b>蔡森技术分析服务已启动</b>
━━━━━━━━━━━━━━━━━━━━
📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📡 监控品种: {len(SYMBOLS)} 个
⏰ 分析间隔: {ANALYSIS_INTERVAL_MINUTES} 分钟
📊 信号阈值: {CONFIDENCE_THRESHOLD}%

监控品种列表:
"""
        for symbol, config in SYMBOLS.items():
            startup_msg += f"• {config['name']} ({symbol})\n"

        startup_msg += """
━━━━━━━━━━━━━━━━━━━━
<i>服务将在后台持续运行，发现交易信号时自动推送</i>
"""
        await self.notifier.send_message(startup_msg)

        # 立即执行一次分析
        await self.run_analysis_cycle()

        # 循环执行
        while self.running:
            await asyncio.sleep(ANALYSIS_INTERVAL_MINUTES * 60)
            if self.running:
                await self.run_analysis_cycle()

    async def stop(self):
        """停止服务"""
        self.running = False
        await self.analyzer.close_session()
        await self.notifier.close_session()
        logger.info("服务已停止")


async def main():
    """主函数"""
    service = TradingAnalyzerService()

    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("收到停止信号 (Ctrl+C)")
        await service.stop()
    except Exception as e:
        logger.error(f"服务错误: {e}")
        import traceback
        traceback.print_exc()
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
