# ========================================
# 阶段 1: 前端构建
# ========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# 替换 Alpine 源为阿里云镜像（加速国内构建）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 复制前端依赖配置
COPY frontend/package*.json ./

# 安装依赖（使用淘宝 npm 镜像）
RUN npm install --registry=https://registry.npmmirror.com

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

# 替换为阿里云 Debian 源（解决官方源超时问题）
RUN echo "deb http://mirrors.aliyun.com/debian/ bookworm main non-free-firmware contrib" > /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ bookworm-updates main non-free-firmware contrib" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ bookworm-backports main non-free-firmware contrib" >> /etc/apt/sources.list

# 安装 GPG 密钥和证书工具（临时禁用 GPG 验证以解决冷启动问题）
RUN apt-get update -o Acquire::AllowInsecureRepositories=true \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 导入 Debian 官方 GPG 密钥
RUN mkdir -p /etc/apt/keyrings \
    && gpg --keyserver keyserver.ubuntu.com --recv-keys 6ED0E7B82643E131 \
    && gpg --keyserver keyserver.ubuntu.com --recv-keys 78DBA3BC47EF2265 \
    && gpg --keyserver keyserver.ubuntu.com --recv-keys F8D2585B8783D481 \
    && gpg --export 6ED0E7B82643E131 78DBA3BC47EF2265 F8D2585B8783D481 > /etc/apt/trusted.gpg.d/debian-archive.gpg

# 安装系统依赖（现在可以正常验证 GPG 签名了）
RUN apt-get update -o Acquire::http::Timeout=30 -o Acquire::Retries=3 \
    && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 复制前端构建产物到 static 目录
COPY --from=frontend-builder /frontend/dist ./static

# 复制后端代码
COPY backend/ ./

# 安装 Python 依赖（使用阿里云 PyPI 镜像）
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

# 设置 PaddlePaddle 环境变量（禁用 MKL-DNN，提高 CPU 兼容性）
ENV FLAGS_use_mkldnn=false
ENV CPU_NUM=1

# 预下载 PaddleOCR 模型到镜像中（避免运行时联网下载）
# 模型下载到父级目录，解压后会自动创建正确的子目录
RUN mkdir -p /root/.paddleocr/whl/det/ch \
    && mkdir -p /root/.paddleocr/whl/rec/ch \
    && mkdir -p /root/.paddleocr/whl/cls \
    && cd /root/.paddleocr/whl/det/ch \
    && wget -q https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar \
    && tar -xf ch_PP-OCRv4_det_infer.tar \
    && rm ch_PP-OCRv4_det_infer.tar \
    && cd /root/.paddleocr/whl/rec/ch \
    && wget -q https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_infer.tar \
    && tar -xf ch_PP-OCRv4_rec_infer.tar \
    && rm ch_PP-OCRv4_rec_infer.tar \
    && cd /root/.paddleocr/whl/cls \
    && wget -q https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar \
    && tar -xf ch_ppocr_mobile_v2.0_cls_infer.tar \
    && rm ch_ppocr_mobile_v2.0_cls_infer.tar

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)"

# 启动应用
CMD ["python", "app.py"]
