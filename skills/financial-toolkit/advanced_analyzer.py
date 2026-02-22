#!/usr/bin/env python3
"""
高级市场分析系统
Advanced Market Analysis System
整合威科夫、蔡森、量化分析
"""

import sys
import json
from datetime import datetime
from typing import Dict, List

# 导入各个模块
from data_api import FinancialDataAPI
from goldapi import GoldAPI
from yahoo_finance_api import YahooFinanceAPI
from quantitative_analysis import QuantitativeAnalyzer

class AdvancedMarketAnalyzer:
    """高级市场分析器"""
    
    def __init__(self):
        self.finnhub = FinancialDataAPI()
        self.goldapi = GoldAPI()
        self.yahoo = YahooFinanceAPI()
        self.quant = QuantitativeAnalyzer()
        
        # 市场数据缓存
        self.market_data = {}
    
    def fetch_all_market_data(self) -> Dict:
        """获取所有市场数据"""
        data = {}
        
        # 美股指数 - Finnhub
        for symbol in ['SPY', 'QQQ']:
            try:
                quote = self.finnhub.finnhub.get_quote(symbol)
                data[symbol] = {
                    'price': quote.get('c'),
                    'change_pct': quote.get('dp'),
                    'source': 'Finnhub'
                }
            except:
                pass
        
        # 全球指数 - Yahoo
        for code, info in self.yahoo.INDICES.items():
            try:
                result = self.yahoo.get_index_quote(code)
                if 'error' not in result:
                    data[code] = {
                        'price': result.get('price'),
                        'change_pct': result.get('change_pct'),
                        'source': 'Yahoo'
                    }
            except:
                pass
        
        # 贵金属 - GoldAPI
        for code in ['XAU', 'XAG']:
            try:
                result = self.goldapi.get_price(code)
                if 'error' not in result:
                    data[code] = {
                        'price': result.get('price'),
                        'change_pct': result.get('change_pct'),
                        'source': 'GoldAPI'
                    }
            except:
                pass
        
        self.market_data = data
        return data
    
    def comprehensive_analysis(self, symbol: str, prices: List[float]) -> Dict:
        """综合分析"""
        if len(prices) < 10:
            return {'error': 'Insufficient data'}
        
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'price_action': {},
            'technical': {},
            'quantitative': {},
            'trading_plan': {}
        }
        
        # 价格行为分析
        current = prices[-1]
        high = max(prices)
        low = min(prices)
        
        analysis['price_action'] = {
            'current': current,
            'high': high,
            'low': low,
            'range': high - low,
            'position_in_range': (current - low) / (high - low) if high != low else 0.5
        }
        
        # 量化指标
        returns = self.quant.calculate_returns(prices)
        if returns:
            analysis['quantitative'] = {
                'volatility': self.quant.calculate_volatility(returns),
                'sharpe_ratio': self.quant.calculate_sharpe_ratio(returns),
                'max_drawdown': self.quant.calculate_max_drawdown(prices)[0],
                'var_95': self.quant.calculate_var(returns)
            }
        
        # 技术位
        analysis['technical'] = {
            'fibonacci': self.quant.fibonacci_levels(high, low),
            'pivot': self.quant.pivot_points(high, low, prices[-2] if len(prices) > 1 else current)
        }
        
        # 交易计划
        position = analysis['price_action']['position_in_range']
        
        if position > 0.7:
            direction = 'short'
            entry = current
            stop = high
            target = analysis['technical']['fibonacci']['50%']
        elif position < 0.3:
            direction = 'long'
            entry = current
            stop = low
            target = analysis['technical']['fibonacci']['50%']
        else:
            direction = 'neutral'
            entry = None
            stop = None
            target = None
        
        analysis['trading_plan'] = {
            'direction': direction,
            'entry': entry,
            'stop_loss': stop,
            'target': target,
            'risk_reward': abs(target - entry) / abs(entry - stop) if entry and stop and target else 0
        }
        
        return analysis
    
    def generate_professional_report(self) -> str:
        """生成专业分析报告"""
        data = self.fetch_all_market_data()
        
        report = f"""═══════════════════════════════════════════════════
📊 量化金融市场分析报告
═══════════════════════════════════════════════════
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析师: JARVIS QFA (Quantitative Financial Analyst)

═══════════════════════════════════════════════════
一、市场概览
═══════════════════════════════════════════════════
"""
        
        # 分类显示
        indices = {k: v for k, v in data.items() if k in ['SPY', 'QQQ', 'SPX', 'NQ', 'DAX', 'JP225']}
        commodities = {k: v for k, v in data.items() if k in ['XAU', 'XAG']}
        
        if indices:
            report += "\n📈 股票指数:\n"
            for code, info in indices.items():
                change = info.get('change_pct', 0)
                emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                report += f"  {emoji} {code}: ${info.get('price', 0):.2f} ({change:+.2f}%) [{info.get('source', '')}]\n"
        
        if commodities:
            report += "\n🥇 贵金属:\n"
            for code, info in commodities.items():
                change = info.get('change_pct', 0)
                emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                report += f"  {emoji} {code}: ${info.get('price', 0):.2f} ({change:+.2f}%) [{info.get('source', '')}]\n"
        
        report += """
═══════════════════════════════════════════════════
二、技术分析框架
═══════════════════════════════════════════════════

【威科夫分析】
• 当前市场结构评估
• 供需关系分析
• 关键价位识别

【蔡森技术分析】
• 型态识别 (W底/M头/头肩等)
• 量价关系
• 支撑压力位

【量化指标】
• 波动率分析
• 风险调整收益
• 相关性矩阵

═══════════════════════════════════════════════════
三、交易建议
═══════════════════════════════════════════════════

⚠️ 风险提示:
• 所有分析仅供参考，不构成投资建议
• 市场有风险，投资需谨慎
• 建议严格执行风险管理

💡 专业建议:
• 单笔交易风险不超过账户2%
• 使用止损保护本金
• 分散投资降低风险

═══════════════════════════════════════════════════
"""
        
        return report

if __name__ == "__main__":
    analyzer = AdvancedMarketAnalyzer()
    
    print("正在获取市场数据...")
    data = analyzer.fetch_all_market_data()
    
    print("\n=== 市场数据 ===")
    for code, info in data.items():
        print(f"{code}: ${info.get('price', 0):.2f} ({info.get('change_pct', 0):+.2f}%)")
    
    # 生成完整报告
    report = analyzer.generate_professional_report()
    print(report)
