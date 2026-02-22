#!/usr/bin/env python3
"""
实时金融数据 API 集成模块
支持 Finnhub, Twelve Data, Alpha Vantage
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

# API 配置
FINNHUB_API_KEY = "d6476nhr01ql6dj2ekegd6476nhr01ql6dj2ekf0"
TWELVE_DATA_API_KEY = "f5491ce160e64101a960e19eb8363f38"
ALPHA_VANTAGE_API_KEY = "IUO07N60XUPUHNTL"
TAVILY_API_KEY = "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"

class FinnhubAPI:
    """Finnhub API 封装"""
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: str = FINNHUB_API_KEY):
        self.api_key = api_key
    
    def get_quote(self, symbol: str) -> Dict:
        """获取实时报价"""
        url = f"{self.BASE_URL}/quote"
        params = {"symbol": symbol, "token": self.api_key}
        response = requests.get(url, params=params)
        return response.json()
    
    def get_profile(self, symbol: str) -> Dict:
        """获取公司信息"""
        url = f"{self.BASE_URL}/stock/profile2"
        params = {"symbol": symbol, "token": self.api_key}
        response = requests.get(url, params=params)
        return response.json()
    
    def get_financials(self, symbol: str) -> Dict:
        """获取财务报表"""
        url = f"{self.BASE_URL}/stock/financials"
        params = {"symbol": symbol, "statement": "bs", "token": self.api_key}
        response = requests.get(url, params=params)
        return response.json()
    
    def get_news(self, symbol: str, from_date: str, to_date: str) -> List:
        """获取公司新闻"""
        url = f"{self.BASE_URL}/company-news"
        params = {
            "symbol": symbol,
            "from": from_date,
            "to": to_date,
            "token": self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_peers(self, symbol: str) -> List:
        """获取同行业公司"""
        url = f"{self.BASE_URL}/stock/peers"
        params = {"symbol": symbol, "token": self.api_key}
        response = requests.get(url, params=params)
        return response.json()


class TwelveDataAPI:
    """Twelve Data API 封装"""
    
    BASE_URL = "https://api.twelvedata.com"
    
    def __init__(self, api_key: str = TWELVE_DATA_API_KEY):
        self.api_key = api_key
    
    def get_quote(self, symbol: str) -> Dict:
        """获取实时报价"""
        url = f"{self.BASE_URL}/quote"
        params = {"symbol": symbol, "apikey": self.api_key}
        response = requests.get(url, params=params)
        return response.json()
    
    def get_time_series(self, symbol: str, interval: str = "1day", outputsize: int = 30) -> Dict:
        """获取历史价格数据"""
        url = f"{self.BASE_URL}/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_technical_indicators(self, symbol: str, indicator: str = "rsi") -> Dict:
        """获取技术指标"""
        url = f"{self.BASE_URL}/{indicator}"
        params = {"symbol": symbol, "apikey": self.api_key}
        response = requests.get(url, params=params)
        return response.json()
    
    def get_earnings(self, symbol: str) -> Dict:
        """获取盈利数据"""
        url = f"{self.BASE_URL}/earnings"
        params = {"symbol": symbol, "apikey": self.api_key}
        response = requests.get(url, params=params)
        return response.json()


class AlphaVantageAPI:
    """Alpha Vantage API 封装"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str = ALPHA_VANTAGE_API_KEY):
        self.api_key = api_key
    
    def get_overview(self, symbol: str) -> Dict:
        """获取公司概览"""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        return response.json()
    
    def get_income_statement(self, symbol: str) -> Dict:
        """获取利润表"""
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbol,
            "apikey": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        return response.json()
    
    def get_balance_sheet(self, symbol: str) -> Dict:
        """获取资产负债表"""
        params = {
            "function": "BALANCE_SHEET",
            "symbol": symbol,
            "apikey": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        return response.json()
    
    def get_cash_flow(self, symbol: str) -> Dict:
        """获取现金流量表"""
        params = {
            "function": "CASH_FLOW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        return response.json()
    
    def get_technical_indicator(self, symbol: str, indicator: str = "RSI", interval: str = "daily") -> Dict:
        """获取技术指标"""
        params = {
            "function": indicator,
            "symbol": symbol,
            "interval": interval,
            "time_period": 14,
            "series_type": "close",
            "apikey": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        return response.json()


class TavilyAPI:
    """Tavily AI 搜索 API"""
    
    BASE_URL = "https://api.tavily.com"
    
    def __init__(self, api_key: str = TAVILY_API_KEY):
        self.api_key = api_key
    
    def search(self, query: str, search_depth: str = "basic", max_results: int = 5) -> Dict:
        """AI 增强搜索"""
        url = f"{self.BASE_URL}/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.json()


# 统一接口
class FinancialDataAPI:
    """统一金融数据接口"""
    
    def __init__(self):
        self.finnhub = FinnhubAPI()
        self.twelve_data = TwelveDataAPI()
        self.alpha_vantage = AlphaVantageAPI()
        self.tavily = TavilyAPI()
    
    def get_stock_quote(self, symbol: str) -> Dict:
        """获取股票实时报价"""
        return self.finnhub.get_quote(symbol)
    
    def get_stock_profile(self, symbol: str) -> Dict:
        """获取公司信息"""
        return self.finnhub.get_profile(symbol)
    
    def get_financial_data(self, symbol: str) -> Dict:
        """获取财务数据"""
        return {
            "overview": self.alpha_vantage.get_overview(symbol),
            "income": self.alpha_vantage.get_income_statement(symbol),
            "balance": self.alpha_vantage.get_balance_sheet(symbol),
            "cash_flow": self.alpha_vantage.get_cash_flow(symbol)
        }
    
    def get_technical_analysis(self, symbol: str) -> Dict:
        """获取技术分析数据"""
        return {
            "price_history": self.twelve_data.get_time_series(symbol),
            "rsi": self.twelve_data.get_technical_indicators(symbol, "rsi"),
            "sma": self.twelve_data.get_technical_indicators(symbol, "sma")
        }
    
    def search_news(self, query: str) -> Dict:
        """AI 搜索新闻"""
        return self.tavily.search(query, search_depth="advanced", max_results=10)


if __name__ == "__main__":
    # 测试
    api = FinancialDataAPI()
    
    # 测试 Finnhub
    print("=== Finnhub Quote ===")
    print(json.dumps(api.get_stock_quote("AAPL"), indent=2))
    
    # 测试 Tavily
    print("\n=== Tavily Search ===")
    print(json.dumps(api.search_news("Apple stock analysis 2024"), indent=2))
