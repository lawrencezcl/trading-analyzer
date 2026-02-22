#!/usr/bin/env python3
"""
Yahoo Finance 数据获取模块
用于获取指数和期货数据
"""

import yfinance as yf
from datetime import datetime

class YahooFinanceAPI:
    """Yahoo Finance API 封装"""
    
    # 指数映射
    INDICES = {
        'SPX': {'symbol': '^GSPC', 'name': 'S&P 500', 'type': 'index'},
        'NQ': {'symbol': '^NDX', 'name': 'NASDAQ 100', 'type': 'index'},
        'DAX': {'symbol': '^GDAXI', 'name': 'DAX 40', 'type': 'index'},
        'JP225': {'symbol': '^N225', 'name': 'Nikkei 225', 'type': 'index'},
    }
    
    # 期货映射
    FUTURES = {
        'ES': {'symbol': 'ES=F', 'name': 'E-mini S&P 500', 'type': 'future'},
        'NQ_F': {'symbol': 'NQ=F', 'name': 'E-mini NASDAQ 100', 'type': 'future'},
        'GC': {'symbol': 'GC=F', 'name': 'Gold', 'type': 'commodity'},
        'SI': {'symbol': 'SI=F', 'name': 'Silver', 'type': 'commodity'},
        'NKD': {'symbol': 'NKD=F', 'name': 'Nikkei 225 Futures', 'type': 'future'},
    }
    
    def get_quote(self, symbol):
        """获取实时报价"""
        try:
            ticker = yf.Ticker(symbol)
            # 获取最新数据
            data = ticker.history(period='1d', interval='1m')
            if data.empty:
                # 尝试日数据
                data = ticker.history(period='5d', interval='1d')
            
            if data.empty:
                return {'error': 'No data available'}
            
            last = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else last
            
            return {
                'price': float(last['Close']),
                'change': float(last['Close'] - prev['Close']),
                'change_pct': float((last['Close'] - prev['Close']) / prev['Close'] * 100),
                'high': float(last['High']),
                'low': float(last['Low']),
                'open': float(last['Open']),
                'prev_close': float(prev['Close']),
                'volume': int(last['Volume']) if 'Volume' in last else 0,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_index_quote(self, index_code):
        """获取指数报价"""
        if index_code in self.INDICES:
            symbol = self.INDICES[index_code]['symbol']
            result = self.get_quote(symbol)
            result['name'] = self.INDICES[index_code]['name']
            return result
        return {'error': f'Unknown index: {index_code}'}
    
    def get_future_quote(self, future_code):
        """获取期货报价"""
        if future_code in self.FUTURES:
            symbol = self.FUTURES[future_code]['symbol']
            result = self.get_quote(symbol)
            result['name'] = self.FUTURES[future_code]['name']
            return result
        return {'error': f'Unknown future: {future_code}'}
    
    def get_all_market_data(self):
        """获取所有市场数据"""
        results = {}
        
        # 获取指数
        for code in self.INDICES:
            results[code] = self.get_index_quote(code)
        
        # 获取期货/商品
        for code in ['GC', 'SI']:
            results[code] = self.get_future_quote(code)
        
        return results

if __name__ == "__main__":
    api = YahooFinanceAPI()
    
    # 测试
    print("=== Yahoo Finance 市场数据 ===\n")
    
    data = api.get_all_market_data()
    for code, info in data.items():
        if 'error' in info:
            print(f"{code}: {info['error']}")
        else:
            print(f"{code} ({info.get('name', '')}): {info['price']:.2f} ({info['change_pct']:+.2f}%)")
