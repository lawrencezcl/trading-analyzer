#!/usr/bin/env python3
"""
国内期货详细分析系统
China Futures Detailed Analysis System
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime

class DetailedFuturesAnalyzer:
    def __init__(self):
        self.futures_list = {
            # 股指期货
            'IF': {'name': '沪深300', 'exchange': 'CFFEX', 'category': '股指期货', 'unit': '点'},
            'IC': {'name': '中证500', 'exchange': 'CFFEX', 'category': '股指期货', 'unit': '点'},
            'IH': {'name': '上证50', 'exchange': 'CFFEX', 'category': '股指期货', 'unit': '点'},
            'IM': {'name': '中证1000', 'exchange': 'CFFEX', 'category': '股指期货', 'unit': '点'},
            # 贵金属
            'AU': {'name': '黄金', 'exchange': 'SHFE', 'category': '贵金属', 'unit': '元/克'},
            'AG': {'name': '白银', 'exchange': 'SHFE', 'category': '贵金属', 'unit': '元/千克'},
            # 有色
            'CU': {'name': '铜', 'exchange': 'SHFE', 'category': '有色金属', 'unit': '元/吨'},
            'AL': {'name': '铝', 'exchange': 'SHFE', 'category': '有色金属', 'unit': '元/吨'},
            'ZN': {'name': '锌', 'exchange': 'SHFE', 'category': '有色金属', 'unit': '元/吨'},
            'NI': {'name': '镍', 'exchange': 'SHFE', 'category': '有色金属', 'unit': '元/吨'},
            # 黑色
            'RB': {'name': '螺纹钢', 'exchange': 'SHFE', 'category': '黑色系', 'unit': '元/吨'},
            'I': {'name': '铁矿石', 'exchange': 'DCE', 'category': '黑色系', 'unit': '元/吨'},
            'J': {'name': '焦炭', 'exchange': 'DCE', 'category': '黑色系', 'unit': '元/吨'},
            'JM': {'name': '焦煤', 'exchange': 'DCE', 'category': '黑色系', 'unit': '元/吨'},
            # 能源化工
            'SC': {'name': '原油', 'exchange': 'INE', 'category': '能源化工', 'unit': '元/桶'},
            'FU': {'name': '燃料油', 'exchange': 'SHFE', 'category': '能源化工', 'unit': '元/吨'},
            'RU': {'name': '橡胶', 'exchange': 'SHFE', 'category': '能源化工', 'unit': '元/吨'},
            'TA': {'name': 'PTA', 'exchange': 'CZCE', 'category': '能源化工', 'unit': '元/吨'},
            'MA': {'name': '甲醇', 'exchange': 'CZCE', 'category': '能源化工', 'unit': '元/吨'},
            # 建材
            'FG': {'name': '玻璃', 'exchange': 'CZCE', 'category': '建材', 'unit': '元/吨'},
            'SA': {'name': '纯碱', 'exchange': 'CZCE', 'category': '建材', 'unit': '元/吨'},
            # 农产品
            'M': {'name': '豆粕', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨'},
            'Y': {'name': '豆油', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨'},
            'P': {'name': '棕榈油', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨'},
            'SR': {'name': '白糖', 'exchange': 'CZCE', 'category': '农产品', 'unit': '元/吨'},
            'CF': {'name': '棉花', 'exchange': 'CZCE', 'category': '农产品', 'unit': '元/吨'},
        }
    
    def get_data(self, symbol):
        try:
            data = ak.futures_main_sina(symbol=f'{symbol}0')
            if data.empty or len(data) < 20:
                return None
            return data
        except:
            return None
    
    def analyze(self, symbol, info, data):
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        closes = data['收盘价'].values
        highs = data['最高价'].values
        lows = data['最低价'].values
        volumes = data['成交量'].values
        
        # 基础数据
        close = latest['收盘价']
        high = latest['最高价']
        low = latest['最低价']
        volume = latest['成交量']
        oi = latest['持仓量']
        
        change = close - prev['收盘价']
        change_pct = (change / prev['收盘价']) * 100
        
        # 技术指标
        sma5 = np.mean(closes[-5:])
        sma10 = np.mean(closes[-10:])
        sma20 = np.mean(closes[-20:])
        
        # 波动率
        if len(closes) >= 21:
            returns = []
            for i in range(len(closes)-20, len(closes)):
                ret = (closes[i] - closes[i-1]) / closes[i-1]
                returns.append(ret)
            volatility = np.std(returns) * np.sqrt(252) * 100 if returns else 0
        else:
            volatility = 0
        
        # 趋势判断
        if close > sma20 and sma5 > sma10:
            trend = 'UP'
            trend_desc = '上升趋势'
        elif close < sma20 and sma5 < sma10:
            trend = 'DOWN'
            trend_desc = '下降趋势'
        else:
            trend = 'NEUTRAL'
            trend_desc = '震荡整理'
        
        # 支撑压力
        resistance = max(highs[-10:])
        support = min(lows[-10:])
        
        # 持仓量变化
        oi_change = oi - prev['持仓量']
        oi_change_pct = (oi_change / prev['持仓量']) * 100 if prev['持仓量'] > 0 else 0
        
        # 成交量分析
        avg_volume = np.mean(volumes[-5:])
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1
        
        # 交易计划
        if trend == 'UP':
            direction = 'LONG'
            entry = close
            stop = max(support, sma10 * 0.99)
            target1 = close + (close - stop) * 1.5
            target2 = close + (close - stop) * 2.5
        elif trend == 'DOWN':
            direction = 'SHORT'
            entry = close
            stop = min(resistance, sma10 * 1.01)
            target1 = close - (stop - close) * 1.5
            target2 = close - (stop - close) * 2.5
        else:
            direction = 'NEUTRAL'
            entry = None
            stop = None
            target1 = None
            target2 = None
        
        return {
            'symbol': symbol,
            'name': info['name'],
            'category': info['category'],
            'exchange': info['exchange'],
            'unit': info['unit'],
            'close': close,
            'change_pct': change_pct,
            'volume': volume,
            'oi': oi,
            'oi_change_pct': oi_change_pct,
            'sma5': sma5,
            'sma10': sma10,
            'sma20': sma20,
            'volatility': volatility,
            'trend': trend,
            'trend_desc': trend_desc,
            'resistance': resistance,
            'support': support,
            'volume_ratio': volume_ratio,
            'direction': direction,
            'entry': entry,
            'stop': stop,
            'target1': target1,
            'target2': target2
        }
    
    def generate_full_report(self):
        report = f"""══════════════════════════════════════════════════════════════════
                    国内期货品种详细分析报告
══════════════════════════════════════════════════════════════════
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
分析师: JARVIS QFA/FOE

"""
        
        categories = {}
        for symbol, info in self.futures_list.items():
            data = self.get_data(symbol)
            if data is not None:
                analysis = self.analyze(symbol, info, data)
                cat = info['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(analysis)
        
        for cat, items in categories.items():
            report += f"""
══════════════════════════════════════════════════════════════════
                        {cat}
══════════════════════════════════════════════════════════════════
"""
            for item in items:
                emoji = "🟢" if item['change_pct'] > 0 else "🔴" if item['change_pct'] < 0 else "⚪"
                direction_emoji = "📈" if item['direction'] == 'LONG' else "📉" if item['direction'] == 'SHORT' else "➖"
                
                report += f"""
【{item['name']} ({item['symbol']})】{emoji}
交易所: {item['exchange']} | 单位: {item['unit']}

基础数据:
  最新价: {item['close']:.2f}
  涨跌: {item['change_pct']:+.2f}%
  成交量: {item['volume']:,}
  持仓量: {item['oi']:,} ({item['oi_change_pct']:+.2f}%)

技术指标:
  趋势: {item['trend_desc']} ({item['trend']})
  SMA5: {item['sma5']:.2f} | SMA10: {item['sma10']:.2f} | SMA20: {item['sma20']:.2f}
  波动率: {item['volatility']:.2f}%
  支撑: {item['support']:.2f} | 压力: {item['resistance']:.2f}

交易计划 {direction_emoji}:
  方向: {item['direction']}
"""
                if item['entry']:
                    rr = abs(item['target1'] - item['entry']) / abs(item['entry'] - item['stop']) if item['stop'] else 0
                    report += f"""  入场: {item['entry']:.2f}
  停损: {item['stop']:.2f}
  目标1: {item['target1']:.2f}
  目标2: {item['target2']:.2f}
  盈亏比: {rr:.2f}
"""
                else:
                    report += "  建议观望\n"
                
                report += "\n"
        
        return report

if __name__ == "__main__":
    analyzer = DetailedFuturesAnalyzer()
    report = analyzer.generate_full_report()
    print(report)
    
    # 保存到文件
    with open('/root/.openclaw/workspace/国内期货详细分析报告.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print('\n✅ 报告已保存至: /root/.openclaw/workspace/国内期货详细分析报告.md')
