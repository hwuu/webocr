# ========================================
# 阶段 1: 前端构建
# ========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# 复制前端依赖配置
COPY frontend/package*.json ./

# 安装依赖
RUN npm install

# 复制前端源代码
COPY frontend/ ./

# 构建前端（生成 dist 目录）
RUN npm run build

# ========================================
# 阶段 2: Python 运行环境
# ========================================
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（PaddleOCR 需要）
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 复制前端构建产物到 static 目录
COPY --from=frontend-builder /frontend/dist ./static

# 复制后端代码
COPY backend/ ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)"

# 启动应用
CMD ["python", "app.py"]
