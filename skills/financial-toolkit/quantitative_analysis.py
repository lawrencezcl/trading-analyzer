#!/usr/bin/env python3
"""
量化金融分析工具集
Quantitative Financial Analysis Toolkit
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class QuantitativeAnalyzer:
    """量化分析器"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 无风险利率 2%
    
    def calculate_returns(self, prices: List[float]) -> List[float]:
        """计算收益率序列"""
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        return returns
    
    def calculate_volatility(self, returns: List[float], annualize=True) -> float:
        """计算波动率"""
        if not returns:
            return 0.0
        vol = np.std(returns)
        if annualize:
            vol *= np.sqrt(252)  # 年化
        return vol
    
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """计算夏普比率"""
        if not returns:
            return 0.0
        avg_return = np.mean(returns) * 252  # 年化收益
        vol = self.calculate_volatility(returns)
        if vol == 0:
            return 0.0
        return (avg_return - self.risk_free_rate) / vol
    
    def calculate_max_drawdown(self, prices: List[float]) -> Tuple[float, int, int]:
        """计算最大回撤"""
        if not prices:
            return 0.0, 0, 0
        
        peak = prices[0]
        peak_idx = 0
        max_dd = 0.0
        max_dd_start = 0
        max_dd_end = 0
        
        for i, price in enumerate(prices):
            if price > peak:
                peak = price
                peak_idx = i
            
            dd = (peak - price) / peak
            if dd > max_dd:
                max_dd = dd
                max_dd_start = peak_idx
                max_dd_end = i
        
        return max_dd, max_dd_start, max_dd_end
    
    def calculate_var(self, returns: List[float], confidence=0.95) -> float:
        """计算风险价值 VaR"""
        if not returns:
            return 0.0
        return np.percentile(returns, (1 - confidence) * 100)
    
    def calculate_beta(self, stock_returns: List[float], market_returns: List[float]) -> float:
        """计算 Beta 系数"""
        if len(stock_returns) != len(market_returns) or len(stock_returns) == 0:
            return 1.0
        
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        return covariance / market_variance
    
    def calculate_correlation(self, returns1: List[float], returns2: List[float]) -> float:
        """计算相关系数"""
        if len(returns1) != len(returns2) or len(returns1) == 0:
            return 0.0
        return np.corrcoef(returns1, returns2)[0][1]
    
    def position_sizing(self, account_value: float, risk_per_trade: float, 
                       entry: float, stop_loss: float) -> int:
        """计算头寸规模"""
        risk_amount = account_value * risk_per_trade
        price_risk = abs(entry - stop_loss)
        
        if price_risk == 0:
            return 0
        
        shares = int(risk_amount / price_risk)
        return shares
    
    def kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """凯利公式计算最优仓位"""
        if avg_loss == 0:
            return 0.0
        
        b = avg_win / avg_loss  # 盈亏比
        q = 1 - win_rate
        
        kelly = (win_rate * b - q) / b
        return max(0, min(kelly, 0.25))  # 限制最大25%
    
    def fibonacci_levels(self, high: float, low: float) -> Dict[str, float]:
        """计算斐波那契回撤位"""
        diff = high - low
        levels = {
            '0%': high,
            '23.6%': high - 0.236 * diff,
            '38.2%': high - 0.382 * diff,
            '50%': high - 0.5 * diff,
            '61.8%': high - 0.618 * diff,
            '78.6%': high - 0.786 * diff,
            '100%': low,
            '138.2%': high - 1.382 * diff,
            '161.8%': high - 1.618 * diff
        }
        return levels
    
    def pivot_points(self, high: float, low: float, close: float) -> Dict[str, float]:
        """计算枢轴点"""
        pivot = (high + low + close) / 3
        
        levels = {
            'R3': pivot + (high - low),
            'R2': pivot + (high - low) * 0.618,
            'R1': pivot + (high - low) * 0.382,
            'Pivot': pivot,
            'S1': pivot - (high - low) * 0.382,
            'S2': pivot - (high - low) * 0.618,
            'S3': pivot - (high - low)
        }
        return levels
    
    def atr(self, highs: List[float], lows: List[float], closes: List[float], period=14) -> float:
        """计算平均真实波幅 ATR"""
        if len(highs) < period + 1:
            return 0.0
        
        tr_values = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_values.append(max(tr1, tr2, tr3))
        
        return np.mean(tr_values[-period:])
    
    def bollinger_bands(self, prices: List[float], period=20, std_dev=2) -> Dict[str, List[float]]:
        """计算布林带"""
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}
        
        sma = []
        upper = []
        lower = []
        
        for i in range(period - 1, len(prices)):
            window = prices[i-period+1:i+1]
            middle = np.mean(window)
            std = np.std(window)
            
            sma.append(middle)
            upper.append(middle + std_dev * std)
            lower.append(middle - std_dev * std)
        
        return {'upper': upper, 'middle': sma, 'lower': lower}

if __name__ == "__main__":
    # 测试
    analyzer = QuantitativeAnalyzer()
    
    # 模拟价格数据
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
    
    print("=== 量化分析测试 ===\n")
    
    # 收益率
    returns = analyzer.calculate_returns(prices)
    print(f"收益率序列: {[f'{r:.2%}' for r in returns]}")
    
    # 波动率
    vol = analyzer.calculate_volatility(returns)
    print(f"年化波动率: {vol:.2%}")
    
    # 夏普比率
    sharpe = analyzer.calculate_sharpe_ratio(returns)
    print(f"夏普比率: {sharpe:.2f}")
    
    # 最大回撤
    max_dd, start, end = analyzer.calculate_max_drawdown(prices)
    print(f"最大回撤: {max_dd:.2%} (从第{start}天到第{end}天)")
    
    # VaR
    var = analyzer.calculate_var(returns)
    print(f"VaR (95%): {var:.2%}")
    
    # 斐波那契
    fib = analyzer.fibonacci_levels(max(prices), min(prices))
    print(f"\n斐波那契回撤位:")
    for level, price in fib.items():
        print(f"  {level}: ${price:.2f}")
    
    # 头寸规模
    shares = analyzer.position_sizing(100000, 0.02, 100, 95)
    print(f"\n建议头寸: {shares} 股 (账户$100k, 风险2%, 入场$100, 止损$95)")
