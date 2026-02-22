#!/usr/bin/env python3
"""
国内期货15分钟自动分析系统
China Futures 15-Minute Auto Analysis System
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import subprocess

class ChinaFuturesAutoAnalyzer:
    """国内期货自动分析器"""
    
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
            'EG': {'name': '乙二醇', 'exchange': 'DCE', 'category': '能源化工', 'unit': '元/吨'},
            # 建材
            'FG': {'name': '玻璃', 'exchange': 'CZCE', 'category': '建材', 'unit': '元/吨'},
            'SA': {'name': '纯碱', 'exchange': 'CZCE', 'category': '建材', 'unit': '元/吨'},
            # 农产品
            'M': {'name': '豆粕', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨'},
            'Y': {'name': '豆油', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨'},
            'P': {'name': '棕榈油', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨'},
            'SR': {'name': '白糖', 'exchange': 'CZCE', 'category': '农产品', 'unit': '元/吨'},
            'CF': {'name': '棉花', 'exchange': 'CZCE', 'category': '农产品', 'unit': '元/吨'},
            'OI': {'name': '菜籽油', 'exchange': 'CZCE', 'category': '农产品', 'unit': '元/吨'},
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
        
        close = latest['收盘价']
        change_pct = ((close - prev['收盘价']) / prev['收盘价']) * 100
        
        sma5 = np.mean(closes[-5:])
        sma10 = np.mean(closes[-10:])
        sma20 = np.mean(closes[-20:])
        
        if len(closes) >= 21:
            returns = []
            for i in range(len(closes)-20, len(closes)):
                ret = (closes[i] - closes[i-1]) / closes[i-1]
                returns.append(ret)
            volatility = np.std(returns) * np.sqrt(252) * 100 if returns else 0
        else:
            volatility = 0
        
        if close > sma20 and sma5 > sma10:
            trend = 'UP'
        elif close < sma20 and sma5 < sma10:
            trend = 'DOWN'
        else:
            trend = 'NEUTRAL'
        
        resistance = max(highs[-10:])
        support = min(lows[-10:])
        
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
            entry = stop = target1 = target2 = None
        
        return {
            'symbol': symbol, 'name': info['name'], 'category': info['category'],
            'exchange': info['exchange'], 'unit': info['unit'], 'close': close,
            'change_pct': change_pct, 'volume': latest['成交量'], 'oi': latest['持仓量'],
            'sma5': sma5, 'sma10': sma10, 'sma20': sma20, 'volatility': volatility,
            'trend': trend, 'resistance': resistance, 'support': support,
            'direction': direction, 'entry': entry, 'stop': stop,
            'target1': target1, 'target2': target2
        }
    
    def generate_report(self):
        timestamp = datetime.now()
        filename = f"qihuo{timestamp.strftime('%Y%m%d%H%M%S')}.md"
        
        report = f"""# 国内期货15分钟分析报告

**生成时间:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**分析师:** JARVIS QFA/FOE  
**数据周期:** 15分钟  
**覆盖品种:** {len(self.futures_list)}个

---

## 市场概览

| 时间 | {timestamp.strftime('%H:%M')} |
|------|-------------------------------|
| 交易日 | {timestamp.strftime('%Y-%m-%d')} |
| 分析状态 | ✅ 自动运行 |

---

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
            report += f"## {cat}\n\n"
            for item in items:
                emoji = "🟢" if item['change_pct'] > 0 else "🔴" if item['change_pct'] < 0 else "⚪"
                report += f"""### {emoji} {item['name']} ({item['symbol']})

**基础数据:**
- 最新价: {item['close']:.2f} {item['unit']}
- 涨跌: {item['change_pct']:+.2f}%
- 成交量: {item['volume']:,}
- 持仓量: {item['oi']:,}

**技术指标:**
- 趋势: {item['trend']}
- SMA5: {item['sma5']:.2f} | SMA10: {item['sma10']:.2f} | SMA20: {item['sma20']:.2f}
- 波动率: {item['volatility']:.2f}%
- 支撑: {item['support']:.2f} | 压力: {item['resistance']:.2f}

**交易计划:**
- 方向: **{item['direction']}**
"""
                if item['entry']:
                    rr = abs(item['target1'] - item['entry']) / abs(item['entry'] - item['stop']) if item['stop'] else 0
                    report += f"""- 入场: {item['entry']:.2f}
- 停损: {item['stop']:.2f}
- 目标1: {item['target1']:.2f}
- 目标2: {item['target2']:.2f}
- 盈亏比: {rr:.2f}
"""
                else:
                    report += "- 建议观望\n"
                report += "\n---\n\n"
        
        report += """## 免责声明

⚠️ **风险提示:**
- 本报告仅供参考，不构成投资建议
- 期货交易风险极高，可能导致本金全部损失
- 投资者应根据自身情况独立判断
- 过往业绩不代表未来表现

---

*报告由 JARVIS QFA/FOE 自动生成*
"""
        
        return filename, report
    
    def save_and_push(self):
        """保存报告并推送到GitHub"""
        filename, report = self.generate_report()
        
        # 保存到本地
        filepath = f'/root/.openclaw/workspace/{filename}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 报告已生成: {filepath}")
        
        # Git 操作
        try:
            os.chdir('/root/.openclaw/workspace')
            
            # 添加文件
            subprocess.run(['git', 'add', filename], check=True, capture_output=True)
            
            # 提交
            commit_msg = f"Auto: {filename} - China Futures 15min Analysis"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True)
            
            # 推送
            result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 已推送到 GitHub: {filename}")
                return True
            else:
                print(f"⚠️ 推送失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Git 操作失败: {e}")
            return False

if __name__ == "__main__":
    analyzer = ChinaFuturesAutoAnalyzer()
    analyzer.save_and_push()
