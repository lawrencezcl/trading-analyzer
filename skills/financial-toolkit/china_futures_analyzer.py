#!/usr/bin/env python3
"""
国内期货分析系统
China Futures Analysis System
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

class ChinaFuturesAnalyzer:
    """国内期货分析器"""
    
    def __init__(self):
        # 品种配置
        self.stock_index_futures = {
            'IF': {'name': '沪深300', 'exchange': 'CFFEX', 'multiplier': 300},
            'IC': {'name': '中证500', 'exchange': 'CFFEX', 'multiplier': 200},
            'IH': {'name': '上证50', 'exchange': 'CFFEX', 'multiplier': 300},
            'IM': {'name': '中证1000', 'exchange': 'CFFEX', 'multiplier': 200}
        }
        
        self.commodity_futures = {
            # 金属
            'RB': {'name': '螺纹钢', 'exchange': 'SHFE', 'category': '黑色'},
            'CU': {'name': '铜', 'exchange': 'SHFE', 'category': '有色'},
            'AL': {'name': '铝', 'exchange': 'SHFE', 'category': '有色'},
            'ZN': {'name': '锌', 'exchange': 'SHFE', 'category': '有色'},
            'NI': {'name': '镍', 'exchange': 'SHFE', 'category': '有色'},
            'AU': {'name': '黄金', 'exchange': 'SHFE', 'category': '贵金属'},
            'AG': {'name': '白银', 'exchange': 'SHFE', 'category': '贵金属'},
            # 能源化工
            'SC': {'name': '原油', 'exchange': 'INE', 'category': '能源'},
            'FU': {'name': '燃料油', 'exchange': 'SHFE', 'category': '能源'},
            'RU': {'name': '橡胶', 'exchange': 'SHFE', 'category': '化工'},
            'TA': {'name': 'PTA', 'exchange': 'CZCE', 'category': '化工'},
            'MA': {'name': '甲醇', 'exchange': 'CZCE', 'category': '化工'},
            'FG': {'name': '玻璃', 'exchange': 'CZCE', 'category': '建材'},
            'SA': {'name': '纯碱', 'exchange': 'CZCE', 'category': '建材'},
            # 农产品
            'M': {'name': '豆粕', 'exchange': 'DCE', 'category': '农产品'},
            'Y': {'name': '豆油', 'exchange': 'DCE', 'category': '农产品'},
            'P': {'name': '棕榈油', 'exchange': 'DCE', 'category': '农产品'},
            'SR': {'name': '白糖', 'exchange': 'CZCE', 'category': '农产品'},
            'CF': {'name': '棉花', 'exchange': 'CZCE', 'category': '农产品'}
        }
    
    def get_futures_data(self, symbol: str) -> Dict:
        """获取期货数据"""
        try:
            data = ak.futures_main_sina(symbol=f'{symbol}0')
            if data.empty:
                return {'error': 'No data'}
            
            latest = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else latest
            
            # 计算技术指标
            closes = data['收盘价'].tail(20).values
            sma5 = np.mean(closes[-5:]) if len(closes) >= 5 else closes[-1]
            sma10 = np.mean(closes[-10:]) if len(closes) >= 10 else closes[-1]
            sma20 = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]
            
            # 计算波动率
            returns = np.diff(closes) / closes[:-1]
            volatility = np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
            
            return {
                'symbol': symbol,
                'date': latest['日期'],
                'open': latest['开盘价'],
                'high': latest['最高价'],
                'low': latest['最低价'],
                'close': latest['收盘价'],
                'volume': latest['成交量'],
                'oi': latest['持仓量'],
                'change': latest['收盘价'] - prev['收盘价'],
                'change_pct': ((latest['收盘价'] - prev['收盘价']) / prev['收盘价']) * 100,
                'sma5': sma5,
                'sma10': sma10,
                'sma20': sma20,
                'volatility': volatility,
                'trend': 'up' if latest['收盘价'] > sma20 else 'down' if latest['收盘价'] < sma20 else 'neutral'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_stock_index_futures(self) -> Dict:
        """分析股指期货"""
        results = {}
        for symbol in self.stock_index_futures:
            data = self.get_futures_data(symbol)
            if 'error' not in data:
                data.update(self.stock_index_futures[symbol])
                results[symbol] = data
        return results
    
    def analyze_commodity_futures(self) -> Dict:
        """分析商品期货"""
        results = {}
        for symbol in self.commodity_futures:
            data = self.get_futures_data(symbol)
            if 'error' not in data:
                data.update(self.commodity_futures[symbol])
                results[symbol] = data
        return results
    
    def generate_trading_plan(self, data: Dict) -> Dict:
        """生成交易计划"""
        close = data['close']
        sma5 = data['sma5']
        sma10 = data['sma10']
        sma20 = data['sma20']
        trend = data['trend']
        
        # 确定方向
        if trend == 'up' and close > sma5 > sma10:
            direction = 'long'
            entry = close
            stop = min(data['low'], sma10 * 0.995)
            target = close + (close - stop) * 2
        elif trend == 'down' and close < sma5 < sma10:
            direction = 'short'
            entry = close
            stop = max(data['high'], sma10 * 1.005)
            target = close - (stop - close) * 2
        else:
            direction = 'neutral'
            entry = None
            stop = None
            target = None
        
        return {
            'direction': direction,
            'entry': entry,
            'stop_loss': stop,
            'target': target,
            'risk_reward': abs(target - entry) / abs(entry - stop) if entry and stop and target else 0
        }
    
    def generate_report(self) -> str:
        """生成分析报告"""
        stock_index = self.analyze_stock_index_futures()
        commodities = self.analyze_commodity_futures()
        
        report = f"""═══════════════════════════════════════════════════
📊 国内期货市场分析报告
═══════════════════════════════════════════════════
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析师: JARVIS QFA/FOE

═══════════════════════════════════════════════════
一、股指期货分析
═══════════════════════════════════════════════════
"""
        
        for symbol, data in stock_index.items():
            plan = self.generate_trading_plan(data)
            emoji = "🟢" if data['change_pct'] > 0 else "🔴"
            
            report += f"""
┌─ {data['name']} ({symbol})
│
│  {emoji} 价格: {data['close']:.2f} ({data['change_pct']:+.2f}%)
│     涨跌: {data['change']:+.2f}
│     最高: {data['high']:.2f} | 最低: {data['low']:.2f}
│     成交量: {data['volume']:,} | 持仓量: {data['oi']:,}
│
│  📈 技术指标:
│     趋势: {data['trend'].upper()}
│     SMA5: {data['sma5']:.2f}
│     SMA10: {data['sma10']:.2f}
│     SMA20: {data['sma20']:.2f}
│     波动率: {data['volatility']*100:.2f}%
│
│  📋 交易计划: {plan['direction'].upper()}
"""
            if plan['entry']:
                report += f"""│     入场: {plan['entry']:.2f}
│     停损: {plan['stop_loss']:.2f}
│     目标: {plan['target']:.2f}
│     盈亏比: {plan['risk_reward']:.2f}
"""
            report += "│\n└────────────────────\n"
        
        # 商品期货按分类
        categories = {}
        for symbol, data in commodities.items():
            cat = data.get('category', '其他')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((symbol, data))
        
        report += """
═══════════════════════════════════════════════════
二、商品期货分析
═══════════════════════════════════════════════════
"""
        
        for cat, items in categories.items():
            report += f"\n【{cat}】\n"
            for symbol, data in items[:5]:  # 每类显示前5个
                emoji = "🟢" if data['change_pct'] > 0 else "🔴"
                report += f"  {emoji} {data['name']}({symbol}): {data['close']:.2f} ({data['change_pct']:+.2f}%)\n"
        
        report += """
═══════════════════════════════════════════════════
三、市场总结
═══════════════════════════════════════════════════

【股指期货】
• 关注大盘趋势和资金流向
• 注意基差变化
• 严格风险管理

【商品期货】
• 关注产业链上下游联动
• 注意库存和供需数据
• 关注宏观政策影响

⚠️ 风险提示:
• 期货交易杠杆高，风险大
• 建议单笔风险不超过本金2%
• 严格执行止损

═══════════════════════════════════════════════════
"""
        
        return report

if __name__ == "__main__":
    analyzer = ChinaFuturesAnalyzer()
    report = analyzer.generate_report()
    print(report)
