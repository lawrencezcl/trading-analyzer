#!/usr/bin/env python3
"""
国内期货15分钟自动分析系统 - 高胜率策略版
China Futures 15-Minute Auto Analysis with High Win Rate Strategies

基于6个月回测结果优化:
- 白银(AG): Volatility_Breakout / SMA_Crossover (胜率50-66%)
- 股指(IF/IM): Mean_Reversion (胜率62-77%)
- 原油(SC): Mean_Reversion (胜率50%)
- 其他品种: 自适应策略选择
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import subprocess

class ChinaFuturesAutoAnalyzerV2:
    """国内期货自动分析器 V2 - 高胜率策略"""
    
    def __init__(self):
        # 品种配置 + 推荐策略 (基于回测结果)
        self.futures_list = {
            # 股指期货 - 推荐 Mean_Reversion (高胜率)
            'IF': {'name': '沪深300', 'exchange': 'CFFEX', 'category': '股指期货', 'unit': '点', 'strategy': 'Mean_Reversion', 'win_rate': 0.778},
            'IC': {'name': '中证500', 'exchange': 'CFFEX', 'category': '股指期货', 'unit': '点', 'strategy': 'SMA_Crossover', 'win_rate': 0.167},
            'IH': {'name': '上证50', 'exchange': 'CFFEX', 'category': '股指期货', 'unit': '点', 'strategy': 'SMA_Crossover', 'win_rate': 0.500},
            'IM': {'name': '中证1000', 'exchange': 'CFFEX', 'category': '股指期货', 'unit': '点', 'strategy': 'Mean_Reversion', 'win_rate': 0.625},
            
            # 贵金属 - AG推荐 Volatility_Breakout (最高胜率)
            'AU': {'name': '黄金', 'exchange': 'SHFE', 'category': '贵金属', 'unit': '元/克', 'strategy': 'SMA_Crossover', 'win_rate': 0.333},
            'AG': {'name': '白银', 'exchange': 'SHFE', 'category': '贵金属', 'unit': '元/千克', 'strategy': 'Volatility_Breakout', 'win_rate': 0.667},
            
            # 有色金属
            'CU': {'name': '铜', 'exchange': 'SHFE', 'category': '有色金属', 'unit': '元/吨', 'strategy': 'Breakout', 'win_rate': 1.000},
            'AL': {'name': '铝', 'exchange': 'SHFE', 'category': '有色金属', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'ZN': {'name': '锌', 'exchange': 'SHFE', 'category': '有色金属', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'NI': {'name': '镍', 'exchange': 'SHFE', 'category': '有色金属', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            
            # 黑色系 - RB各策略表现均不佳, 建议观望
            'RB': {'name': '螺纹钢', 'exchange': 'SHFE', 'category': '黑色系', 'unit': '元/吨', 'strategy': 'Mean_Reversion', 'win_rate': 0.375},
            'I': {'name': '铁矿石', 'exchange': 'DCE', 'category': '黑色系', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'J': {'name': '焦炭', 'exchange': 'DCE', 'category': '黑色系', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'JM': {'name': '焦煤', 'exchange': 'DCE', 'category': '黑色系', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            
            # 能源化工 - SC推荐 Mean_Reversion
            'SC': {'name': '原油', 'exchange': 'INE', 'category': '能源化工', 'unit': '元/桶', 'strategy': 'Mean_Reversion', 'win_rate': 0.500},
            'FU': {'name': '燃料油', 'exchange': 'SHFE', 'category': '能源化工', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'RU': {'name': '橡胶', 'exchange': 'SHFE', 'category': '能源化工', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'TA': {'name': 'PTA', 'exchange': 'CZCE', 'category': '能源化工', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'MA': {'name': '甲醇', 'exchange': 'CZCE', 'category': '能源化工', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'EG': {'name': '乙二醇', 'exchange': 'DCE', 'category': '能源化工', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            
            # 建材
            'FG': {'name': '玻璃', 'exchange': 'CZCE', 'category': '建材', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'SA': {'name': '纯碱', 'exchange': 'CZCE', 'category': '建材', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            
            # 农产品
            'M': {'name': '豆粕', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨', 'strategy': 'Mean_Reversion', 'win_rate': 0.500},
            'Y': {'name': '豆油', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'P': {'name': '棕榈油', 'exchange': 'DCE', 'category': '农产品', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'SR': {'name': '白糖', 'exchange': 'CZCE', 'category': '农产品', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'CF': {'name': '棉花', 'exchange': 'CZCE', 'category': '农产品', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
            'OI': {'name': '菜籽油', 'exchange': 'CZCE', 'category': '农产品', 'unit': '元/吨', 'strategy': 'SMA_Crossover', 'win_rate': 0.000},
        }
    
    def get_data(self, symbol):
        try:
            data = ak.futures_main_sina(symbol=f'{symbol}0')
            if data.empty or len(data) < 30:
                return None
            return data
        except:
            return None
    
    # ==================== 高胜率策略实现 ====================
    
    def strategy_sma_crossover(self, data, symbol_info):
        """
        策略1: SMA均线交叉 (金叉做多, 死叉做空)
        适用: AG, IH 等高趋势性品种
        """
        closes = data['收盘价'].values
        highs = data['最高价'].values
        lows = data['最低价'].values
        
        sma5 = np.mean(closes[-5:])
        sma10 = np.mean(closes[-10:])
        sma20 = np.mean(closes[-20:])
        
        # 判断交叉
        prev_sma5 = np.mean(closes[-6:-1])
        prev_sma10 = np.mean(closes[-11:-1])
        
        current_close = closes[-1]
        
        # 金叉信号
        if prev_sma5 <= prev_sma10 and sma5 > sma10:
            direction = 'LONG'
            entry = current_close
            stop = min(lows[-10:]) * 0.99
            target1 = entry + (entry - stop) * 2
            target2 = entry + (entry - stop) * 3
            signal_strength = '强' if current_close > sma20 else '中'
        
        # 死叉信号
        elif prev_sma5 >= prev_sma10 and sma5 < sma10:
            direction = 'SHORT'
            entry = current_close
            stop = max(highs[-10:]) * 1.01
            target1 = entry - (stop - entry) * 2
            target2 = entry - (stop - entry) * 3
            signal_strength = '强' if current_close < sma20 else '中'
        
        else:
            direction = 'NEUTRAL'
            entry = stop = target1 = target2 = None
            signal_strength = '无'
        
        return {
            'direction': direction,
            'entry': entry,
            'stop': stop,
            'target1': target1,
            'target2': target2,
            'sma5': sma5,
            'sma10': sma10,
            'sma20': sma20,
            'signal_strength': signal_strength,
            'strategy_name': 'SMA_Crossover'
        }
    
    def strategy_mean_reversion(self, data, symbol_info):
        """
        策略2: 均值回归 (布林带反转)
        适用: IF, IM, SC 等震荡品种
        """
        closes = data['收盘价'].values
        highs = data['最高价'].values
        lows = data['最低价'].values
        
        sma20 = np.mean(closes[-20:])
        std20 = np.std(closes[-20:])
        
        upper_band = sma20 + 2 * std20
        lower_band = sma20 - 2 * std20
        
        current_close = closes[-1]
        current_high = highs[-1]
        current_low = lows[-1]
        
        # 价格突破上轨, 做空 (回归)
        if current_high > upper_band:
            direction = 'SHORT'
            entry = current_close
            stop = current_high * 1.01
            target1 = sma20
            target2 = lower_band
            signal_strength = '强'
        
        # 价格跌破下轨, 做多 (回归)
        elif current_low < lower_band:
            direction = 'LONG'
            entry = current_close
            stop = current_low * 0.99
            target1 = sma20
            target2 = upper_band
            signal_strength = '强'
        
        # 价格在均线附近, 观望
        else:
            direction = 'NEUTRAL'
            entry = stop = target1 = target2 = None
            signal_strength = '无'
        
        return {
            'direction': direction,
            'entry': entry,
            'stop': stop,
            'target1': target1,
            'target2': target2,
            'sma20': sma20,
            'upper_band': upper_band,
            'lower_band': lower_band,
            'signal_strength': signal_strength,
            'strategy_name': 'Mean_Reversion'
        }
    
    def strategy_volatility_breakout(self, data, symbol_info):
        """
        策略3: 波动率突破 (基于ATR)
        适用: AG 等高波动品种
        """
        closes = data['收盘价'].values
        highs = data['最高价'].values
        lows = data['最低价'].values
        
        # 计算ATR
        tr_list = []
        for i in range(-20, 0):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr_list.append(max(tr1, tr2, tr3))
        atr = np.mean(tr_list)
        
        sma20 = np.mean(closes[-20:])
        current_close = closes[-1]
        
        # 突破 SMA + 0.5*ATR 做多
        if current_close > sma20 + 0.5 * atr:
            direction = 'LONG'
            entry = current_close
            stop = entry - 1.5 * atr
            target1 = entry + 2 * atr
            target2 = entry + 3 * atr
            signal_strength = '强'
        
        # 跌破 SMA - 0.5*ATR 做空
        elif current_close < sma20 - 0.5 * atr:
            direction = 'SHORT'
            entry = current_close
            stop = entry + 1.5 * atr
            target1 = entry - 2 * atr
            target2 = entry - 3 * atr
            signal_strength = '强'
        
        else:
            direction = 'NEUTRAL'
            entry = stop = target1 = target2 = None
            signal_strength = '无'
        
        return {
            'direction': direction,
            'entry': entry,
            'stop': stop,
            'target1': target1,
            'target2': target2,
            'sma20': sma20,
            'atr': atr,
            'signal_strength': signal_strength,
            'strategy_name': 'Volatility_Breakout'
        }
    
    def strategy_breakout(self, data, symbol_info):
        """
        策略4: 突破策略 (突破前高/前低)
        适用: CU 等趋势性品种
        """
        closes = data['收盘价'].values
        highs = data['最高价'].values
        lows = data['最低价'].values
        
        high_20 = max(highs[-20:])
        low_20 = min(lows[-20:])
        
        current_close = closes[-1]
        current_high = highs[-1]
        current_low = lows[-1]
        
        # 突破前高做多
        if current_high > high_20:
            direction = 'LONG'
            entry = current_close
            stop = low_20 * 0.99
            target1 = entry + (entry - stop) * 2
            target2 = entry + (entry - stop) * 3
            signal_strength = '强'
        
        # 跌破前低做空
        elif current_low < low_20:
            direction = 'SHORT'
            entry = current_close
            stop = high_20 * 1.01
            target1 = entry - (stop - entry) * 2
            target2 = entry - (stop - entry) * 3
            signal_strength = '强'
        
        else:
            direction = 'NEUTRAL'
            entry = stop = target1 = target2 = None
            signal_strength = '无'
        
        return {
            'direction': direction,
            'entry': entry,
            'stop': stop,
            'target1': target1,
            'target2': target2,
            'high_20': high_20,
            'low_20': low_20,
            'signal_strength': signal_strength,
            'strategy_name': 'Breakout'
        }
    
    # ==================== 主分析函数 ====================
    
    def analyze_with_strategy(self, symbol, info, data):
        """使用推荐策略进行分析"""
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        closes = data['收盘价'].values
        
        close = latest['收盘价']
        change_pct = ((close - prev['收盘价']) / prev['收盘价']) * 100
        
        # 根据品种选择策略
        strategy_name = info.get('strategy', 'SMA_Crossover')
        win_rate = info.get('win_rate', 0.5)
        
        if strategy_name == 'SMA_Crossover':
            result = self.strategy_sma_crossover(data, info)
        elif strategy_name == 'Mean_Reversion':
            result = self.strategy_mean_reversion(data, info)
        elif strategy_name == 'Volatility_Breakout':
            result = self.strategy_volatility_breakout(data, info)
        elif strategy_name == 'Breakout':
            result = self.strategy_breakout(data, info)
        else:
            result = self.strategy_sma_crossover(data, info)
        
        # 计算波动率
        if len(closes) >= 21:
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(-20, 0)]
            volatility = np.std(returns) * np.sqrt(252) * 100
        else:
            volatility = 0
        
        result.update({
            'symbol': symbol,
            'name': info['name'],
            'category': info['category'],
            'exchange': info['exchange'],
            'unit': info['unit'],
            'close': close,
            'change_pct': change_pct,
            'volume': latest['成交量'],
            'oi': latest['持仓量'],
            'volatility': volatility,
            'win_rate': win_rate,
            'recommended_strategy': strategy_name
        })
        
        return result
    
    def generate_report(self):
        """生成报告"""
        timestamp = datetime.now()
        filename = f"qihuo{timestamp.strftime('%Y%m%d%H%M%S')}.md"
        
        report = f"""# 国内期货15分钟分析报告 (高胜率策略版)

**生成时间:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**分析师:** JARVIS QFA/FOE  
**数据周期:** 15分钟  
**覆盖品种:** {len(self.futures_list)}个  
**策略版本:** V2.0 (基于6个月回测优化)

---

## 📊 策略说明

本报告基于 **6个月历史回测** 结果，为每个品种选择胜率最高的策略：

| 策略 | 适用品种 | 历史胜率 | 特点 |
|------|----------|----------|------|
| **Mean_Reversion** | IF, IM, SC, M | 50-77% | 均值回归，适合震荡 |
| **SMA_Crossover** | AG, IH, AU | 33-50% | 趋势跟踪，盈亏比高 |
| **Volatility_Breakout** | AG | 66.7% | 波动率突破，高收益 |
| **Breakout** | CU | 100% | 趋势突破，信号少 |

---

## 🎯 高胜率重点品种

基于回测，以下品种策略表现优异：
- 🥇 **白银(AG)** + Volatility_Breakout: 66.7% 胜率
- 🥈 **沪深300(IF)** + Mean_Reversion: 77.8% 胜率
- 🥉 **中证1000(IM)** + Mean_Reversion: 62.5% 胜率

---

"""
        
        categories = {}
        high_win_rate_signals = []
        
        for symbol, info in self.futures_list.items():
            data = self.get_data(symbol)
            if data is not None:
                analysis = self.analyze_with_strategy(symbol, info, data)
                cat = info['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(analysis)
                
                # 收集高胜率信号
                if analysis.get('win_rate', 0) >= 0.5 and analysis.get('direction') != 'NEUTRAL':
                    high_win_rate_signals.append(analysis)
        
        # 高胜率信号优先展示
        if high_win_rate_signals:
            report += "## 🔥 高胜率交易信号 (胜率≥50%)\n\n"
            for item in sorted(high_win_rate_signals, key=lambda x: x.get('win_rate', 0), reverse=True):
                emoji = "🟢" if item['change_pct'] > 0 else "🔴"
                rr = abs(item['target1'] - item['entry']) / abs(item['entry'] - item['stop']) if item['entry'] and item['stop'] else 0
                report += f"""### {emoji} {item['name']} ({item['symbol']}) - 胜率 {item['win_rate']:.1%}

**策略:** {item['recommended_strategy']} | **方向:** {item['direction']}

**基础数据:**
- 最新价: {item['close']:.2f} {item['unit']}
- 涨跌: {item['change_pct']:+.2f}%
- 成交量: {item['volume']:,}

**交易计划:**
- 入场: {item['entry']:.2f}
- 停损: {item['stop']:.2f} (风险 {abs(item['entry']-item['stop'])/item['entry']*100:.2f}%)
- 目标1: {item['target1']:.2f} (收益 {abs(item['target1']-item['entry'])/item['entry']*100:.2f}%)
- 目标2: {item['target2']:.2f}
- 盈亏比: {rr:.2f}
- 信号强度: {item.get('signal_strength', '中')}

---

"""
        
        # 分类展示所有品种
        for cat, items in categories.items():
            report += f"## {cat}\n\n"
            for item in items:
                emoji = "🟢" if item['change_pct'] > 0 else "🔴" if item['change_pct'] < 0 else "⚪"
                win_rate_emoji = "⭐" if item.get('win_rate', 0) >= 0.5 else ""
                
                report += f"""### {emoji} {item['name']} ({item['symbol']}) {win_rate_emoji}

**基础数据:**
- 最新价: {item['close']:.2f} {item['unit']}
- 涨跌: {item['change_pct']:+.2f}%
- 成交量: {item['volume']:,}
- 持仓量: {item['oi']:,}

**策略信息:**
- 推荐策略: **{item['recommended_strategy']}**
- 历史胜率: {item.get('win_rate', 0):.1%}
- 波动率: {item['volatility']:.2f}%

**交易计划:**
- 方向: **{item['direction']}**
"""
                if item.get('entry'):
                    rr = abs(item['target1'] - item['entry']) / abs(item['entry'] - item['stop']) if item['stop'] else 0
                    report += f"""- 入场: {item['entry']:.2f}
- 停损: {item['stop']:.2f}
- 目标1: {item['target1']:.2f}
- 目标2: {item['target2']:.2f}
- 盈亏比: {rr:.2f}
- 信号强度: {item.get('signal_strength', '中')}
"""
                else:
                    report += "- 建议观望 (无明确信号)\n"
                report += "\n---\n\n"
        
        report += """## ⚠️ 风险提示与免责声明

### 高胜率策略说明
- 回测胜率基于历史数据，不代表未来表现
- 实际交易中需考虑滑点、手续费等因素
- 建议先用模拟盘验证策略有效性

### 风险管理
- 单笔交易风险不超过本金2%
- 严格执行止损，不扛单
- 分散投资，不要重仓单一品种

### 免责声明
- 本报告仅供参考，不构成投资建议
- 期货交易风险极高，可能导致本金全部损失
- 投资者应根据自身情况独立判断

---

*报告由 JARVIS QFA/FOE 自动生成*  
*策略基于6个月历史回测优化*
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
            commit_msg = f"Auto: {filename} - High Win Rate Strategy Analysis"
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
    analyzer = ChinaFuturesAutoAnalyzerV2()
    analyzer.save_and_push()
