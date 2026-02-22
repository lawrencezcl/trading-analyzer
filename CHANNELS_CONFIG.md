# Telegram & QQ 配置记录
# 创建于: 2026-02-22

## Telegram 配置
- Bot 用户名: @jht1983_bot
- Bot Token: 8450500469:AAHQ_uqLZ0Qf1U9Ff5V-_5OHu7Arn8_2o6Y
- 状态: ✅ 已配置
- DM 策略: pairing
- 群组提及: 需要 @提及

## QQ 配置
- QQ号: 3889733681
- AppID: 102837673
- AppSecret: cIzkVH4rfUJ90rjcVPKFB85321DQet9P
- 状态: ⚠️ 待配置

### QQ 配置说明
OpenClaw 目前没有内置 QQ 频道支持。QQ 接入需要通过以下方式：

#### 方案1: 使用 go-cqhttp 桥接
1. 安装 go-cqhttp: https://github.com/Mrs4s/go-cqhttp
2. 配置 QQ 账号登录
3. 通过 HTTP API 或 WebSocket 与 OpenClaw 通信
4. 需要自定义脚本转发消息

#### 方案2: 使用 Lagrange.Core
1. 安装 Lagrange.Core: https://github.com/LagrangeDev/Lagrange.Core
2. 配置 QQ Bot 协议
3. 通过 OneBot 协议与 OpenClaw 对接

#### 方案3: 等待官方扩展
OpenClaw 社区可能在未来添加原生 QQ 支持

### 建议
目前 Telegram 已完全配置好，可以立即使用。
QQ 建议使用 go-cqhttp 方案，这是目前最稳定的 QQ Bot 协议实现。
