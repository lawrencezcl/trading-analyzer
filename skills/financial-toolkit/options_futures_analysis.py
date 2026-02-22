#!/usr/bin/env python3
"""
期权链分析工具
Options Chain Analysis Toolkit
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class OptionsChainAnalyzer:
    """期权链分析器"""
    
    def __init__(self):
        self.risk_free_rate = 0.05
    
    def calculate_max_pain(self, strikes: List[float], 
                          call_oi: List[float], 
                          put_oi: List[float]) -> float:
        """
        计算最大痛点 (Max Pain)
        期权买方损失最大、卖方获利最大的价格点
        """
        min_pain = float('inf')
        max_pain_price = 0
        
        for strike in strikes:
            total_pain = 0
            
            # 计算 Call 的痛苦值
            for i, s in enumerate(strikes):
                if s < strike:
                    total_pain += call_oi[i] * (strike - s)
            
            # 计算 Put 的痛苦值
            for i, s in enumerate(strikes):
                if s > strike:
                    total_pain += put_oi[i] * (s - strike)
            
            if total_pain < min_pain:
                min_pain = total_pain
                max_pain_price = strike
        
        return max_pain_price
    
    def calculate_put_call_ratio(self, put_volume: float, call_volume: float) -> float:
        """
        计算 Put/Call Ratio
        > 1: 看跌情绪浓厚
        < 0.7: 看涨情绪浓厚
        """
        if call_volume == 0:
            return float('inf')
        return put_volume / call_volume
    
    def calculate_iv_skew(self, strikes: List[float], 
                         iv_values: List[float],
                         current_price: float) -> Dict:
        """
        计算波动率偏度 (IV Skew)
        """
        # 分离虚值 Put 和虚值 Call 的 IV
        otm_puts_iv = []
        otm_calls_iv = []
        
        for strike, iv in zip(strikes, iv_values):
            if strike < current_price:
                otm_puts_iv.append(iv)
            else:
                otm_calls_iv.append(iv)
        
        return {
            'otm_put_iv_avg': np.mean(otm_puts_iv) if otm_puts_iv else 0,
            'otm_call_iv_avg': np.mean(otm_calls_iv) if otm_calls_iv else 0,
            'skew': np.mean(otm_puts_iv) - np.mean(otm_calls_iv) if otm_puts_iv and otm_calls_iv else 0
        }
    
    def calculate_greeks(self, S: float, K: float, T: float, 
                        r: float, sigma: float, option_type: str = 'call') -> Dict:
        """
        计算期权希腊字母 (使用 Black-Scholes 模型)
        
        S: 标的资产价格
        K: 行权价
        T: 到期时间 (年)
        r: 无风险利率
        sigma: 波动率
        """
        from scipy.stats import norm
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            delta = norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                    - r * K * np.exp(-r * T) * norm.cdf(d2))
        else:
            delta = -norm.cdf(-d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                    + r * K * np.exp(-r * T) * norm.cdf(-d2))
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # 除以100表示1%波动率变化
        rho = K * T * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2) / 100
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }
    
    def analyze_options_flow(self, trades: List[Dict]) -> Dict:
        """
        分析期权流向
        """
        call_premium = 0
        put_premium = 0
        call_volume = 0
        put_volume = 0
        
        for trade in trades:
            premium = trade.get('price', 0) * trade.get('volume', 0) * 100
            if trade.get('type') == 'call':
                call_premium += premium
                call_volume += trade.get('volume', 0)
            else:
                put_premium += premium
                put_volume += trade.get('volume', 0)
        
        return {
            'call_premium': call_premium,
            'put_premium': put_premium,
            'total_premium': call_premium + put_premium,
            'pc_ratio_volume': put_volume / call_volume if call_volume > 0 else 0,
            'pc_ratio_premium': put_premium / call_premium if call_premium > 0 else 0
        }
    
    def find_unusual_activity(self, strikes: List[float],
                             oi_current: List[float],
                             oi_previous: List[float],
                             volume: List[float],
                             threshold: float = 2.0) -> List[Dict]:
        """
        识别异常期权活动
        """
        unusual = []
        
        for i, strike in enumerate(strikes):
            oi_change = oi_current[i] - oi_previous[i] if oi_previous[i] > 0 else 0
            volume_oi_ratio = volume[i] / oi_current[i] if oi_current[i] > 0 else 0
            
            # 成交量是持仓量的2倍以上，或持仓量大幅增加
            if volume_oi_ratio > threshold or oi_change > 1000:
                unusual.append({
                    'strike': strike,
                    'volume': volume[i],
                    'oi_current': oi_current[i],
                    'oi_change': oi_change,
                    'volume_oi_ratio': volume_oi_ratio
                })
        
        return sorted(unusual, key=lambda x: x['volume_oi_ratio'], reverse=True)


class FuturesAnalyzer:
    """期货分析器"""
    
    def analyze_term_structure(self, expirations: List[str], 
                              prices: List[float]) -> Dict:
        """
        分析期货期限结构
        """
        if len(prices) < 2:
            return {'structure': 'unknown'}
        
        # 判断 Contango 还是 Backwardation
        spreads = []
        for i in range(len(prices) - 1):
            spread = prices[i+1] - prices[i]
            spreads.append(spread)
        
        avg_spread = np.mean(spreads)
        
        if avg_spread > 0:
            structure = 'contango'
        elif avg_spread < 0:
            structure = 'backwardation'
        else:
            structure = 'flat'
        
        return {
            'structure': structure,
            'spreads': spreads,
            'avg_spread': avg_spread
        }
    
    def calculate_roll_cost(self, front_price: float, 
                           back_price: float,
                           days_to_roll: int) -> Dict:
        """
        计算展期成本
        """
        absolute_cost = back_price - front_price
        percentage_cost = (absolute_cost / front_price) * 100
        annualized_cost = percentage_cost * (365 / days_to_roll)
        
        return {
            'absolute_cost': absolute_cost,
            'percentage_cost': percentage_cost,
            'annualized_cost': annualized_cost
        }
    
    def calculate_basis(self, futures_price: float, 
                       spot_price: float) -> Dict:
        """
        计算基差
        """
        basis = futures_price - spot_price
        basis_percent = (basis / spot_price) * 100
        
        return {
            'basis': basis,
            'basis_percent': basis_percent,
            'annualized_basis': basis_percent * 12  # 简化为年化
        }


if __name__ == "__main__":
    # 测试
    options_analyzer = OptionsChainAnalyzer()
    futures_analyzer = FuturesAnalyzer()
    
    print("=== 期权链分析测试 ===\n")
    
    # 模拟期权链数据
    strikes = [100, 105, 110, 115, 120]
    call_oi = [1000, 2000, 3500, 2800, 1500]
    put_oi = [800, 1500, 3000, 3200, 2000]
    
    # 计算 Max Pain
    max_pain = options_analyzer.calculate_max_pain(strikes, call_oi, put_oi)
    print(f"最大痛点 (Max Pain): ${max_pain}")
    
    # 计算 Put/Call Ratio
    pc_ratio = options_analyzer.calculate_put_call_ratio(sum(put_oi), sum(call_oi))
    print(f"Put/Call Ratio (OI): {pc_ratio:.2f}")
    
    # 测试 Greeks
    greeks = options_analyzer.calculate_greeks(S=110, K=110, T=0.25, r=0.05, sigma=0.2)
    print(f"\n希腊字母 (ATM Call):")
    for greek, value in greeks.items():
        print(f"  {greek.upper()}: {value:.4f}")
    
    print("\n=== 期货分析测试 ===\n")
    
    # 模拟期货期限结构
    expirations = ['2025-03', '2025-06', '2025-09', '2025-12']
    prices = [100, 102, 104, 106]  # Contango
    
    term_structure = futures_analyzer.analyze_term_structure(expirations, prices)
    print(f"期限结构: {term_structure['structure'].upper()}")
    print(f"平均价差: ${term_structure['avg_spread']:.2f}")
