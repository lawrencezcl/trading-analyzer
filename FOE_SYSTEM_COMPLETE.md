# 期货期权链分析专家配置完成
# Futures & Options Chain Analysis Expert Complete
# 时间: 2026-02-22 21:45

## ✅ 已完成配置

### 1. 角色定位
- 身份: 期货期权链分析专家 (FOE)
- 专长: 期权链分析、期货期限结构、波动率分析、Greeks 计算

### 2. 核心能力 (5大模块)

#### ✅ 期权链深度分析
- 期权链结构解析
- Max Pain 计算
- 持仓量 (OI) 分析
- 成交量异常识别
- Put/Call Ratio

#### ✅ 波动率专业分析
- 隐含波动率 (IV) 计算
- 波动率期限结构
- 波动率偏度 (Skew)
- 波动率微笑 (Smile)
- IV Rank / IV Percentile

#### ✅ 希腊字母分析
- Delta (方向敏感度)
- Gamma (凸性风险)
- Theta (时间衰减)
- Vega (波动率敏感度)
- Rho (利率敏感度)

#### ✅ 期货专业分析
- 期限结构 (Contango/Backwardation)
- 基差分析
- 展期成本计算
- 持仓量资金流向

#### ✅ 期权策略
- 方向性策略
- 波动率策略
- 收入策略
- 对冲策略

### 3. 分析工具

#### 核心文件
- `options_futures_analysis.py` - 期权期货分析核心
  - OptionsChainAnalyzer 类
  - FuturesAnalyzer 类
  - Max Pain 计算
  - Greeks 计算 (Black-Scholes)
  - 异常活动识别

#### 测试通过
```
✅ 最大痛点 (Max Pain): $110
✅ Put/Call Ratio: 0.97
✅ 希腊字母计算:
   - DELTA: 0.5695
   - GAMMA: 0.0357
   - THETA: -11.5216
   - VEGA: 0.2161
   - RHO: 0.1439
✅ 期限结构: CONTANGO
```

### 4. 配置文件
- `FUTURES_OPTIONS_EXPERT_CONFIG.yaml` - 角色配置
- `FUTURES_OPTIONS_EXPERT_PERSONA.md` - 系统提示词

### 5. 专业术语体系

#### 期权术语
- Options Chain, Strike, Expiration
- Implied Volatility, Open Interest
- Max Pain, Greeks (Delta, Gamma, Theta, Vega, Rho)
- IV Rank, IV Percentile

#### 期货术语
- Term Structure, Contango, Backwardation
- Basis, Roll Cost, Open Interest

#### 波动率术语
- IV, HV, Skew, Smile, Surface

## 输出标准

### 期权链分析报告
- 期权链概览
- 关键指标 (Max Pain, P/C Ratio)
- 波动率分析
- Greeks 分析
- 异常活动
- 交易建议

### 期货分析报告
- 期限结构
- 基差分析
- 展期成本
- 交易建议

## 下一步
期货期权链分析专家系统已就绪！
可以开始进行专业的期权链和期货分析。

示例请求:
- "分析 SPY 的期权链，找出 Max Pain"
- "计算当前市场的 Put/Call Ratio"
- "分析原油期货的期限结构"
- "评估某个期权策略的 Greeks 风险"
