<template>
  <div id="app">
    <div class="app-header">
      <h1 class="app-title">Web OCR - 图片文字识别</h1>
    </div>

    <div class="app-container">
      <!-- 上传区域（顶部） -->
      <div class="upload-section">
        <UploadArea @upload="handleUpload" />
      </div>

      <!-- 主内容区域（左右布局） -->
      <div class="main-section">
        <!-- 左侧：图片预览 -->
        <div class="left-panel">
          <ImagePreview
            :image-url="imageUrl"
            :file-name="fileName"
            :file-size="fileSize"
            @clear="handleClear"
          />
        </div>

        <!-- 右侧：结果展示 -->
        <div class="right-panel">
          <ResultDisplay
            :result="ocrResult"
            :loading="loading"
            :loading-text="loadingText"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import UploadArea from './components/UploadArea.vue'
import ImagePreview from './components/ImagePreview.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import { fileToBase64 } from './utils/validator'
import { ocrRecognize } from './api/ocr'

// 图片相关状态
const imageUrl = ref('')
const fileName = ref('')
const fileSize = ref(0)

// OCR 结果和加载状态
const ocrResult = ref({ plain_text: '', detailed: [] })
const loading = ref(false)
const loadingText = ref('正在识别中，请稍候...')

/**
 * 处理文件上传
 */
const handleUpload = async (file) => {
  try {
    // 1. 显示图片预览
    imageUrl.value = URL.createObjectURL(file)
    fileName.value = file.name
    fileSize.value = file.size

    // 2. 清空之前的结果
    ocrResult.value = { plain_text: '', detailed: [] }

    // 3. 转为 Base64
    loading.value = true
    loadingText.value = '正在准备图片...'

    const base64 = await fileToBase64(file)

    // 4. 调用 OCR API
    loadingText.value = '正在识别中，请稍候...'

    const result = await ocrRecognize(base64)

    // 5. 显示结果
    ocrResult.value = result
    loading.value = false

    if (result.plain_text) {
      ElMessage.success(`识别完成，共 ${result.detailed.length} 行文本`)
    } else {
      ElMessage.warning('未识别到文字')
    }
  } catch (error) {
    console.error('OCR 识别失败:', error)
    loading.value = false
  }
}

/**
 * 清除图片和结果
 */
const handleClear = () => {
  // 释放对象 URL
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value)
  }

  imageUrl.value = ''
  fileName.value = ''
  fileSize.value = 0
  ocrResult.value = { plain_text: '', detailed: [] }
  loading.value = false

  ElMessage.info('已清除')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', Arial, sans-serif;
}

#app {
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.app-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f0f2f5;
}

.upload-section {
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.main-section {
  flex: 1;
  display: flex;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.left-panel,
.right-panel {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
</style>
