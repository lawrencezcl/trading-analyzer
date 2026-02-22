# 每日自动总结任务
# Daily Summary Cron Job

## 任务说明
每天自动执行以下操作：
1. 总结当日所有对话
2. 提取新的用户偏好
3. 更新习惯模式
4. 记录重要决策
5. 更新用户画像
6. 生成学习报告

## 执行时间
cron_schedule: "0 23 * * *"
# 每天晚上 23:00 执行

## 输出位置
summary_output: memory/daily-summary-YYYY-MM-DD.md
profile_update: knowledge/USER_PROFILE.yaml
