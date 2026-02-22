#!/usr/bin/env python3
"""
GoldAPI.io 数据获取模块
用于获取贵金属实时价格
"""

import requests
import json
from datetime import datetime

class GoldAPI:
    """GoldAPI.io 封装"""
    
    BASE_URL = "https://www.goldapi.io/api"
    API_KEY = "goldapi-72cmsmlxs0po2-io"
    
    # 品种映射
    METALS = {
        'XAU': {'symbol': 'XAU', 'name': 'Gold', 'currency': 'USD'},
        'XAG': {'symbol': 'XAG', 'name': 'Silver', 'currency': 'USD'},
        'XPT': {'symbol': 'XPT', 'name': 'Platinum', 'currency': 'USD'},
        'XPD': {'symbol': 'XPD', 'name': 'Palladium', 'currency': 'USD'},
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key or self.API_KEY
        self.headers = {
            'x-access-token': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_price(self, symbol):
        """获取单个品种价格"""
        url = f"{self.BASE_URL}/{symbol}/USD"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'price': data.get('price', 0),
                    'change': data.get('ch', 0),
                    'change_pct': data.get('chp', 0),
                    'high': data.get('high', 0),
                    'low': data.get('low', 0),
                    'open': data.get('open', 0),
                    'prev_close': data.get('prev_close', 0),
                    'timestamp': datetime.now().isoformat(),
                    'currency': 'USD'
                }
            else:
                return {'error': f'HTTP {response.status_code}: {response.text}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_all_metals(self):
        """获取所有贵金属价格"""
        results = {}
        for code, info in self.METALS.items():
            result = self.get_price(info['symbol'])
            result['name'] = info['name']
            results[code] = result
        return results

if __name__ == "__main__":
    api = GoldAPI()
    
    print("=== GoldAPI.io 贵金属实时价格 ===\n")
    
    # 测试黄金
    print("黄金 (XAU):")
    gold = api.get_price('XAU')
    if 'error' in gold:
        print(f"  错误: {gold['error']}")
    else:
        print(f"  价格: ${gold['price']:.2f}")
        print(f"  涨跌: {gold['change']:+.2f} ({gold['change_pct']:+.2f}%)")
        print(f"  最高: ${gold['high']:.2f}")
        print(f"  最低: ${gold['low']:.2f}")
    
    # 测试白银
    print("\n白银 (XAG):")
    silver = api.get_price('XAG')
    if 'error' in silver:
        print(f"  错误: {silver['error']}")
    else:
        print(f"  价格: ${silver['price']:.2f}")
        print(f"  涨跌: {silver['change']:+.2f} ({silver['change_pct']:+.2f}%)")
        print(f"  最高: ${silver['high']:.2f}")
        print(f"  最低: ${silver['low']:.2f}")
