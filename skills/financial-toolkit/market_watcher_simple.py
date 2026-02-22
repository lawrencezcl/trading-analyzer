#!/usr/bin/env python3
"""
15分钟间隔市场观察任务 - 带超时的简化版本
生成交易时间段的分析报告
"""

import json
import sys
import os
from datetime import datetime, timedelta
import requests

# 观察的品种 - 使用 Yahoo Finance (更可靠)
INDICES = {
    'SPX': {'symbol': '^GSPC', 'name': 'S&P 500', 'futures': 'ES', 'type': 'index'},
    'NQ': {'symbol': '^IXIC', 'name': 'NASDAQ 100', 'futures': 'NQ', 'type': 'index'},
    'JP225': {'symbol': '^N225', 'name': 'Nikkei 225', 'futures': 'NKD', 'type': 'index'},
    'DAX': {'symbol': '^GDAXI', 'name': 'DAX 40', 'futures': 'FDAX', 'type': 'index'},
    'XAU': {'symbol': 'GC=F', 'name': 'Gold Futures', 'futures': 'GC', 'type': 'commodity'},
    'XAG': {'symbol': 'SI=F', 'name': 'Silver Futures', 'futures': 'SI', 'type': 'commodity'}
}

def get_yahoo_data(symbol):
    """从 Yahoo Finance 获取数据 - 带超时"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            return {'error': 'No data available'}
        
        result = data['chart']['result'][0]
        meta = result['meta']
        
        # 获取最新价格
        price = meta.get('regularMarketPrice', 0)
        prev_close = meta.get('previousClose', 0)
        
        # 从 indicators 获取高低开
        if 'indicators' in result and 'quote' in result['indicators'] and result['indicators']['quote']:
            quote = result['indicators']['quote'][0]
            high = max([x for x in quote.get('high', []) if x is not None]) if quote.get('high') else price
            low = min([x for x in quote.get('low', []) if x is not None]) if quote.get('low') else price
            open_price = quote.get('open', [price])[0] if quote.get('open') else price
        else:
            high = price * 1.01
            low = price * 0.99
            open_price = price
        
        change = price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        return {
            'price': price,
            'change': change,
            'change_pct': change_pct,
            'high': high,
            'low': low,
            'open': open_price,
            'prev_close': prev_close,
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
            'poc': (high + low) / 2
        }
    }
    
    mid = (high + low) / 2
    
    if price > prev_close:
        if price > mid:
            analysis['phase'] = 'markup'
            analysis['signals'].append('价格在上半区，多头控制')
        else:
            analysis['phase'] = 'accumulation'
            analysis['signals'].append('价格反弹但仍在区间下半')
    else:
        if price < mid:
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
        data = get_yahoo_data(symbol)
        
        if 'error' in data:
            report['indices'][index_code] = {'error': data['error']}
            continue
        
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
    
    indices_data = {k: v for k, v in report['indices'].items() if v.get('type') == 'index'}
    commodities_data = {k: v for k, v in report['indices'].items() if v.get('type') == 'commodity'}
    
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

**实时数据:** 当前 ${quote['price']:.2f} | 涨跌 {quote['change']:+.2f} ({quote['change_pct']:+.2f}%)

**威科夫阶段:** {wyckoff['phase'].upper()} | **蔡森形态:** {caisen['pattern']}

**关键价位:** 阻力 ${wyckoff['key_levels']['resistance']:.2f} / 支撑 ${wyckoff['key_levels']['support']:.2f}

**交易计划:** {plan['direction'].upper()} | 入场 ${plan['entry']:.2f if plan['entry'] else 0:.2f} | 停损 ${plan['stop_loss']:.2f if plan['stop_loss'] else 0:.2f} | 目标 ${plan['target']:.2f if plan['target'] else 0:.2f}

---

"""
    
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

**实时数据:** 当前 ${quote['price']:.2f} | 涨跌 {quote['change']:+.2f} ({quote['change_pct']:+.2f}%)

**威科夫阶段:** {wyckoff['phase'].upper()} | **蔡森形态:** {caisen['pattern']}

**关键价位:** 阻力 ${wyckoff['key_levels']['resistance']:.2f} / 支撑 ${wyckoff['key_levels']['support']:.2f}

**交易计划:** {plan['direction'].upper()} | 入场 ${plan['entry']:.2f if plan['entry'] else 0:.2f} | 停损 ${plan['stop_loss']:.2f if plan['stop_loss'] else 0:.2f} | 目标 ${plan['target']:.2f if plan['target'] else 0:.2f}

---

"""
    
    md += f"""## 总结与观察

### 市场整体评估
- **SPX:** 观察关键价位突破情况
- **NQ:** 关注技术压力
- **JP225:** 注意亚洲市场情绪
- **DAX:** 欧洲市场动态
- **XAU:** 关注黄金关键位
- **XAG:** 白银支撑压力

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
    
    # 输出到文件
    output_dir = "/root/.openclaw/workspace/market-reports"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"报告已生成: {filepath}")
    print(f"生成时间: {report['metadata']['generated_at']}")
