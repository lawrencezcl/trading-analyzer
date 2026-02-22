#!/usr/bin/env python3
"""
15分钟间隔市场观察任务
生成交易时间段的分析报告
"""

import json
import sys
import os
from datetime import datetime, timedelta
from data_api import FinancialDataAPI, FinnhubAPI, TwelveDataAPI
from goldapi import GoldAPI
from yahoo_finance_api import YahooFinanceAPI

# 交易时间段配置 (美东时间)
TRADING_HOURS = {
    'pre_market': ('04:00', '09:30'),    # 盘前
    'regular': ('09:30', '16:00'),        # 常规交易
    'after_hours': ('16:00', '20:00')     # 盘后
}

# 观察的品种
INDICES = {
    'SPX': {'symbol': 'SPY', 'name': 'S&P 500', 'futures': 'ES', 'type': 'index', 'source': 'finnhub'},
    'NQ': {'symbol': 'QQQ', 'name': 'NASDAQ 100', 'futures': 'NQ', 'type': 'index', 'source': 'finnhub'},
    'JP225': {'symbol': '^N225', 'name': 'Nikkei 225', 'futures': 'NKD', 'type': 'index', 'source': 'yahoo'},
    'DAX': {'symbol': '^GDAXI', 'name': 'DAX 40', 'futures': 'FDAX', 'type': 'index', 'source': 'yahoo'},
    'XAU': {'symbol': 'XAU', 'name': 'Gold', 'futures': 'GC', 'type': 'commodity', 'source': 'goldapi'},
    'XAG': {'symbol': 'XAG', 'name': 'Silver', 'futures': 'SI', 'type': 'commodity', 'source': 'goldapi'}
}

# 初始化 API
finnhub_api = FinancialDataAPI()
goldapi = GoldAPI()
yahoo_api = YahooFinanceAPI()

def get_current_data(symbol, source='finnhub'):
    """获取当前数据 - 多数据源"""
    try:
        if source == 'goldapi':
            # GoldAPI 获取贵金属
            return goldapi.get_price(symbol)
        elif source == 'yahoo':
            # Yahoo Finance 获取指数
            result = yahoo_api.get_quote(symbol)
            if 'error' not in result:
                return {
                    'price': result.get('price'),
                    'change': result.get('change'),
                    'change_pct': result.get('change_pct'),
                    'high': result.get('high'),
                    'low': result.get('low'),
                    'open': result.get('open'),
                    'prev_close': result.get('prev_close'),
                    'timestamp': datetime.now().isoformat()
                }
            return result
        else:
            # 默认 Finnhub
            quote = finnhub_api.finnhub.get_quote(symbol)
            return {
                'price': quote.get('c'),
                'change': quote.get('d'),
                'change_pct': quote.get('dp'),
                'high': quote.get('h'),
                'low': quote.get('l'),
                'open': quote.get('o'),
                'prev_close': quote.get('pc'),
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {'error': str(e)}

def analyze_wyckoff(price, high, low, open_price, prev_close):
    """威科夫分析"""
    analysis = {
        'phase': 'unknown',
        'signals': [],
        'key_levels': {
            'resistance': high,
            'support': low,
            'poc': (high + low) / 2  # Point of Control
        }
    }
    
    # 判断阶段
    if price > prev_close:
        if price > (high + low) / 2:
            analysis['phase'] = 'markup'
            analysis['signals'].append('价格在上半区，多头控制')
        else:
            analysis['phase'] = 'accumulation'
            analysis['signals'].append('价格反弹但仍在区间下半')
    else:
        if price < (high + low) / 2:
            analysis['phase'] = 'markdown'
            analysis['signals'].append('价格在下半区，空头控制')
        else:
            analysis['phase'] = 'distribution'
            analysis['signals'].append('价格回落但仍在区间上半')
    
    return analysis

def analyze_caisen(price, high, low, open_price, prev_close):
    """蔡森技术分析"""
    analysis = {
        'pattern': 'none',
        'signals': [],
        'levels': {}
    }
    
    # 判断K线形态
    body = abs(price - open_price)
    upper_shadow = high - max(price, open_price)
    lower_shadow = min(price, open_price) - low
    
    if body > (high - low) * 0.6:
        if price > open_price:
            analysis['pattern'] = '长阳线'
            analysis['signals'].append('多头强势')
        else:
            analysis['pattern'] = '长阴线'
            analysis['signals'].append('空头强势')
    elif upper_shadow > body * 2:
        analysis['pattern'] = '流星线'
        analysis['signals'].append('上方压力大')
    elif lower_shadow > body * 2:
        analysis['pattern'] = '锤子线'
        analysis['signals'].append('下方支撑强')
    
    # 支撑压力
    analysis['levels'] = {
        'resistance_1': high,
        'resistance_2': round(high + (high - low) * 0.382, 2),
        'support_1': low,
        'support_2': round(low - (high - low) * 0.382, 2),
        'pivot': round((high + low + price) / 3, 2)
    }
    
    return analysis

def generate_trading_plan(index_name, data, wyckoff, caisen):
    """生成交易计划"""
    price = data.get('price', 0)
    
    plan = {
        'direction': 'neutral',
        'entry': None,
        'stop_loss': None,
        'target': None,
        'confidence': 'low',
        'rationale': []
    }
    
    # 基于分析生成计划
    if wyckoff['phase'] == 'markup' and '多头' in str(caisen['signals']):
        plan['direction'] = 'long'
        plan['entry'] = price
        plan['stop_loss'] = caisen['levels']['support_1']
        plan['target'] = caisen['levels']['resistance_2']
        plan['confidence'] = 'medium'
        plan['rationale'] = ['威科夫上涨阶段', '蔡森多头信号']
    elif wyckoff['phase'] == 'markdown' and '空头' in str(caisen['signals']):
        plan['direction'] = 'short'
        plan['entry'] = price
        plan['stop_loss'] = caisen['levels']['resistance_1']
        plan['target'] = caisen['levels']['support_2']
        plan['confidence'] = 'medium'
        plan['rationale'] = ['威科夫下跌阶段', '蔡森空头信号']
    
    return plan

def generate_report():
    """生成完整报告"""
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')
    readable_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    report = {
        'metadata': {
            'generated_at': readable_time,
            'filename': f'{timestamp}.md',
            'interval': '15min',
            'timezone': 'Asia/Shanghai'
        },
        'indices': {}
    }
    
    for index_code, config in INDICES.items():
        symbol = config['symbol']
        source = config.get('source', 'finnhub')
        data = get_current_data(symbol, source)
        
        if 'error' in data:
            report['indices'][index_code] = {'error': data['error']}
            continue
        
        # 分析
        wyckoff = analyze_wyckoff(
            data['price'], data['high'], data['low'],
            data['open'], data['prev_close']
        )
        
        caisen = analyze_caisen(
            data['price'], data['high'], data['low'],
            data['open'], data['prev_close']
        )
        
        plan = generate_trading_plan(index_code, data, wyckoff, caisen)
        
        report['indices'][index_code] = {
            'name': config['name'],
            'futures': config['futures'],
            'type': config.get('type', 'index'),
            'data': data,
            'wyckoff_analysis': wyckoff,
            'caisen_analysis': caisen,
            'trading_plan': plan
        }
    
    return report, timestamp

def format_price(price, symbol_type='index'):
    """根据品种类型格式化价格"""
    if symbol_type == 'commodity':
        return f"${price:.2f}"
    return f"${price:.2f}"

def format_feishu_message(report):
    """格式化为飞书消息 - 详细版"""
    meta = report['metadata']
    
    msg = f"""📊 15分钟市场观察报告 | {meta['generated_at']}

"""
    
    # 指数部分
    indices_data = {k: v for k, v in report['indices'].items() if v.get('type') == 'index' or k in ['SPX', 'NQ', 'JP225', 'DAX']}
    commodities_data = {k: v for k, v in report['indices'].items() if v.get('type') == 'commodity' or k in ['XAU', 'XAG']}
    
    if indices_data:
        msg += "═══════════════════\n📈 股票指数\n═══════════════════\n"
        for index_code, data in indices_data.items():
            if 'error' in data:
                msg += f"\n❌ {index_code}: 数据获取失败\n"
                continue
            
            quote = data['data']
            wyckoff = data['wyckoff_analysis']
            caisen = data['caisen_analysis']
            plan = data['trading_plan']
            
            # 方向表情
            if plan['direction'] == 'long':
                direction_emoji = "🟢 做多"
            elif plan['direction'] == 'short':
                direction_emoji = "🔴 做空"
            else:
                direction_emoji = "⚪ 观望"
            
            # 涨跌幅表情
            if quote['change_pct'] > 2:
                change_emoji = "🚀"
            elif quote['change_pct'] > 0:
                change_emoji = "📈"
            elif quote['change_pct'] < -2:
                change_emoji = "💥"
            elif quote['change_pct'] < 0:
                change_emoji = "📉"
            else:
                change_emoji = "➖"
            
            msg += f"""
┌─ {index_code} | {data['name']} ({data['futures']})
│
│  💰 价格: ${quote['price']:.2f} {change_emoji} {quote['change_pct']:+.2f}%
│     高: ${quote['high']:.2f} | 低: ${quote['low']:.2f}
│
│  📊 威科夫: {wyckoff['phase'].upper()}
│  🕯️ 形态: {caisen['pattern']}
│
│  🎯 关键位:
│     阻力: ${wyckoff['key_levels']['resistance']:.2f}
│     支撑: ${wyckoff['key_levels']['support']:.2f}
│     枢轴: ${caisen['levels']['pivot']:.2f}
│
│  ⚡ 信号: {', '.join(wyckoff['signals']) if wyckoff['signals'] else '无'}
│
│  📋 交易计划: {direction_emoji}
"""
            
            if plan['entry']:
                rr_ratio = abs(plan['target'] - plan['entry']) / abs(plan['entry'] - plan['stop_loss']) if plan['stop_loss'] else 0
                msg += f"""│     入场: ${plan['entry']:.2f}
│     停损: ${plan['stop_loss']:.2f} (风险 {abs(plan['entry']-plan['stop_loss'])/plan['entry']*100:.1f}%)
│     目标: ${plan['target']:.2f} (收益 {abs(plan['target']-plan['entry'])/plan['entry']*100:.1f}%)
│     盈亏比: {rr_ratio:.2f}
│     置信度: {plan['confidence'].upper()}
"""
            else:
                msg += "│     当前无明确交易信号，建议观望\n"
            
            msg += "│\n└────────────────────\n"
    
    # 贵金属部分
    if commodities_data:
        msg += "\n═══════════════════\n🥇 贵金属\n═══════════════════\n"
        for index_code, data in commodities_data.items():
            if 'error' in data:
                msg += f"\n❌ {index_code}: 数据获取失败\n"
                continue
            
            quote = data['data']
            wyckoff = data['wyckoff_analysis']
            caisen = data['caisen_analysis']
            plan = data['trading_plan']
            
            if plan['direction'] == 'long':
                direction_emoji = "🟢 做多"
            elif plan['direction'] == 'short':
                direction_emoji = "🔴 做空"
            else:
                direction_emoji = "⚪ 观望"
            
            if quote['change_pct'] > 3:
                change_emoji = "🚀"
            elif quote['change_pct'] > 0:
                change_emoji = "📈"
            elif quote['change_pct'] < -3:
                change_emoji = "💥"
            elif quote['change_pct'] < 0:
                change_emoji = "📉"
            else:
                change_emoji = "➖"
            
            msg += f"""
┌─ {index_code} | {data['name']} ({data['futures']})
│
│  💰 价格: ${quote['price']:.2f} {change_emoji} {quote['change_pct']:+.2f}%
│     高: ${quote['high']:.2f} | 低: ${quote['low']:.2f}
│
│  📊 威科夫: {wyckoff['phase'].upper()} | 形态: {caisen['pattern']}
│
│  🎯 关键位: 阻 ${wyckoff['key_levels']['resistance']:.2f} / 支 ${wyckoff['key_levels']['support']:.2f}
│
│  📋 交易计划: {direction_emoji}
"""
            
            if plan['entry']:
                rr_ratio = abs(plan['target'] - plan['entry']) / abs(plan['entry'] - plan['stop_loss']) if plan['stop_loss'] else 0
                msg += f"""│     入场: ${plan['entry']:.2f}
│     停损: ${plan['stop_loss']:.2f}
│     目标: ${plan['target']:.2f}
│     盈亏比: {rr_ratio:.2f}
"""
            else:
                msg += "│     观望\n"
            
            msg += "│\n└────────────────────\n"
    
    msg += f"""
═══════════════════
💡 交易提示
═══════════════════
• 所有信号基于威科夫+蔡森技术分析
• 严格执行停损，单笔风险不超过2%
• 重大数据/事件前减仓

⏰ 下次观察: {(datetime.now() + timedelta(minutes=15)).strftime('%H:%M')}
📁 详细报告: market-reports/{meta['generated_at'].replace('-','').replace(':','').replace(' ','')}.md
"""
    
    return msg

def format_md_report(report, timestamp):
    """格式化为Markdown"""
    meta = report['metadata']
    
    md = f"""# 15分钟市场观察报告

## 报告信息
- **生成时间:** {meta['generated_at']}
- **时间周期:** {meta['interval']}
- **时区:** {meta['timezone']}

---

"""
    
    # 分类显示
    indices_data = {k: v for k, v in report['indices'].items() if v.get('type') == 'index' or k in ['SPX', 'NQ', 'JP225', 'DAX']}
    commodities_data = {k: v for k, v in report['indices'].items() if v.get('type') == 'commodity' or k in ['XAU', 'XAG']}
    
    # 指数部分
    if indices_data:
        md += "## 📊 股票指数\n\n"
        for index_code, data in indices_data.items():
            if 'error' in data:
                md += f"### {index_code}\n\n**错误:** {data['error']}\n\n---\n\n"
                continue
            
            quote = data['data']
            wyckoff = data['wyckoff_analysis']
            caisen = data['caisen_analysis']
            plan = data['trading_plan']
            
            md += f"""### {index_code} - {data['name']} ({data['futures']})

**实时数据:** 当前 {format_price(quote['price'], 'index')} | 涨跌 {quote['change']:+.2f} ({quote['change_pct']:+.2f}%)

**威科夫阶段:** {wyckoff['phase'].upper()} | **蔡森形态:** {caisen['pattern']}

**关键价位:** 阻力 ${wyckoff['key_levels']['resistance']:.2f} / 支撑 ${wyckoff['key_levels']['support']:.2f}

**交易计划:** {plan['direction'].upper()} | 入场 ${plan['entry']:.2f if plan['entry'] else 0:.2f} | 停损 ${plan['stop_loss']:.2f if plan['stop_loss'] else 0:.2f} | 目标 ${plan['target']:.2f if plan['target'] else 0:.2f}

---

"""
    
    # 大宗商品部分
    if commodities_data:
        md += "## 🥇 贵金属\n\n"
        for index_code, data in commodities_data.items():
            if 'error' in data:
                md += f"### {index_code}\n\n**错误:** {data['error']}\n\n---\n\n"
                continue
            
            quote = data['data']
            wyckoff = data['wyckoff_analysis']
            caisen = data['caisen_analysis']
            plan = data['trading_plan']
            
            md += f"""### {index_code} - {data['name']} ({data['futures']})

**实时数据:** 当前 {format_price(quote['price'], 'commodity')} | 涨跌 {quote['change']:+.2f} ({quote['change_pct']:+.2f}%)

**威科夫阶段:** {wyckoff['phase'].upper()} | **蔡森形态:** {caisen['pattern']}

**关键价位:** 阻力 ${wyckoff['key_levels']['resistance']:.2f} / 支撑 ${wyckoff['key_levels']['support']:.2f}

**交易计划:** {plan['direction'].upper()} | 入场 ${plan['entry']:.2f if plan['entry'] else 0:.2f} | 停损 ${plan['stop_loss']:.2f if plan['stop_loss'] else 0:.2f} | 目标 ${plan['target']:.2f if plan['target'] else 0:.2f}

---

"""
    
    md += f"""## 总结与观察

### 市场整体评估
- **SPX:** 观察 $692 突破情况
- **NQ:** 关注 $610 压力
- **JP225:** 高位震荡，谨慎
- **DAX:** 等待区间突破
- **XAU:** 关注 $2900 关键位
- **XAG:** 关注 $32 支撑

### 风险提示
1. 所有信号仅供参考，不构成投资建议
2. 严格执行停损，控制风险
3. 注意市场流动性变化
4. 重大新闻事件前减仓

### 下次观察
**预计时间:** {(datetime.now() + timedelta(minutes=15)).strftime('%H:%M')}

---
*报告由 JARVIS 自动生成*
"""
    
    return md

if __name__ == "__main__":
    report, timestamp = generate_report()
    md_content = format_md_report(report, timestamp)
    feishu_msg = format_feishu_message(report)
    
    # 输出到文件
    output_dir = "/root/.openclaw/workspace/market-reports"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # 输出飞书消息到stdout，供外部调用
    print("=== FEISHU_MSG_START ===")
    print(feishu_msg)
    print("=== FEISHU_MSG_END ===")
    
    print(f"\n报告已生成: {filepath}")
