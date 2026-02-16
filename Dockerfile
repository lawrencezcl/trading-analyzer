# 蔡森技术分析交易信号服务
# 多阶段构建，优化镜像大小

FROM python:3.11-slim as base

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY trading_analyzer_service.py .
COPY start_service.sh .
COPY signals/ ./signals/

# 创建日志目录
RUN mkdir -p /app/logs

# 设置权限
RUN chmod +x start_service.sh

# 健康检查
HEALTHCHECK --interval=60s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 暴露端口 (用于健康检查和Web界面)
EXPOSE 8080

# 默认命令
CMD ["python3", "trading_analyzer_service.py"]
