# Paddle.js 前端 OCR 调研报告

## 测试时间
2025-11-19

## 测试包
- **包名**: `antdigital-paddlejs-ocr`
- **版本**: 1.0.0
- **发布时间**: 2024-07-23
- **维护方**: 蚂蚁集团（阿里巴巴）

## ✅ 好消息

1. **包可以安装**: npm 安装成功，无依赖冲突
2. **有 TypeScript 支持**: 提供类型定义文件
3. **API 简洁**: 只需两步 - init + recognize
4. **支持 Web Worker**: 不会阻塞 UI 线程
5. **返回边界框**: 与现有功能兼容

## ❌ 发现的问题

### 1. **需要自己提供模型文件**（最大问题）

包**不包含**模型文件，需要自行准备：
- 检测模型（det）
- 识别模型（rec）
- 字符集文件（ocrChars）

**API 示例：**
```javascript
import { init, recognize } from 'antdigital-paddlejs-ocr';

await init({
  detModel: 'https://你的CDN/det_model.json',  // ❌ 需要自己托管
  recModel: 'https://你的CDN/rec_model.json',  // ❌ 需要自己托管
  ocrChars: '字符集文本'                         // ❌ 需要准备
});

const result = await recognize(imageBlob);
// { text: ['文本数组'], points: [边界框] }
```

### 2. **模型文件获取困难**

需要完成以下步骤才能使用：
1. 下载 PaddleOCR 官方模型
2. 使用 `paddlejs-converter` 转换为 Web 格式
3. 托管到静态服务器或 CDN
4. 配置 CORS 允许跨域

**预估模型大小：**
- 检测模型：2-4 MB
- 识别模型：2-4 MB
- **总计：4-8 MB** 首次加载

### 3. **文档缺失**

- README 只有 11 行
- 没有使用示例
- 没有说明如何获取模型

## 📊 与 Tesseract.js 对比

| 特性 | antdigital-paddlejs-ocr | Tesseract.js |
|------|------------------------|--------------|
| 安装 | ✅ 简单 | ✅ 简单 |
| 模型获取 | ❌ 需要自己转换+托管 | ✅ 官方 CDN 直接用 |
| 文档 | ❌ 几乎没有 | ✅ 完善 |
| 准确率 | ✅ 高（PaddleOCR） | ⚠️ 中等 |
| 速度 | ⚠️ 未知（需测试） | ⚠️ 3-10秒/张 |
| 中文支持 | ✅ 原生支持 | ✅ 支持 |

## 🎯 结论与建议

### 方案 A：使用 Tesseract.js（推荐）
**理由：**
- ✅ 开箱即用，无需准备模型
- ✅ 文档完善，社区活跃
- ✅ 3 行代码即可运行
- ⚠️ 准确率稍低，但可接受

**代码示例：**
```bash
npm install tesseract.js
```

```javascript
import Tesseract from 'tesseract.js';

const worker = await Tesseract.createWorker('chi_sim');
const { data } = await worker.recognize(image);
console.log(data.text); // 识别结果
console.log(data.words); // 带边界框
```

### 方案 B：保留服务器模式 + 添加 Tesseract.js 本地模式
**混合架构：**
```
用户设置
├── 本地模式（Tesseract.js）  ← 隐私优先，速度慢
└── 服务器模式（PaddleOCR）   ← 速度快，准确率高
```

**优点：**
- ✅ 满足隐私需求
- ✅ 灵活选择
- ✅ 降低技术风险

### 方案 C：深度投入 Paddle.js（不推荐）
**需要做：**
1. 学习 paddlejs-converter 工具
2. 转换模型（可能遇到各种坑）
3. 配置模型托管（CDN / 静态服务器）
4. 处理 CORS 问题
5. 测试性能和准确率

**预估工作量：** 1-3 天

**风险：**
- 转换可能失败
- 性能不理想
- 模型文件太大影响加载

## 💡 最终建议

**立即可行方案：**
实现混合模式（服务器 + Tesseract.js），步骤：

1. **安装 Tesseract.js**（10分钟）
2. **添加"模式切换"开关**（30分钟）
3. **实现本地识别逻辑**（1小时）
4. **测试并优化**（1小时）

**总计：~3 小时** 即可完成

---

## 下一步行动

请选择：
1. ✅ **实现混合模式（Tesseract.js + 服务器）** ← 推荐
2. ⏸️ **暂时保持现状，等 Paddle.js 生态成熟**
3. ❌ **深入研究 Paddle.js 模型转换**（风险高）

需要我帮你实现方案 1 吗？
