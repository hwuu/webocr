<template>
  <div class="upload-area">
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :show-file-list="false"
      :on-change="handleFileChange"
      accept="image/jpeg,image/png,image/bmp"
      drag
    >
      <div class="upload-content">
        <el-icon class="upload-icon"><Upload /></el-icon>
        <div class="upload-text">
          <div class="main-text">点击或拖拽图片到此处上传</div>
          <div class="sub-text">支持 JPG/PNG/BMP 格式，文件大小不超过 10MB</div>
          <div class="sub-text tip">提示：也可以使用 Ctrl+V 粘贴剪贴板中的图片</div>
        </div>
      </div>
    </el-upload>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { validateFile } from '@/utils/validator'
import { getImageFromClipboard } from '@/utils/clipboard'

const emit = defineEmits(['upload'])

const uploadRef = ref(null)

/**
 * 处理文件变化（选择文件后触发）
 */
const handleFileChange = (uploadFile) => {
  // 获取原始文件对象
  const file = uploadFile.raw

  const { valid, message } = validateFile(file)

  if (!valid) {
    ElMessage.error(message)
    return
  }

  // 触发上传事件
  emit('upload', file)
}

/**
 * 处理剪贴板粘贴
 */
const handlePaste = (event) => {
  const file = getImageFromClipboard(event)

  if (file) {
    const { valid, message } = validateFile(file)

    if (!valid) {
      ElMessage.error(message)
      return
    }

    ElMessage.success('已检测到剪贴板图片')
    emit('upload', file)
  }
}

onMounted(() => {
  // 监听粘贴事件
  document.addEventListener('paste', handlePaste)
})

onUnmounted(() => {
  // 移除粘贴事件监听
  document.removeEventListener('paste', handlePaste)
})
</script>

<style scoped>
.upload-area {
  width: 100%;
  padding: 20px;
}

.upload-content {
  padding: 40px;
  text-align: center;
}

.upload-icon {
  font-size: 60px;
  color: #409eff;
  margin-bottom: 20px;
}

.upload-text {
  color: #606266;
}

.main-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 10px;
}

.sub-text {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.sub-text.tip {
  margin-top: 16px;
  color: #67c23a;
  font-weight: 500;
}

:deep(.el-upload-dragger) {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  transition: all 0.3s;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
}

:deep(.el-upload-dragger.is-dragover) {
  background-color: rgba(64, 158, 255, 0.06);
  border-color: #409eff;
}
</style>
