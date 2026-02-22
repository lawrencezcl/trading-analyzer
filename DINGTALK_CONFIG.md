# 钉钉 DingTalk 配置
# 配置时间: 2026-02-22

## 配置信息
- **Client ID (AppKey):** ding46qnowlnrkwzmxbx
- **Client Secret (AppSecret):** R353LOIGelofXi9i_UTrMUd8aIs2F5cKNhWFigW2Dc9er0SoZYyAxSANxFqDs1HY
- **Gateway Token:** 已配置
- **会话超时:** 30分钟
- **状态:** 已配置

## 钉钉开放平台设置
1. 访问 https://open.dingtalk.com
2. 进入应用开发 → 企业内部开发 → 找到应用
3. 添加机器人能力，消息接收模式选择 **Stream 模式**
4. 开通权限:
   - Card.Streaming.Write
   - Card.Instance.Write
   - qyapi_robot_sendmsg
5. 发布应用

## 使用方式
- 在钉钉中 @机器人 发送消息
- 支持 AI Card 流式响应
- 发送 /new 或 "新会话" 清空对话历史
