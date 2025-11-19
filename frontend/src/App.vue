<template>
  <div id="app">
    <div class="app-container">
      <!-- 上传视图（初始状态 - 全屏） -->
      <div v-if="!hasImage" class="upload-view">
        <UploadArea @upload="handleFileSelected" />
      </div>

      <!-- 识别视图（选择图片后 - 左右布局） -->
      <div v-else class="main-section">
        <!-- 左侧：图片预览 -->
        <div class="left-panel">
          <ImagePreview
            :image-url="imageUrl"
            :file-name="fileName"
            :file-size="fileSize"
            :ocr-result="ocrResult"
            :highlight-index="highlightIndex"
          />
        </div>

        <!-- 右侧：结果展示 -->
        <div class="right-panel">
          <ResultDisplay
            :result="ocrResult"
            :loading="loading"
            :loading-text="loadingText"
            @clear="handleClear"
            @highlight="handleHighlight"
          />
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="app-footer">
      <div class="footer-content">
        <span>Web OCR v1.0.0</span>
        <span class="separator">|</span>
        <a href="https://github.com/hwuu/webocr/blob/main/docs/user_manual.md" target="_blank" rel="noopener noreferrer">使用指南</a>
        <span class="separator">|</span>
        <a href="https://github.com/hwuu/webocr" target="_blank" rel="noopener noreferrer">项目主页</a>
      </div>
    </div>

    <!-- 确认对话框 -->
    <el-dialog
      v-model="showConfirmDialog"
      title="确认识别"
      width="60%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      @open="handleDialogOpen"
    >
      <div class="confirm-dialog-content">
        <div class="preview-image-container">
          <img :src="previewImageUrl" alt="预览图片" />
        </div>
        <div class="file-info">
          <p><strong>文件名：</strong>{{ previewFileName }}</p>
          <p><strong>大小：</strong>{{ previewFileSize }}</p>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleConfirm" autofocus>
            开始识别
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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

// 预览对话框状态
const showConfirmDialog = ref(false)
const previewImageUrl = ref('')
const previewFileName = ref('')
const previewFileSize = ref('')
const pendingFile = ref(null)

// OCR 结果和加载状态
const ocrResult = ref({ plain_text: '', detailed: [] })
const loading = ref(false)
const loadingText = ref('正在识别中，请稍候...')

// 高亮索引（用于边界框高亮）
const highlightIndex = ref(-1)

// 是否已选择图片
const hasImage = computed(() => !!imageUrl.value)

/**
 * 格式化文件大小
 */
const formatFileSize = (size) => {
  if (!size) return '-'
  const kb = size / 1024
  if (kb < 1024) {
    return `${kb.toFixed(2)} KB`
  }
  const mb = kb / 1024
  return `${mb.toFixed(2)} MB`
}

/**
 * 处理文件选择（显示确认对话框）
 */
const handleFileSelected = (file) => {
  pendingFile.value = file
  previewImageUrl.value = URL.createObjectURL(file)
  previewFileName.value = file.name
  previewFileSize.value = formatFileSize(file.size)
  showConfirmDialog.value = true
}

/**
 * 对话框打开后，聚焦到确认按钮
 */
const handleDialogOpen = () => {
  // Element Plus 会自动处理 autofocus
}

/**
 * 取消识别
 */
const handleCancel = () => {
  showConfirmDialog.value = false
  // 释放预览 URL
  if (previewImageUrl.value) {
    URL.revokeObjectURL(previewImageUrl.value)
  }
  previewImageUrl.value = ''
  previewFileName.value = ''
  previewFileSize.value = ''
  pendingFile.value = null
}

/**
 * 确认识别
 */
const handleConfirm = async () => {
  const file = pendingFile.value
  if (!file) return

  // 关闭对话框
  showConfirmDialog.value = false

  // 设置图片信息（显示识别视图）
  imageUrl.value = previewImageUrl.value
  fileName.value = previewFileName.value
  fileSize.value = file.size

  try {
    // 清空之前的结果
    ocrResult.value = { plain_text: '', detailed: [] }

    // 转为 Base64
    loading.value = true
    loadingText.value = '正在准备图片...'

    const base64 = await fileToBase64(file)

    // 调用 OCR API
    loadingText.value = '正在识别中，请稍候...'

    const result = await ocrRecognize(base64)

    // 显示结果
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
 * 清除图片和结果（返回上传视图）
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
  highlightIndex.value = -1

  ElMessage.info('已清除')
}

/**
 * 设置高亮索引
 */
const handleHighlight = (index) => {
  highlightIndex.value = index
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

.app-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f0f2f5;
}

/* 上传视图 - 全屏 */
.upload-view {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.upload-view :deep(.upload-area) {
  flex: 1;
}

/* 识别视图 - 左右布局 */
.main-section {
  flex: 1;
  display: flex;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.left-panel,
.right-panel {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.left-panel {
  flex: 2;
}

.right-panel {
  flex: 1;
}

/* Footer 样式 */
.app-footer {
  flex-shrink: 0;
  padding: 8px 20px;
  background-color: #f0f2f5;
  border-top: 1px solid #e4e7ed;
}

.footer-content {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.footer-content .separator {
  color: #dcdfe6;
}

.footer-content a {
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-content a:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 确认对话框样式 */
.confirm-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-image-container {
  width: 100%;
  min-height: 50vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.preview-image-container img {
  max-width: 100%;
  max-height: 50vh;
  object-fit: contain;
  border-radius: 4px;
}

.file-info {
  padding: 10px 0;
}

.file-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

.file-info strong {
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 隐藏图片预览器的旋转按钮 */
.el-image-viewer__btn .el-icon-refresh-left,
.el-image-viewer__btn .el-icon-refresh-right,
.el-image-viewer__actions__inner .is-first + .el-image-viewer__actions__divider,
.el-image-viewer__actions__inner svg[class*="refresh"],
.el-image-viewer__actions__inner i[class*="refresh"] {
  display: none !important;
}

/* 通过 SVG 内容隐藏旋转按钮 */
.el-image-viewer__actions__inner > *:nth-child(6),
.el-image-viewer__actions__inner > *:nth-child(7) {
  display: none !important;
}
</style>
