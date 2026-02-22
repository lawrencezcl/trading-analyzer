#!/usr/bin/env python3
"""
MCP (Model Context Protocol) 技能集成
提供标准化的金融数据接口
"""

import json
import sys
from data_api import FinancialDataAPI, FinnhubAPI, TwelveDataAPI, AlphaVantageAPI, TavilyAPI

api = FinancialDataAPI()

def mcp_stock_quote(symbol: str):
    """获取股票实时报价"""
    data = api.get_stock_quote(symbol)
    return {
        "symbol": symbol,
        "current_price": data.get("c"),
        "change": data.get("d"),
        "change_percent": data.get("dp"),
        "high": data.get("h"),
        "low": data.get("l"),
        "open": data.get("o"),
        "previous_close": data.get("pc"),
        "timestamp": data.get("t")
    }

def mcp_stock_profile(symbol: str):
    """获取公司概况"""
    data = api.get_stock_profile(symbol)
    return {
        "symbol": symbol,
        "name": data.get("name"),
        "industry": data.get("finnhubIndustry"),
        "sector": data.get("sector"),
        "country": data.get("country"),
        "market_cap": data.get("marketCapitalization"),
        "employees": data.get("employeeTotal"),
        "website": data.get("weburl"),
        "description": data.get("description")
    }

def mcp_financial_analysis(symbol: str):
    """财务分析"""
    data = api.get_financial_data(symbol)
    overview = data.get("overview", {})
    
    return {
        "symbol": symbol,
        "valuation": {
            "pe_ratio": overview.get("PERatio"),
            "pb_ratio": overview.get("PriceToBookRatio"),
            "ps_ratio": overview.get("PriceToSalesRatioTTM"),
            "peg_ratio": overview.get("PEGRatio")
        },
        "profitability": {
            "roe": overview.get("ReturnOnEquityTTM"),
            "roa": overview.get("ReturnOnAssetsTTM"),
            "gross_margin": overview.get("GrossProfitTTM"),
            "operating_margin": overview.get("OperatingMarginTTM"),
            "profit_margin": overview.get("ProfitMargin")
        },
        "growth": {
            "revenue_growth": overview.get("QuarterlyRevenueGrowthYOY"),
            "earnings_growth": overview.get("QuarterlyEarningsGrowthYOY")
        },
        "financial_health": {
            "current_ratio": overview.get("CurrentRatio"),
            "quick_ratio": overview.get("QuickRatio"),
            "debt_to_equity": overview.get("DebtToEquityRatio")
        }
    }

def mcp_technical_analysis(symbol: str):
    """技术分析"""
    data = api.get_technical_analysis(symbol)
    
    return {
        "symbol": symbol,
        "indicators": {
            "rsi": data.get("rsi"),
            "sma": data.get("sma")
        },
        "price_history": data.get("price_history", {}).get("values", [])[:5]
    }

def mcp_search(query: str):
    """AI 搜索"""
    data = api.search_news(query)
    
    results = []
    for result in data.get("results", []):
        results.append({
            "title": result.get("title"),
            "url": result.get("url"),
            "content": result.get("content"),
            "score": result.get("score")
        })
    
    return {
        "query": query,
        "answer": data.get("answer"),
        "results": results[:5]
    }

def mcp_comprehensive_analysis(symbol: str):
    """综合分析"""
    return {
        "symbol": symbol,
        "quote": mcp_stock_quote(symbol),
        "profile": mcp_stock_profile(symbol),
        "financials": mcp_financial_analysis(symbol),
        "technicals": mcp_technical_analysis(symbol)
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_skills.py <command> [args]")
        print("Commands:")
        print("  quote <symbol>           - 获取实时报价")
        print("  profile <symbol>         - 获取公司概况")
        print("  financials <symbol>      - 财务分析")
        print("  technicals <symbol>      - 技术分析")
        print("  search <query>           - AI 搜索")
        print("  analyze <symbol>         - 综合分析")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "quote" and len(sys.argv) >= 3:
        result = mcp_stock_quote(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "profile" and len(sys.argv) >= 3:
        result = mcp_stock_profile(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "financials" and len(sys.argv) >= 3:
        result = mcp_financial_analysis(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "technicals" and len(sys.argv) >= 3:
        result = mcp_technical_analysis(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "search" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        result = mcp_search(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "analyze" and len(sys.argv) >= 3:
        result = mcp_comprehensive_analysis(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print("Unknown command or missing arguments")
        sys.exit(1)
