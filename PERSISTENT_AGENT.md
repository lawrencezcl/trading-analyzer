# 持久化代理守护进程配置
# Persistent Agent Daemon Configuration

## 守护进程设置
daemon:
  enabled: true
  auto_start: true
  auto_restart: true
  crash_recovery: true
  
## 运行模式
mode: 24x7
status: active

## 监控机制
monitoring:
  health_check: enabled
  heartbeat: enabled
  crash_detection: enabled
  auto_recovery: enabled

## 启动策略
startup:
  on_boot: auto
  on_crash: restart
  max_retries: unlimited
  backoff_strategy: exponential

## 服务承诺
- 24小时持续运行
- 崩溃自动重启
- 开机自动启动
- 永不掉线
