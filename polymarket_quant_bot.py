#!/usr/bin/env python3
"""
Polymarket 量化交易机器人
支持多种策略的回测和模拟交易
初始仓位: $10,000
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 枚举和数据类 ====================

class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class StrategyType(Enum):
    MARKET_MAKING = "Market Making"
    ARBITRAGE = "Arbitrage"
    MOMENTUM = "Momentum"
    MEAN_REVERSION = "Mean Reversion"
    SENTIMENT = "Sentiment Based"
    WHALE_TRACKING = "Whale Tracking"

@dataclass
class Market:
    """预测市场数据类"""
    market_id: str
    question: str
    category: str
    yes_price: float  # 0.0 - 1.0
    no_price: float   # 0.0 - 1.0
    volume: float
    liquidity: float
    timestamp: datetime
    resolution: Optional[bool] = None  # True=Yes wins, False=No wins, None=unresolved

@dataclass
class Position:
    """持仓数据类"""
    market_id: str
    side: str  # "YES" or "NO"
    size: float  # 份额数量
    entry_price: float
    current_price: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    @property
    def value(self) -> float:
        return self.size * self.current_price

    @property
    def pnl(self) -> float:
        return self.size * (self.current_price - self.entry_price)

    @property
    def pnl_pct(self) -> float:
        if self.entry_price == 0:
            return 0
        return (self.current_price - self.entry_price) / self.entry_price * 100

@dataclass
class Trade:
    """交易记录"""
    trade_id: str
    market_id: str
    side: str
    action: str  # "BUY" or "SELL"
    size: float
    price: float
    timestamp: datetime
    strategy: StrategyType
    pnl: float = 0

@dataclass
class Portfolio:
    """投资组合"""
    cash: float
    positions: Dict[str, Position] = field(default_factory=dict)
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)

    @property
    def total_value(self) -> float:
        return self.cash + sum(p.value for p in self.positions.values())

    @property
    def total_pnl(self) -> float:
        return sum(p.pnl for p in self.positions.values())

# ==================== 市场数据生成器 ====================

class MarketDataGenerator:
    """模拟市场数据生成器"""

    CATEGORIES = ["Politics", "Crypto", "Sports", "Economics", "Technology", "Culture"]
    QUESTIONS = {
        "Politics": [
            "Will candidate X win the 2026 election?",
            "Will the bill pass congress by March?",
            "Will there be a government shutdown in Q1?",
        ],
        "Crypto": [
            "Will BTC exceed $120K by March 2026?",
            "Will ETH flip BTC market cap in 2026?",
            "Will a major exchange collapse in Q1?",
        ],
        "Sports": [
            "Will Lakers win the NBA championship?",
            "Will Messi score 30+ goals this season?",
            "Will the Super Bowl go to overtime?",
        ],
        "Economics": [
            "Will Fed cut rates in Q1 2026?",
            "Will US GDP grow above 3% in Q1?",
            "Will unemployment fall below 3.5%?",
        ],
        "Technology": [
            "Will GPT-5 launch before July 2026?",
            "Will Apple release AR glasses in 2026?",
            "Will an AI pass the Turing test publicly?",
        ],
        "Culture": [
            "Will TikTok be banned in the US?",
            "Will a movie break $3B box office?",
            "Will a celebrity run for president?",
        ]
    }

    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.market_counter = 0

    def generate_market(self, timestamp: datetime, volatility: float = 0.02) -> Market:
        """生成单个市场"""
        category = np.random.choice(self.CATEGORIES)
        question = np.random.choice(self.QUESTIONS[category])

        # 生成初始价格（基于概率分布）
        base_prob = np.random.beta(2, 2)  # 倾向于中间值
        yes_price = round(base_prob, 3)
        no_price = round(1 - yes_price, 3)

        # 生成成交量和流动性
        volume = np.random.lognormal(8, 1)  # 日均成交量
        liquidity = np.random.lognormal(7, 0.8)

        self.market_counter += 1

        return Market(
            market_id=f"market_{self.market_counter:04d}",
            question=question,
            category=category,
            yes_price=yes_price,
            no_price=no_price,
            volume=volume,
            liquidity=liquidity,
            timestamp=timestamp
        )

    def update_market_price(self, market: Market, news_impact: float = 0) -> Market:
        """更新市场价格（模拟价格变动）"""
        # 基于随机游走 + 新闻影响
        change = np.random.normal(0, 0.01) + news_impact
        new_yes = np.clip(market.yes_price + change, 0.01, 0.99)
        new_no = 1 - new_yes

        # 更新成交量和流动性
        volume_change = np.random.lognormal(0, 0.1)
        liquidity_change = np.random.lognormal(0, 0.05)

        return Market(
            market_id=market.market_id,
            question=market.question,
            category=market.category,
            yes_price=round(new_yes, 3),
            no_price=round(new_no, 3),
            volume=market.volume * volume_change,
            liquidity=market.liquidity * liquidity_change,
            timestamp=market.timestamp + timedelta(hours=1),
            resolution=market.resolution
        )

    def resolve_market(self, market: Market, probability_bias: float = 0.5) -> Market:
        """解决市场（确定结果）"""
        # 基于最终概率决定结果
        resolution = np.random.random() < (market.yes_price * probability_bias + 0.5 * (1 - probability_bias))
        return Market(
            market_id=market.market_id,
            question=market.question,
            category=market.category,
            yes_price=1.0 if resolution else 0.0,
            no_price=0.0 if resolution else 1.0,
            volume=market.volume,
            liquidity=market.liquidity,
            timestamp=market.timestamp,
            resolution=resolution
        )

    def generate_historical_data(self, days: int = 90, markets_per_day: int = 5) -> List[Market]:
        """生成历史市场数据"""
        markets = []
        start_date = datetime.now() - timedelta(days=days)

        for day in range(days):
            current_date = start_date + timedelta(days=day)
            for _ in range(markets_per_day):
                market = self.generate_market(current_date)

                # 模拟市场生命周期
                lifecycle_hours = np.random.randint(24, 720)  # 1-30天
                for hour in range(lifecycle_hours):
                    market = self.update_market_price(market)
                    if hour == lifecycle_hours - 1:
                        market = self.resolve_market(market)
                    markets.append(market)

        return markets

# ==================== 交易策略 ====================

class TradingStrategy:
    """交易策略基类"""

    def __init__(self, name: str, strategy_type: StrategyType):
        self.name = name
        self.strategy_type = strategy_type
        self.positions_opened = 0
        self.positions_closed = 0
        self.total_pnl = 0
        self.win_count = 0
        self.loss_count = 0

    def analyze(self, market: Market, portfolio: Portfolio) -> Optional[Tuple[Signal, str, float]]:
        """
        分析市场并生成信号
        Returns: (signal, side, suggested_size)
        """
        raise NotImplementedError

    def get_stats(self) -> Dict:
        """获取策略统计"""
        total = self.win_count + self.loss_count
        win_rate = self.win_count / total if total > 0 else 0
        avg_pnl = self.total_pnl / total if total > 0 else 0

        return {
            "name": self.name,
            "type": self.strategy_type.value,
            "positions_opened": self.positions_opened,
            "positions_closed": self.positions_closed,
            "win_rate": win_rate * 100,
            "total_pnl": self.total_pnl,
            "avg_pnl": avg_pnl
        }


class MarketMakingStrategy(TradingStrategy):
    """
    做市商策略
    在买卖两侧挂单，赚取价差
    """

    def __init__(self, spread_target: float = 0.02, position_limit: float = 500):
        super().__init__("Market Maker", StrategyType.MARKET_MAKING)
        self.spread_target = spread_target
        self.position_limit = position_limit

    def analyze(self, market: Market, portfolio: Portfolio) -> Optional[Tuple[Signal, str, float]]:
        # 检查价差是否足够
        spread = abs(market.yes_price - (1 - market.no_price))

        if spread < self.spread_target:
            return None

        # 检查当前持仓
        current_position = portfolio.positions.get(market.market_id)
        if current_position and current_position.value > self.position_limit:
            return Signal.HOLD, current_position.side, 0

        # 选择流动性更好的一侧
        if market.yes_price > 0.5:
            side = "NO"
            entry_price = market.no_price
        else:
            side = "YES"
            entry_price = market.yes_price

        # 计算建议仓位
        suggested_size = min(self.position_limit / entry_price, portfolio.cash * 0.1 / entry_price)

        if suggested_size < 10:
            return None

        return Signal.BUY, side, suggested_size


class ArbitrageStrategy(TradingStrategy):
    """
    套利策略
    利用价格 inefficiencies
    """

    def __init__(self, min_profit_threshold: float = 0.005):
        super().__init__("Arbitrage", StrategyType.ARBITRAGE)
        self.min_profit_threshold = min_profit_threshold

    def analyze(self, market: Market, portfolio: Portfolio) -> Optional[Tuple[Signal, str, float]]:
        # 检查 YES + NO 是否小于 1（套利机会）
        total_price = market.yes_price + market.no_price

        if total_price >= 1.0 - self.min_profit_threshold:
            return None

        # 计算套利利润
        profit_pct = (1.0 - total_price) / total_price

        if profit_pct < self.min_profit_threshold:
            return None

        # 套利：同时买 YES 和 NO
        # 返回较大价差的一侧
        side = "YES" if market.yes_price <= market.no_price else "NO"
        entry_price = market.yes_price if side == "YES" else market.no_price

        # 套利仓位
        max_size = portfolio.cash * 0.2 / entry_price
        suggested_size = min(max_size, 1000)

        return Signal.BUY, side, suggested_size


class MomentumStrategy(TradingStrategy):
    """
    动量策略
    追踪价格趋势
    """

    def __init__(self, lookback: int = 10, threshold: float = 0.05):
        super().__init__("Momentum", StrategyType.MOMENTUM)
        self.lookback = lookback
        self.threshold = threshold
        self.price_history = defaultdict(list)

    def analyze(self, market: Market, portfolio: Portfolio) -> Optional[Tuple[Signal, str, float]]:
        # 记录价格历史
        self.price_history[market.market_id].append(market.yes_price)

        if len(self.price_history[market.market_id]) < self.lookback:
            return None

        # 计算动量
        prices = self.price_history[market.market_id][-self.lookback:]
        momentum = (prices[-1] - prices[0]) / prices[0] if prices[0] > 0 else 0

        # 动量信号
        if momentum > self.threshold:
            side = "YES"
            entry_price = market.yes_price
        elif momentum < -self.threshold:
            side = "NO"
            entry_price = market.no_price
        else:
            return None

        # 检查是否已有持仓
        if market.market_id in portfolio.positions:
            return Signal.HOLD, side, 0

        suggested_size = portfolio.cash * 0.1 / entry_price

        return Signal.BUY, side, min(suggested_size, 500)


class MeanReversionStrategy(TradingStrategy):
    """
    均值回归策略
    在极端价格时反向操作
    """

    def __init__(self, oversold_threshold: float = 0.25, overbought_threshold: float = 0.75):
        super().__init__("Mean Reversion", StrategyType.MEAN_REVERSION)
        self.oversold = oversold_threshold
        self.overbought = overbought_threshold

    def analyze(self, market: Market, portfolio: Portfolio) -> Optional[Tuple[Signal, str, float]]:
        # 均值回归假设价格会回到 0.5
        if market.yes_price < self.oversold:
            # YES 超卖，买入 YES
            side = "YES"
            entry_price = market.yes_price
            confidence = (self.oversold - market.yes_price) / self.oversold
        elif market.yes_price > self.overbought:
            # YES 超买，买入 NO
            side = "NO"
            entry_price = market.no_price
            confidence = (market.yes_price - self.overbought) / (1 - self.overbought)
        else:
            return None

        if market.market_id in portfolio.positions:
            return Signal.HOLD, side, 0

        # 根据置信度调整仓位
        suggested_size = portfolio.cash * 0.15 * confidence / entry_price

        return Signal.BUY, side, min(suggested_size, 800)


class SentimentStrategy(TradingStrategy):
    """
    情绪策略
    基于市场成交量和流动性变化
    """

    def __init__(self, volume_threshold: float = 2.0):
        super().__init__("Sentiment", StrategyType.SENTIMENT)
        self.volume_threshold = volume_threshold
        self.baseline_volume = {}

    def analyze(self, market: Market, portfolio: Portfolio) -> Optional[Tuple[Signal, str, float]]:
        # 建立基线
        if market.market_id not in self.baseline_volume:
            self.baseline_volume[market.market_id] = market.volume
            return None

        baseline = self.baseline_volume[market.market_id]
        volume_ratio = market.volume / baseline if baseline > 0 else 1

        # 成交量激增
        if volume_ratio > self.volume_threshold:
            # 跟随资金方向
            side = "YES" if market.yes_price > 0.5 else "NO"
            entry_price = market.yes_price if side == "YES" else market.no_price

            if market.market_id in portfolio.positions:
                return Signal.HOLD, side, 0

            suggested_size = portfolio.cash * 0.12 / entry_price
            return Signal.BUY, side, min(suggested_size, 600)

        return None


class WhaleTrackingStrategy(TradingStrategy):
    """
    大户追踪策略
    检测大单并跟随
    """

    def __init__(self, large_order_threshold: float = 10000):
        super().__init__("Whale Tracking", StrategyType.WHALE_TRACKING)
        self.large_order_threshold = large_order_threshold

    def analyze(self, market: Market, portfolio: Portfolio) -> Optional[Tuple[Signal, str, float]]:
        # 检测流动性变化（大户进入的信号）
        if market.liquidity > self.large_order_threshold:
            # 高流动性通常意味着大户参与
            # 跟随概率较高的一侧
            if market.yes_price > 0.55:
                side = "YES"
                entry_price = market.yes_price
            elif market.no_price > 0.55:
                side = "NO"
                entry_price = market.no_price
            else:
                return None

            if market.market_id in portfolio.positions:
                return Signal.HOLD, side, 0

            suggested_size = portfolio.cash * 0.08 / entry_price
            return Signal.BUY, side, min(suggested_size, 400)

        return None

# ==================== 风险管理器 ====================

class RiskManager:
    """风险管理器"""

    def __init__(
        self,
        max_position_size: float = 2000,
        max_positions: int = 10,
        max_single_market_exposure: float = 0.15,
        daily_loss_limit: float = 0.10,
        max_drawdown: float = 0.20
    ):
        self.max_position_size = max_position_size
        self.max_positions = max_positions
        self.max_single_market_exposure = max_single_market_exposure
        self.daily_loss_limit = daily_loss_limit
        self.max_drawdown = max_drawdown
        self.peak_equity = 0
        self.daily_start_equity = 0
        self.current_day = None

    def check_position_allowed(self, portfolio: Portfolio, market: Market, size: float, price: float) -> Tuple[bool, str]:
        """检查是否允许开仓"""
        # 检查仓位数量
        if len(portfolio.positions) >= self.max_positions:
            return False, "Maximum number of positions reached"

        # 检查单仓位大小
        position_value = size * price
        if position_value > self.max_position_size:
            return False, f"Position size {position_value:.2f} exceeds max {self.max_position_size}"

        # 检查单一市场敞口
        total_value = portfolio.total_value
        if position_value / total_value > self.max_single_market_exposure:
            return False, f"Position exceeds {self.max_single_market_exposure*100}% of portfolio"

        # 检查现金
        if position_value > portfolio.cash:
            return False, "Insufficient cash"

        return True, "OK"

    def check_should_close(self, position: Position, current_price: float) -> Tuple[bool, str]:
        """检查是否应该平仓"""
        # 止损检查
        if position.stop_loss:
            if position.side == "YES" and current_price <= position.stop_loss:
                return True, "Stop loss triggered"
            elif position.side == "NO" and current_price >= position.stop_loss:
                return True, "Stop loss triggered"

        # 止盈检查
        if position.take_profit:
            if position.side == "YES" and current_price >= position.take_profit:
                return True, "Take profit triggered"
            elif position.side == "NO" and current_price <= position.take_profit:
                return True, "Take profit triggered"

        return False, ""

    def update_daily_stats(self, portfolio: Portfolio, current_date: datetime):
        """更新每日统计"""
        if self.current_day != current_date.date():
            self.current_day = current_date.date()
            self.daily_start_equity = portfolio.total_value

        # 更新峰值
        if portfolio.total_value > self.peak_equity:
            self.peak_equity = portfolio.total_value

    def check_risk_limits(self, portfolio: Portfolio) -> Tuple[bool, str]:
        """检查风险限制"""
        # 检查每日损失
        if self.daily_start_equity > 0:
            daily_pnl_pct = (portfolio.total_value - self.daily_start_equity) / self.daily_start_equity
            if daily_pnl_pct < -self.daily_loss_limit:
                return False, f"Daily loss limit exceeded: {daily_pnl_pct*100:.2f}%"

        # 检查最大回撤
        if self.peak_equity > 0:
            drawdown = (self.peak_equity - portfolio.total_value) / self.peak_equity
            if drawdown > self.max_drawdown:
                return False, f"Max drawdown exceeded: {drawdown*100:.2f}%"

        return True, ""

    def set_stop_loss_take_profit(self, position: Position, market: Market) -> Position:
        """设置止损止盈"""
        if position.side == "YES":
            position.stop_loss = position.entry_price * 0.85  # 15% 止损
            position.take_profit = min(position.entry_price * 1.3, 0.99)  # 30% 止盈
        else:
            position.stop_loss = position.entry_price * 0.85
            position.take_profit = min(position.entry_price * 1.3, 0.99)

        return position

# ==================== 回测引擎 ====================

class BacktestEngine:
    """回测引擎"""

    def __init__(
        self,
        initial_capital: float = 10000,
        start_date: datetime = None,
        end_date: datetime = None,
        fee_rate: float = 0.01  # 1% 交易费
    ):
        self.initial_capital = initial_capital
        self.start_date = start_date or datetime.now() - timedelta(days=90)
        self.end_date = end_date or datetime.now()
        self.fee_rate = fee_rate

        self.portfolio = Portfolio(cash=initial_capital)
        self.risk_manager = RiskManager()
        self.strategies: List[TradingStrategy] = []
        self.market_generator = MarketDataGenerator()

        # 统计数据
        self.stats = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_fees": 0,
            "max_drawdown": 0,
            "sharpe_ratio": 0,
            "win_rate": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "profit_factor": 0,
        }

    def add_strategy(self, strategy: TradingStrategy):
        """添加策略"""
        self.strategies.append(strategy)

    def run(self, days: int = 90, verbose: bool = True) -> Dict:
        """运行回测"""
        if verbose:
            print("=" * 60)
            print("Polymarket 量化交易机器人回测")
            print("=" * 60)
            print(f"初始资金: ${self.initial_capital:,.2f}")
            print(f"回测天数: {days}")
            print(f"策略数量: {len(self.strategies)}")
            print(f"交易费率: {self.fee_rate*100}%")
            print("=" * 60)

        # 生成市场数据
        markets = self.market_generator.generate_historical_data(days=days, markets_per_day=3)

        # 按时间排序
        markets.sort(key=lambda x: x.timestamp)

        # 活跃市场跟踪
        active_markets = {}

        for market in markets:
            current_date = market.timestamp
            self.risk_manager.update_daily_stats(self.portfolio, current_date)

            # 检查风险限制
            risk_ok, risk_msg = self.risk_manager.check_risk_limits(self.portfolio)
            if not risk_ok:
                if verbose:
                    print(f"[RISK] {risk_msg} - 停止交易")
                break

            # 更新活跃市场
            if market.market_id not in active_markets:
                active_markets[market.market_id] = market

            # 更新现有持仓价格
            if market.market_id in self.portfolio.positions:
                pos = self.portfolio.positions[market.market_id]
                pos.current_price = market.yes_price if pos.side == "YES" else market.no_price

                # 检查是否需要平仓
                should_close, close_reason = self.risk_manager.check_should_close(
                    pos, pos.current_price
                )

                if should_close or market.resolution is not None:
                    self._close_position(market, close_reason or "Market resolved")

            # 如果市场已解决，跳过策略分析
            if market.resolution is not None:
                continue

            # 运行每个策略
            for strategy in self.strategies:
                result = strategy.analyze(market, self.portfolio)

                if result is None:
                    continue

                signal, side, suggested_size = result

                if signal == Signal.BUY and suggested_size > 0:
                    # 检查是否允许开仓
                    allowed, msg = self.risk_manager.check_position_allowed(
                        self.portfolio, market, suggested_size,
                        market.yes_price if side == "YES" else market.no_price
                    )

                    if allowed:
                        self._open_position(market, side, suggested_size, strategy)

            # 记录权益曲线
            self.portfolio.equity_curve.append((current_date, self.portfolio.total_value))

        # 平掉所有剩余仓位
        self._close_all_positions()

        # 计算最终统计
        self._calculate_stats()

        if verbose:
            self._print_results()

        return self.stats

    def _open_position(self, market: Market, side: str, size: float, strategy: TradingStrategy):
        """开仓"""
        price = market.yes_price if side == "YES" else market.no_price
        cost = size * price
        fee = cost * self.fee_rate

        if cost + fee > self.portfolio.cash:
            size = (self.portfolio.cash - fee) / price

        if size < 10:  # 最小仓位
            return

        # 创建持仓
        position = Position(
            market_id=market.market_id,
            side=side,
            size=size,
            entry_price=price,
            current_price=price,
            entry_time=market.timestamp
        )

        # 设置止损止盈
        position = self.risk_manager.set_stop_loss_take_profit(position, market)

        # 更新投资组合
        self.portfolio.cash -= (size * price + fee)
        self.portfolio.positions[market.market_id] = position

        # 记录交易
        trade = Trade(
            trade_id=f"trade_{len(self.portfolio.trades):04d}",
            market_id=market.market_id,
            side=side,
            action="BUY",
            size=size,
            price=price,
            timestamp=market.timestamp,
            strategy=strategy.strategy_type
        )
        self.portfolio.trades.append(trade)

        # 更新策略统计
        strategy.positions_opened += 1
        self.stats["total_trades"] += 1
        self.stats["total_fees"] += fee

    def _close_position(self, market: Market, reason: str):
        """平仓"""
        if market.market_id not in self.portfolio.positions:
            return

        position = self.portfolio.positions[market.market_id]

        # 确定平仓价格
        if market.resolution is not None:
            if market.resolution:  # YES wins
                exit_price = 1.0 if position.side == "YES" else 0.0
            else:  # NO wins
                exit_price = 0.0 if position.side == "YES" else 1.0
        else:
            exit_price = market.yes_price if position.side == "YES" else market.no_price

        # 计算收益
        gross_value = position.size * exit_price
        fee = gross_value * self.fee_rate
        pnl = position.size * (exit_price - position.entry_price) - fee

        # 更新投资组合
        self.portfolio.cash += gross_value - fee

        # 记录交易
        trade = Trade(
            trade_id=f"trade_{len(self.portfolio.trades):04d}",
            market_id=market.market_id,
            side=position.side,
            action="SELL",
            size=position.size,
            price=exit_price,
            timestamp=market.timestamp,
            strategy=StrategyType.MARKET_MAKING,  # 可以从position存储
            pnl=pnl
        )
        self.portfolio.trades.append(trade)

        # 更新统计
        if pnl > 0:
            self.stats["winning_trades"] += 1
        else:
            self.stats["losing_trades"] += 1

        # 删除持仓
        del self.portfolio.positions[market.market_id]

    def _close_all_positions(self):
        """平掉所有仓位"""
        positions_to_close = list(self.portfolio.positions.keys())
        for market_id in positions_to_close:
            if market_id in self.portfolio.positions:
                # 创建一个模拟的已解决市场
                pos = self.portfolio.positions[market_id]
                mock_market = Market(
                    market_id=market_id,
                    question="",
                    category="",
                    yes_price=1.0 if pos.side == "YES" else 0.0,
                    no_price=0.0 if pos.side == "YES" else 1.0,
                    volume=0,
                    liquidity=0,
                    timestamp=datetime.now(),
                    resolution=pos.side == "YES"  # 模拟盈利结果
                )
                self._close_position(mock_market, "Backtest end")

    def _calculate_stats(self):
        """计算统计数据"""
        trades = self.portfolio.trades
        sell_trades = [t for t in trades if t.action == "SELL"]

        total = len(sell_trades)
        wins = [t for t in sell_trades if t.pnl > 0]
        losses = [t for t in sell_trades if t.pnl <= 0]

        self.stats["win_rate"] = len(wins) / total * 100 if total > 0 else 0
        self.stats["avg_win"] = np.mean([t.pnl for t in wins]) if wins else 0
        self.stats["avg_loss"] = np.mean([t.pnl for t in losses]) if losses else 0

        total_wins = sum(t.pnl for t in wins)
        total_losses = abs(sum(t.pnl for t in losses))
        self.stats["profit_factor"] = total_wins / total_losses if total_losses > 0 else float('inf')

        # 计算最大回撤
        if self.portfolio.equity_curve:
            equity_values = [e[1] for e in self.portfolio.equity_curve]
            peak = equity_values[0]
            max_dd = 0
            for value in equity_values:
                if value > peak:
                    peak = value
                dd = (peak - value) / peak
                if dd > max_dd:
                    max_dd = dd
            self.stats["max_drawdown"] = max_dd * 100

        # 计算 Sharpe Ratio (简化版)
        if len(equity_values) > 1:
            returns = np.diff(equity_values) / equity_values[:-1]
            if np.std(returns) > 0:
                self.stats["sharpe_ratio"] = np.mean(returns) / np.std(returns) * np.sqrt(252)

        # 最终资产
        self.stats["final_equity"] = self.portfolio.total_value
        self.stats["total_return"] = (self.portfolio.total_value - self.initial_capital) / self.initial_capital * 100
        self.stats["total_pnl"] = self.portfolio.total_value - self.initial_capital

    def _print_results(self):
        """打印结果"""
        print("\n" + "=" * 60)
        print("回测结果")
        print("=" * 60)

        print(f"\n【资金状况】")
        print(f"  初始资金:   ${self.initial_capital:,.2f}")
        print(f"  最终资金:   ${self.stats['final_equity']:,.2f}")
        print(f"  总收益:     ${self.stats['total_pnl']:,.2f} ({self.stats['total_return']:.2f}%)")
        print(f"  总手续费:   ${self.stats['total_fees']:,.2f}")

        print(f"\n【交易统计】")
        print(f"  总交易次数: {self.stats['total_trades']}")
        print(f"  盈利次数:   {self.stats['winning_trades']}")
        print(f"  亏损次数:   {self.stats['losing_trades']}")
        print(f"  胜率:       {self.stats['win_rate']:.2f}%")

        print(f"\n【风险指标】")
        print(f"  最大回撤:   {self.stats['max_drawdown']:.2f}%")
        print(f"  Sharpe比率: {self.stats['sharpe_ratio']:.2f}")
        print(f"  盈亏比:     {abs(self.stats['avg_win']/self.stats['avg_loss']) if self.stats['avg_loss'] != 0 else 'N/A':.2f}")
        print(f"  利润因子:   {self.stats['profit_factor']:.2f}")

        print(f"\n【单笔统计】")
        print(f"  平均盈利:   ${self.stats['avg_win']:.2f}")
        print(f"  平均亏损:   ${self.stats['avg_loss']:.2f}")

        print("\n" + "=" * 60)

        # 策略统计
        print("\n【各策略表现】")
        for strategy in self.strategies:
            stats = strategy.get_stats()
            print(f"\n  {stats['name']} ({stats['type']}):")
            print(f"    开仓次数: {stats['positions_opened']}")
            print(f"    平仓次数: {stats['positions_closed']}")
            print(f"    胜率:     {stats['win_rate']:.2f}%")
            print(f"    总盈亏:   ${stats['total_pnl']:.2f}")

    def generate_report(self, filename: str = "backtest_report.html") -> str:
        """生成HTML报告"""
        # 生成图表
        self._generate_charts()

        # 生成HTML
        html = self._create_html_report()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        return filename

    def _generate_charts(self):
        """生成图表"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. 权益曲线
        ax1 = axes[0, 0]
        if self.portfolio.equity_curve:
            dates = [e[0] for e in self.portfolio.equity_curve]
            values = [e[1] for e in self.portfolio.equity_curve]
            ax1.plot(dates, values, 'b-', linewidth=1.5, label='Equity')
            ax1.axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.7, label='Initial')
            ax1.fill_between(dates, self.initial_capital, values, alpha=0.3)
            ax1.set_title('Equity Curve', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Portfolio Value ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        # 2. 收益分布
        ax2 = axes[0, 1]
        sell_trades = [t for t in self.portfolio.trades if t.action == "SELL"]
        if sell_trades:
            pnls = [t.pnl for t in sell_trades]
            colors = ['green' if p > 0 else 'red' for p in pnls]
            ax2.bar(range(len(pnls)), pnls, color=colors, alpha=0.7)
            ax2.axhline(y=0, color='black', linewidth=0.5)
            ax2.set_title('Trade P&L Distribution', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Trade #')
            ax2.set_ylabel('P&L ($)')
            ax2.grid(True, alpha=0.3)

        # 3. 按策略的盈亏
        ax3 = axes[1, 0]
        strategy_pnls = defaultdict(list)
        for t in sell_trades:
            strategy_pnls[t.strategy.value].append(t.pnl)

        if strategy_pnls:
            strategies = list(strategy_pnls.keys())
            total_pnls = [sum(strategy_pnls[s]) for s in strategies]
            colors = ['green' if p > 0 else 'red' for p in total_pnls]
            bars = ax3.barh(strategies, total_pnls, color=colors, alpha=0.7)
            ax3.axvline(x=0, color='black', linewidth=0.5)
            ax3.set_title('P&L by Strategy', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Total P&L ($)')
            ax3.grid(True, alpha=0.3)

        # 4. 关键指标雷达图 -> 改为柱状图
        ax4 = axes[1, 1]
        metrics = ['Win Rate', 'Profit Factor', 'Sharpe', 'Return %']
        values = [
            self.stats['win_rate'],
            min(self.stats['profit_factor'], 5) * 20,  # 归一化
            (self.stats['sharpe_ratio'] + 2) * 25,  # 归一化
            self.stats['total_return']
        ]
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']
        bars = ax4.bar(metrics, values, color=colors, alpha=0.7)
        ax4.set_title('Key Performance Metrics', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Value (normalized)')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('backtest_charts.png', dpi=150, bbox_inches='tight')
        plt.close()

    def _create_html_report(self) -> str:
        """创建HTML报告"""
        now = datetime.now()

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polymarket 量化交易回测报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            padding: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            margin-bottom: 30px;
        }}
        .header h1 {{ color: #ffd700; font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ color: #888; font-size: 1.1em; }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .summary-card.profit {{ border-left: 4px solid #00ff88; }}
        .summary-card.loss {{ border-left: 4px solid #ff6b6b; }}
        .summary-card.neutral {{ border-left: 4px solid #ffd93d; }}

        .summary-value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .summary-label {{ color: #888; font-size: 0.9em; }}
        .profit-text {{ color: #00ff88; }}
        .loss-text {{ color: #ff6b6b; }}

        .section {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .section h2 {{
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        th {{
            background: rgba(0,0,0,0.3);
            color: #00d4ff;
            font-weight: 600;
        }}
        tr:hover {{ background: rgba(255,255,255,0.05); }}

        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            border-radius: 10px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }}
        .metric-item {{
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 10px;
        }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; color: #00d4ff; }}
        .metric-label {{ color: #888; font-size: 0.85em; }}

        .strategy-card {{
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        }}
        .strategy-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .strategy-name {{ font-size: 1.2em; font-weight: bold; }}
        .strategy-type {{ color: #888; font-size: 0.9em; }}

        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 30px;
        }}

        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-success {{ background: rgba(0,255,136,0.2); color: #00ff88; }}
        .badge-danger {{ background: rgba(255,107,107,0.2); color: #ff6b6b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Polymarket 量化交易回测报告</h1>
            <div class="subtitle">基于 OpenClaw 机器人策略的模拟回测分析</div>
            <div class="subtitle" style="margin-top: 10px;">生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>

        <!-- 核心指标概览 -->
        <div class="summary-grid">
            <div class="summary-card {'profit' if self.stats['total_return'] >= 0 else 'loss'}">
                <div class="summary-label">初始资金</div>
                <div class="summary-value">${self.initial_capital:,.2f}</div>
            </div>
            <div class="summary-card {'profit' if self.stats['total_return'] >= 0 else 'loss'}">
                <div class="summary-label">最终资金</div>
                <div class="summary-value {'profit-text' if self.stats['total_return'] >= 0 else 'loss-text'}">${self.stats['final_equity']:,.2f}</div>
            </div>
            <div class="summary-card {'profit' if self.stats['total_pnl'] >= 0 else 'loss'}">
                <div class="summary-label">总收益</div>
                <div class="summary-value {'profit-text' if self.stats['total_pnl'] >= 0 else 'loss-text'}">${self.stats['total_pnl']:,.2f}</div>
            </div>
            <div class="summary-card {'profit' if self.stats['total_return'] >= 0 else 'loss'}">
                <div class="summary-label">收益率</div>
                <div class="summary-value {'profit-text' if self.stats['total_return'] >= 0 else 'loss-text'}">{self.stats['total_return']:.2f}%</div>
            </div>
        </div>

        <!-- 交易统计 -->
        <div class="section">
            <h2>📊 交易统计</h2>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">总交易次数</div>
                    <div class="metric-value">{self.stats['total_trades']}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">盈利次数</div>
                    <div class="metric-value" style="color: #00ff88;">{self.stats['winning_trades']}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">亏损次数</div>
                    <div class="metric-value" style="color: #ff6b6b;">{self.stats['losing_trades']}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">胜率</div>
                    <div class="metric-value">{self.stats['win_rate']:.2f}%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">平均盈利</div>
                    <div class="metric-value" style="color: #00ff88;">${self.stats['avg_win']:.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">平均亏损</div>
                    <div class="metric-value" style="color: #ff6b6b;">${self.stats['avg_loss']:.2f}</div>
                </div>
            </div>
        </div>

        <!-- 风险指标 -->
        <div class="section">
            <h2>⚠️ 风险指标</h2>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">最大回撤</div>
                    <div class="metric-value" style="color: {'#00ff88' if self.stats['max_drawdown'] < 10 else '#ff6b6b'};">{self.stats['max_drawdown']:.2f}%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Sharpe 比率</div>
                    <div class="metric-value">{self.stats['sharpe_ratio']:.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">利润因子</div>
                    <div class="metric-value">{self.stats['profit_factor']:.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">总手续费</div>
                    <div class="metric-value">${self.stats['total_fees']:,.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">盈亏比</div>
                    <div class="metric-value">{abs(self.stats['avg_win']/self.stats['avg_loss']) if self.stats['avg_loss'] != 0 else 'N/A':.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">回测天数</div>
                    <div class="metric-value">90</div>
                </div>
            </div>
        </div>

        <!-- 图表 -->
        <div class="section">
            <h2>📈 回测图表</h2>
            <div class="chart-container">
                <img src="backtest_charts.png" alt="Backtest Charts">
            </div>
        </div>

        <!-- 策略表现 -->
        <div class="section">
            <h2>🎯 各策略表现</h2>
"""

        for strategy in self.strategies:
            stats = strategy.get_stats()
            is_profitable = stats['total_pnl'] >= 0
            html += f"""
            <div class="strategy-card">
                <div class="strategy-header">
                    <div>
                        <div class="strategy-name">{stats['name']}</div>
                        <div class="strategy-type">{stats['type']}</div>
                    </div>
                    <span class="badge {'badge-success' if is_profitable else 'badge-danger'}">
                        {'Profitable' if is_profitable else 'Loss'}
                    </span>
                </div>
                <div class="metrics-grid" style="margin-top: 15px;">
                    <div class="metric-item">
                        <div class="metric-label">开仓次数</div>
                        <div class="metric-value">{stats['positions_opened']}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">胜率</div>
                        <div class="metric-value">{stats['win_rate']:.2f}%</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">总盈亏</div>
                        <div class="metric-value" style="color: {'#00ff88' if is_profitable else '#ff6b6b'};">
                            ${stats['total_pnl']:.2f}
                        </div>
                    </div>
                </div>
            </div>
"""

        html += """
        </div>

        <!-- 交易记录 -->
        <div class="section">
            <h2>📋 最近交易记录</h2>
            <table>
                <thead>
                    <tr>
                        <th>交易ID</th>
                        <th>市场</th>
                        <th>方向</th>
                        <th>操作</th>
                        <th>数量</th>
                        <th>价格</th>
                        <th>盈亏</th>
                        <th>策略</th>
                    </tr>
                </thead>
                <tbody>
"""

        # 显示最近20条交易
        recent_trades = self.portfolio.trades[-20:] if len(self.portfolio.trades) > 20 else self.portfolio.trades
        for trade in recent_trades:
            pnl_class = 'profit-text' if trade.pnl > 0 else ('loss-text' if trade.pnl < 0 else '')
            html += f"""
                    <tr>
                        <td>{trade.trade_id}</td>
                        <td>{trade.market_id[:15]}...</td>
                        <td>{trade.side}</td>
                        <td>{trade.action}</td>
                        <td>{trade.size:.2f}</td>
                        <td>${trade.price:.3f}</td>
                        <td class="{pnl_class}">${trade.pnl:.2f}</td>
                        <td>{trade.strategy.value}</td>
                    </tr>
"""

        html += f"""
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>Polymarket 量化交易机器人 v1.0 | 回测报告</p>
            <p>⚠️ 本报告仅供研究目的，不构成投资建议。过往表现不代表未来收益。</p>
        </div>
    </div>
</body>
</html>
"""
        return html

# ==================== 主程序 ====================

def main():
    """主函数"""
    print("\n" + "🚀" * 30)
    print("\n    Polymarket 量化交易机器人 - 回测系统\n")
    print("🚀" * 30 + "\n")

    # 创建回测引擎
    engine = BacktestEngine(
        initial_capital=10000,
        fee_rate=0.01  # 1% 交易费
    )

    # 添加策略
    engine.add_strategy(MarketMakingStrategy(spread_target=0.02, position_limit=500))
    engine.add_strategy(ArbitrageStrategy(min_profit_threshold=0.005))
    engine.add_strategy(MomentumStrategy(lookback=10, threshold=0.05))
    engine.add_strategy(MeanReversionStrategy(oversold_threshold=0.25, overbought_threshold=0.75))
    engine.add_strategy(SentimentStrategy(volume_threshold=2.0))
    engine.add_strategy(WhaleTrackingStrategy(large_order_threshold=10000))

    # 运行回测
    stats = engine.run(days=90, verbose=True)

    # 生成报告
    report_file = engine.generate_report("backtest_report.html")
    print(f"\n📄 回测报告已生成: {report_file}")
    print(f"📊 图表已保存: backtest_charts.png")

    # 保存统计数据
    with open("backtest_stats.json", "w", encoding="utf-8") as f:
        # 转换不可序列化的值
        serializable_stats = {}
        for k, v in stats.items():
            if isinstance(v, (int, float, str)):
                serializable_stats[k] = v
            else:
                serializable_stats[k] = str(v)
        json.dump(serializable_stats, f, indent=2, ensure_ascii=False)

    print(f"📈 统计数据已保存: backtest_stats.json")

    return engine, stats


if __name__ == "__main__":
    engine, stats = main()
