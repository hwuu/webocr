# Web OCR - 图片文字识别系统

<div align="center">

📚 一个基于 PaddleOCR 的 Web 端图片文字识别系统

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-brightgreen.svg)](https://vuejs.org/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-2.7+-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用方法](#使用方法) • [技术栈](#技术栈)

</div>

---

## 📖 项目简介

Web OCR 是一个开箱即用的图片文字识别系统，支持中文和英文识别。通过现代化的 Web 界面，用户可以轻松上传图片并快速获取识别结果。

**主要亮点：**
- ✨ 现代化的用户界面，操作简单直观
- 🚀 基于 PaddleOCR，识别准确率高
- 📱 响应式设计，适配各种屏幕尺寸
- 🎯 多种上传方式：点击、拖拽、粘贴
- 📊 可视化结果展示，支持边界框高亮
- ⚡ 并发控制，最多支持 10 个并发请求

---

## 🎬 效果展示

### 主界面
> 💡 **提示**：将实际截图保存为 `docs/images/main-interface.png`

![主界面](docs/images/main-interface.png)

*上传界面支持点击、拖拽和 Ctrl+V 粘贴三种方式*

### 识别结果
> 💡 **提示**：将实际截图保存为 `docs/images/result-display.png`

![识别结果](docs/images/result-display.png)

*左侧显示原图和边界框，右侧显示识别结果*

### 边界框高亮
> 💡 **提示**：将实际截图保存为 `docs/images/highlight-demo.png`

![边界框高亮](docs/images/highlight-demo.png)

*鼠标悬停在结果上时，对应文本区域会高亮显示*

---

## ✨ 功能特性

### 核心功能
- 🔍 **高精度识别**：基于 PaddleOCR，支持中英文混合识别
- 📤 **多种上传方式**：
  - 点击选择文件
  - 拖拽图片到上传区域
  - 使用 `Ctrl+V` 直接粘贴剪贴板图片
- 📊 **双模式展示**：
  - **纯文本模式**：快速复制识别结果
  - **详细模式**：查看每行文本的置信度和边界框信息
- 🎨 **可视化交互**：
  - 图片预览与缩放
  - 鼠标悬停高亮对应文本区域
  - 边界框实时绘制

### 技术特性
- ⚡ **并发控制**：Semaphore + ThreadPoolExecutor，最大 10 并发
- 🛡️ **完善的错误处理**：
  - 文件格式验证（JPG/PNG/BMP）
  - 文件大小限制（≤10MB）
  - 超时控制（60 秒）
  - 友好的错误提示
- 📝 **日志系统**：UTF-8 编码，文件+控制台双输出
- 🔄 **响应式布局**：自适应窗口大小，优化各种屏幕

---

## 🛠️ 技术栈

### 后端
| 技术 | 版本 | 说明 |
|------|------|------|
| Flask | 3.0.0 | Web 框架 |
| PaddleOCR | 2.7.3 | OCR 识别引擎 |
| PaddlePaddle | 2.6.2 | 深度学习框架 |
| Flask-CORS | 4.0.0 | 跨域支持 |

### 前端
| 技术 | 版本 | 说明 |
|------|------|------|
| Vue 3 | 3.5.24 | 渐进式框架 |
| Element Plus | 2.11.8 | UI 组件库 |
| Vite | 7.2.2 | 构建工具 |
| Axios | 1.13.2 | HTTP 客户端 |

---

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 1. 克隆项目
```bash
git clone https://github.com/hwuu/webocr.git
cd webocr
```

### 2. 后端配置

#### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 启动后端服务
```bash
python app.py
```

后端服务将运行在 `http://localhost:5000`

> **⚠️ 注意**：首次运行时，PaddleOCR 会自动下载模型文件（约 10MB），请耐心等待。

### 3. 前端配置

#### 安装依赖
```bash
cd frontend
npm install
```

#### 启动开发服务器
```bash
npm run dev
```

前端服务将运行在 `http://localhost:5173`

### 4. 访问应用

打开浏览器访问 `http://localhost:5173`，即可开始使用！

---

## 📖 使用方法

### 上传图片
支持三种上传方式：

1. **点击上传**：点击上传区域，选择图片文件
2. **拖拽上传**：直接将图片拖拽到上传区域
3. **粘贴上传**：复制图片后，按 `Ctrl+V` 粘贴

### 查看结果

#### 纯文本模式
- 快速查看所有识别文本
- 一键复制到剪贴板

#### 完整结果模式
- 查看每行文本的详细信息
- 显示识别置信度（颜色标识）：
  - 🟢 绿色：置信度 ≥ 90%
  - 🟡 黄色：置信度 70% - 90%
  - 🔴 红色：置信度 < 70%
- 鼠标悬停时，左侧图片对应区域会高亮显示

### 复制结果
- **纯文本模式**：复制识别的纯文本
- **完整结果模式**：复制 JSON 格式的详细数据（包含坐标和置信度）

### 清除结果
点击右侧的"清除"按钮，返回上传界面

---

## 📁 项目结构

```
webocr/
├── backend/                 # 后端服务
│   ├── app.py              # Flask 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── logs/               # 日志文件
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   │   ├── UploadArea.vue      # 上传区域
│   │   │   ├── ImagePreview.vue    # 图片预览
│   │   │   └── ResultDisplay.vue   # 结果展示
│   │   ├── api/           # API 接口
│   │   ├── utils/         # 工具函数
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── public/
│   │   └── favicon.svg    # 网站图标
│   └── package.json       # 前端依赖
├── docs/                  # 文档
│   ├── design.md          # 技术设计文档
│   └── frontend-ocr-research.md  # 前端 OCR 调研
└── README.md              # 项目说明
```

---

## 🔧 API 文档

### OCR 识别接口

**请求：**
```http
POST /api/ocr
Content-Type: application/json

{
  "image": "base64_encoded_image_string"
}
```

**响应（成功）：**
```json
{
  "plain_text": "识别的文本内容",
  "detailed": [
    {
      "text": "单行文本",
      "confidence": 0.9876,
      "box": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    }
  ]
}
```

**响应（失败）：**
```json
{
  "error": "错误信息"
}
```

### 健康检查接口

**请求：**
```http
GET /health
```

**响应：**
```json
{
  "status": "healthy"
}
```

---

## 🗺️ 开发路线

### ✅ 已完成
- [x] 基础 OCR 识别功能
- [x] 现代化 Web 界面
- [x] 多种上传方式支持
- [x] 边界框可视化
- [x] 置信度展示
- [x] 响应式布局
- [x] 完善的错误处理

### 🔜 计划中
- [ ] 支持更多图片格式（WEBP, TIFF）
- [ ] 批量识别功能
- [ ] 结果导出（TXT, JSON, Excel）
- [ ] 识别历史记录
- [ ] 自定义识别参数
- [ ] 多语言支持（英、日、韩）
- [ ] Docker 部署支持

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发规范
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的 OCR 工具
- [Element Plus](https://element-plus.org/) - 优秀的 Vue 3 组件库
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架

---

## 📧 联系方式

- 项目主页: [https://github.com/hwuu/webocr](https://github.com/hwuu/webocr)
- 问题反馈: [Issues](https://github.com/hwuu/webocr/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by hwuu

</div>
