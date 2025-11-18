# Web OCR 技术方案设计文档 v1.0

## 一、整体架构

**技术栈**：
- 后端：Flask + PaddleOCR + ThreadPoolExecutor
- 前端：Vue 3 + Vite + Element Plus + Axios
- 上传方式：Base64 编码
- 部署：内网 HTTP 服务

**页面布局**：
```
┌─────────────────────────────────────────────┐
│              上传区域（顶部）                │
│  [点击上传] [拖拽区域] [剪贴板提示]         │
├──────────────────┬──────────────────────────┤
│                  │                          │
│    图片预览      │      结果展示区域        │
│   (左半边)       │   [纯文本] [完整结果]    │
│                  │   [复制按钮]             │
│                  │                          │
│                  │                          │
└──────────────────┴──────────────────────────┘
```

---

## 二、文件结构

```
webocr/
├── backend/
│   ├── app.py                    # Flask 应用主文件
│   ├── ocr_service.py            # OCR 服务封装
│   ├── config.py                 # 配置文件
│   ├── requirements.txt          # 依赖清单
│   ├── logs/                     # 日志目录
│   │   └── .gitkeep
│   └── tests/
│       ├── test_ocr_service.py   # OCR 服务单元测试
│       └── test_concurrent.py    # 并发控制测试
├── frontend/
│   ├── src/
│   │   ├── App.vue               # 主应用（左右布局容器）
│   │   ├── components/
│   │   │   ├── UploadArea.vue    # 上传区域组件
│   │   │   ├── ImagePreview.vue  # 图片预览组件（左侧）
│   │   │   └── ResultDisplay.vue # 结果展示组件（右侧）
│   │   ├── api/
│   │   │   └── ocr.js            # OCR API 封装
│   │   ├── utils/
│   │   │   ├── validator.js      # 文件验证
│   │   │   └── clipboard.js      # 剪贴板工具
│   │   └── main.js
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env.development
├── docs/
│   └── design.md                 # 本设计文档
├── README.md
├── CLAUDE.md
└── .gitignore
```

---

## 三、核心技术实现

### 3.1 并发控制逻辑

**实现方案**：使用 `Semaphore(10)` + `ThreadPoolExecutor(max_workers=10)`

**流程**：
```
请求到达 POST /api/ocr
├── 解析 Base64 图片
├── 验证文件大小、格式
├── 尝试获取信号量（非阻塞）
│   ├── 成功：提交到线程池处理
│   │   ├── 调用 OCR 识别
│   │   ├── 返回结果（200）
│   │   └── 释放信号量
│   └── 失败：立即返回 429
```

**关键代码**：
```python
semaphore = threading.Semaphore(10)
executor = ThreadPoolExecutor(max_workers=10)

@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    # 1. 解析和验证
    image_bytes = base64.b64decode(request.json['image'])
    validate_image(image_bytes)

    # 2. 并发控制
    if not semaphore.acquire(blocking=False):
        return jsonify({"error": "服务繁忙，请稍后重试"}), 429

    try:
        future = executor.submit(ocr_service.recognize, image_bytes)
        result = future.result(timeout=60)
        return jsonify(result), 200
    finally:
        semaphore.release()
```

---

### 3.2 图片上传与验证

**前端验证**（快速失败）：
- 文件类型检查：`image/jpeg`, `image/png`, `image/bmp`
- 文件大小检查：<= 10MB

**后端二次验证**：
```python
def validate_image(image_bytes):
    # 1. 大小验证
    if len(image_bytes) > 10 * 1024 * 1024:
        raise ValueError("文件大小超过 10MB")

    # 2. 格式验证（使用 Pillow）
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.format.lower() not in ['jpeg', 'jpg', 'png', 'bmp']:
            raise ValueError("不支持的图片格式")
    except Exception:
        raise ValueError("无效的图片文件")
```

---

### 3.3 OCR 结果格式化

**PaddleOCR 原始输出**：
```python
[
  [
    [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],  # 坐标
    ("识别文本", 0.98)                      # 文本 + 置信度
  ],
  ...
]
```

**转换为标准格式**：
```python
def recognize(self, image_bytes):
    img_array = np.array(Image.open(io.BytesIO(image_bytes)))
    result = self.ocr.ocr(img_array, cls=True)

    if not result or not result[0]:
        return {"plain_text": "", "detailed": []}

    plain_text = "\n".join([line[1][0] for line in result[0]])
    detailed = [
        {
            "text": line[1][0],
            "confidence": round(line[1][1], 4),
            "box": line[0]
        }
        for line in result[0]
    ]

    return {"plain_text": plain_text, "detailed": detailed}
```

---

### 3.4 前端三种上传方式

**方式 1：点击选择**
```vue
<el-upload
  :before-upload="handleBeforeUpload"
  :auto-upload="false">
  <el-button>点击上传</el-button>
</el-upload>
```

**方式 2：拖拽上传**
```vue
<div
  @drop.prevent="handleDrop"
  @dragover.prevent
  class="drop-zone">
  拖拽图片到此处
</div>
```

**方式 3：剪贴板粘贴**
```javascript
mounted() {
  document.addEventListener('paste', this.handlePaste)
}

handlePaste(e) {
  const items = e.clipboardData.items
  for (let item of items) {
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile()
      this.processFile(file)
    }
  }
}
```

---

### 3.5 Base64 编码处理

**前端：File → Base64**
```javascript
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      // 去掉 data:image/xxx;base64, 前缀
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}
```

**后端：Base64 → bytes**
```python
import base64
image_bytes = base64.b64decode(image_b64)
```

---

### 3.6 日志记录策略

**配置**：
```python
logging.basicConfig(
    filename='logs/ocr.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
```

**记录内容**（不包含图片和识别结果）：
- 请求时间、处理耗时
- 图片尺寸（宽x高）、文件大小（KB）
- 成功/失败状态
- 错误类型（并发限制、格式错误、超时等）

**示例**：
```
2025-01-18 10:30:15 | INFO | OCR Success | Size: 245KB | Dimension: 800x600 | Time: 3.2s | Lines: 15
2025-01-18 10:30:20 | ERROR | OCR Failed | Error: ConcurrentLimit | Message: 服务繁忙
```

---

## 四、实施步骤

### Phase 1：后端核心实现

#### 步骤 1.1：搭建 Flask 基础框架
- 创建 `backend/app.py`、`backend/config.py`、`backend/requirements.txt`
- 配置 CORS、请求体大小限制
- 实现 `/health` 健康检查接口

#### 步骤 1.2：集成 PaddleOCR
- 创建 `backend/ocr_service.py`
- 封装 `OCRService` 类
- 实现 `recognize()` 方法

#### 步骤 1.3：实现并发控制与 OCR 接口
- 实现 POST `/api/ocr` 接口
- 集成并发控制逻辑
- 实现日志记录

---

### Phase 2：前端基础实现

#### 步骤 2.1：初始化 Vue 项目
- 创建 Vite 项目
- 安装 Element Plus、Axios
- 配置开发环境

#### 步骤 2.2：实现 API 封装层
- 创建 `src/api/ocr.js`
- 封装 Axios 实例和错误处理

#### 步骤 2.3：实现工具函数
- 创建 `src/utils/validator.js`
- 创建 `src/utils/clipboard.js`

#### 步骤 2.4：实现上传区域组件
- 创建 `src/components/UploadArea.vue`
- 实现三种上传方式

#### 步骤 2.5：实现图片预览组件
- 创建 `src/components/ImagePreview.vue`

#### 步骤 2.6：实现结果展示组件
- 创建 `src/components/ResultDisplay.vue`
- 实现纯文本和完整结果两个页签
- 实现复制功能

#### 步骤 2.7：组装主应用
- 修改 `src/App.vue`
- 实现左右布局
- 串联所有子组件

---

### Phase 3：前后端联调与优化

#### 步骤 3.1：前后端联调
- 同时启动前后端服务
- 测试完整流程

#### 步骤 3.2：错误提示优化
- 完善各类错误的用户提示

#### 步骤 3.3：样式优化
- 调整界面样式和布局

---

### Phase 4：测试与文档

#### 步骤 4.1：后端单元测试
- 创建测试用例

#### 步骤 4.2：集成测试与压力测试
- 并发压力测试
- 稳定性测试

#### 步骤 4.3：编写 README 文档
- 部署和使用说明

---

## 五、测试要点

### 后端测试

**OCR 功能测试**：
- ✅ 正常图片：中文、英文、混合文本
- ✅ 支持格式：JPG、PNG、BMP、JPEG
- ✅ 异常图片：损坏文件、纯黑图片、空白图片
- ✅ 返回格式：`plain_text` 和 `detailed` 字段完整性

**并发控制测试**：
- ✅ 并发数 ≤ 10：所有请求正常响应（HTTP 200）
- ✅ 并发数 > 10：超出部分返回 429 错误
- ✅ 并发任务完成后，新请求能正常获取槽位

**边界条件测试**：
- ✅ 文件大小：9.9MB（通过）、10.1MB（拒绝）
- ✅ 非法格式：PDF、TXT 文件（拒绝）
- ✅ 空文件、0 字节文件
- ✅ 超时处理

**日志验证**：
- ✅ 日志文件正常写入
- ✅ 包含关键信息（时间、耗时、错误类型）
- ✅ 不包含敏感信息

---

### 前端测试

**上传功能测试**：
- ✅ 点击选择文件
- ✅ 拖拽上传
- ✅ 剪贴板粘贴
- ✅ 格式验证
- ✅ 大小验证

**结果展示测试**：
- ✅ 默认显示"纯文本"页签
- ✅ 纯文本页签格式正确
- ✅ 完整结果页签表格显示正确
- ✅ 复制功能正常

**错误处理测试**：
- ✅ 429 错误提示
- ✅ 网络错误提示
- ✅ 超时错误提示
- ✅ 500 错误提示

---

### 集成测试

**端到端流程**：
- ✅ 上传图片 → 等待识别 → 查看结果

**并发压力测试**：
- ✅ 模拟 20 个并发请求
- ✅ 验证前 10 个成功，后 10 个返回 429

**稳定性测试**：
- ✅ 连续处理 100 张图片，无内存泄漏
- ✅ 长时间运行无崩溃

---

## 六、部署说明

### 开发环境启动

**后端**：
```bash
cd backend
pip install -r requirements.txt
python app.py  # 默认端口 5000
```

**前端**：
```bash
cd frontend
npm install
npm run dev  # 默认端口 5173
```

---

### 生产环境部署（内网）

**后端**：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**前端**：
```bash
npm run build
# 将 dist/ 目录部署到 Nginx 或直接用 Flask 托管
```

---

## 七、技术风险与解决方案

| 风险点 | 影响 | 解决方案 |
|--------|------|----------|
| PaddleOCR 首次加载慢 | 首次启动耗时长 | 提前下载模型到 `~/.paddleocr/` |
| CPU 模式下单张图片处理慢 | 用户等待时间长 | 前端显示处理进度提示 |
| Base64 上传大文件时请求体过大 | 可能触发服务器限制 | Flask 配置 `MAX_CONTENT_LENGTH = 15MB` |
| 线程池长时间占用 | 后续请求延迟 | 设置单个 OCR 任务超时（60 秒） |

---

## 八、功能特性总结

✅ 基于 PaddleOCR 的 CPU 模式识别
✅ 三种上传方式（点击、拖拽、剪贴板）
✅ 左右布局（图片预览 + 结果展示）
✅ 纯文本 + 完整结果两个页签
✅ 复制纯文本功能
✅ 10 并发限制，超出返回"服务繁忙"
✅ 10MB 文件大小限制
✅ 支持 JPG/PNG/BMP 等格式
✅ 日志记录（不存储识别结果）
✅ 内网 HTTP 部署

---

**文档版本**：v1.0
**创建日期**：2025-01-18
**最后更新**：2025-01-18
