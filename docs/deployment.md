# Web OCR Docker 部署指南

本文档介绍如何使用 Docker 在 CentOS 7 服务器上部署 Web OCR 应用。

## 目录

- [系统要求](#系统要求)
- [安装 Docker](#安装-docker)
- [部署步骤](#部署步骤)
- [验证部署](#验证部署)
- [容器管理](#容器管理)
- [常见问题](#常见问题)

---

## 系统要求

- **操作系统**: CentOS 7 或更高版本
- **内存**: 建议 4GB 以上（PaddleOCR 模型占用约 1-2GB）
- **磁盘**: 建议 10GB 可用空间
- **网络**: 可访问 Docker Hub 和 npm 仓库

---

## 安装 Docker

### 1. 安装 Docker

```bash
# 安装依赖
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 2. （可选）配置 Docker 镜像加速

编辑 `/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

重启 Docker：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 3. （可选）添加当前用户到 docker 组

```bash
sudo usermod -aG docker $USER
# 退出并重新登录以生效
```

---

## 部署步骤

### 1. 克隆代码仓库

```bash
# 克隆项目
git clone https://github.com/hwuu/webocr.git
cd webocr
```

### 2. 构建 Docker 镜像

```bash
# 构建镜像（首次构建约需 5-10 分钟）
docker build -t webocr:latest .
```

构建过程说明：
- **阶段 1**: 使用 Node.js 构建前端（生成静态文件）
- **阶段 2**: 安装 Python 依赖和 PaddleOCR 模型
- **模型预下载**: 构建时自动下载 OCR 模型（约 18MB），无需运行时联网

### 3. 运行容器

```bash
# 运行容器（映射到 80 端口）
docker run -d \
  --name webocr \
  -p 80:5000 \
  --restart unless-stopped \
  webocr:latest
```

**参数说明**：
- `-d`: 后台运行
- `--name webocr`: 容器名称
- `-p 80:5000`: 将容器的 5000 端口映射到宿主机的 80 端口
- `--restart unless-stopped`: 自动重启策略

### 4. （可选）运行在其他端口

如果 80 端口被占用，可以使用其他端口：

```bash
docker run -d \
  --name webocr \
  -p 8080:5000 \
  --restart unless-stopped \
  webocr:latest
```

---

## 验证部署

### 1. 检查容器状态

```bash
docker ps
```

应该看到类似输出：
```
CONTAINER ID   IMAGE           STATUS         PORTS                  NAMES
xxxxx          webocr:latest   Up 2 minutes   0.0.0.0:80->5000/tcp   webocr
```

### 2. 检查健康状态

```bash
# 查看容器日志
docker logs webocr

# 测试健康检查接口
curl http://localhost:80/health
```

预期输出：
```json
{
  "status": "ok",
  "service": "Web OCR",
  "max_workers": 10
}
```

### 3. 访问 Web 界面

在浏览器中打开：
```
http://服务器IP/
```

或
```
http://服务器IP:8080/  （如果使用了 8080 端口）
```

---

## 容器管理

### 查看容器日志

```bash
# 查看最新日志
docker logs webocr

# 实时查看日志
docker logs -f webocr

# 查看最近 100 行日志
docker logs --tail 100 webocr
```

### 停止容器

```bash
docker stop webocr
```

### 启动容器

```bash
docker start webocr
```

### 重启容器

```bash
docker restart webocr
```

### 删除容器

```bash
# 停止并删除
docker stop webocr
docker rm webocr
```

### 更新应用

```bash
# 1. 拉取最新代码
cd webocr
git pull

# 2. 重新构建镜像
docker build -t webocr:latest .

# 3. 停止并删除旧容器
docker stop webocr
docker rm webocr

# 4. 启动新容器
docker run -d \
  --name webocr \
  -p 80:5000 \
  --restart unless-stopped \
  webocr:latest
```

---

## 常见问题

### 0. 离线环境部署

**问题**: 服务器无法连接外网，OCR 模型能否正常工作？

**解决**: 本项目已内置模型预下载机制：
- 所有 OCR 模型（约 18MB）在 `docker build` 时下载并打包到镜像中
- 运行时无需联网，可在完全离线环境中使用
- 模型包括：文本检测模型、文本识别模型、文本方向分类器

### 1. 构建时出现网络错误

**问题**: npm install 或 pip install 失败

**解决**:
- 配置 Docker 镜像加速（见上文）
- 使用 npm 镜像：在 `frontend/package.json` 之前添加 `.npmrc`：
  ```
  registry=https://registry.npmmirror.com
  ```
- 使用 pip 镜像：在 Dockerfile 中修改 pip 安装命令：
  ```dockerfile
  RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  ```

### 2. 容器启动后立即退出

**问题**: `docker ps` 看不到容器

**解决**:
```bash
# 查看容器日志
docker logs webocr

# 查看所有容器（包括已停止的）
docker ps -a
```

常见原因：
- 端口被占用：修改端口映射
- 依赖缺失：检查 Dockerfile 中的系统依赖安装

### 3. 访问 Web 界面显示 502 Bad Gateway

**问题**: Nginx 显示 502 错误

**解决**: 本项目不使用 Nginx，直接访问 Flask 服务。如果看到 502，可能是：
- 容器未正常启动：`docker logs webocr`
- 端口映射错误：检查 `-p` 参数

### 4. OCR 识别超时或失败

**问题**: 上传图片后识别超时

**解决**:
- 检查容器内存：`docker stats webocr`
- PaddleOCR 首次运行会下载模型（较慢），等待模型下载完成
- 检查日志：`docker logs -f webocr`

### 5. 如何限制容器资源使用

```bash
docker run -d \
  --name webocr \
  -p 80:5000 \
  --memory="4g" \
  --cpus="2.0" \
  --restart unless-stopped \
  webocr:latest
```

---

## 架构说明

### Docker 单容器架构

```
┌──────────────────────────────────┐
│      Docker 容器 (端口 5000)      │
│  ┌────────────────────────────┐  │
│  │   Flask 应用               │  │
│  │   ├─ /           (前端)    │  │
│  │   ├─ /assets/*   (静态)    │  │
│  │   ├─ /api/ocr    (OCR)     │  │
│  │   └─ /health     (健康)    │  │
│  │                            │  │
│  │   PaddleOCR 服务           │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
         │
         │ 端口映射
         ▼
    宿主机 80 端口
```

### 构建流程

```
1. Node.js 镜像
   ├─ npm install
   └─ npm run build  → dist/

2. Python 镜像
   ├─ 安装系统依赖
   ├─ 复制 dist/ → static/
   ├─ pip install
   └─ 启动 Flask
```

---

## 性能优化建议

### 1. 镜像大小优化

当前镜像大小约 2-3GB（包含 PaddleOCR 模型）。如果需要优化：
- 使用 `python:3.10-slim` 已经是较小的镜像
- PaddleOCR 模型必需，无法删除

### 2. 并发处理

默认配置：`MAX_WORKERS=10`（见 `backend/config.py`）

根据服务器资源调整：
- 修改 `backend/config.py`
- 或通过环境变量：
  ```bash
  docker run -d \
    --name webocr \
    -p 80:5000 \
    -e MAX_WORKERS=20 \
    webocr:latest
  ```

### 3. 日志管理

Docker 日志可能占用磁盘空间，建议配置日志轮转：

```bash
docker run -d \
  --name webocr \
  -p 80:5000 \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  webocr:latest
```

---

## 安全建议

### 1. 防火墙配置

```bash
# 只允许特定 IP 访问（如果需要）
sudo firewall-cmd --zone=public --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" port port="80" protocol="tcp" accept' --permanent
sudo firewall-cmd --reload
```

### 2. HTTPS 配置

生产环境建议使用 Nginx 反向代理并配置 SSL 证书：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 技术支持

- 项目主页: https://github.com/hwuu/webocr
- 问题反馈: https://github.com/hwuu/webocr/issues
- 使用指南: https://github.com/hwuu/webocr/blob/main/docs/user_manual.md

---

**文档版本**: 1.0.0
**更新时间**: 2025-11-20
