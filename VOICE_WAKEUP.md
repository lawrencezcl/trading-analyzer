# 语音唤醒系统配置
# Voice Wake-Up System Configuration

## 唤醒词
wake_words:
  - "龙虾"
  - "OpenClaw"
  - "贾维斯"

## 功能特性
features:
  anytime_interruption: true  # 随时打断
  always_responsive: true     # 随时响应
  continuous_listening: true  # 持续监听
  
## 响应行为
response_behavior:
  on_wake:
    - 确认唤醒
    - 等待指令
    - 保持专注
  
  on_interrupt:
    - 立即停止当前任务
    - 响应新指令
    - 保存上下文

## 状态
enabled: true
activated: 2026-02-22T18:28:00+08:00
