<template>
  <div class="image-preview">
    <div v-if="imageUrl" class="preview-container">
      <div class="preview-header">
        <span class="title">图片预览</span>
        <el-button type="danger" size="small" @click="handleClear">清除</el-button>
      </div>
      <div class="preview-content">
        <img :src="imageUrl" alt="预览图片" />
      </div>
      <div class="preview-info">
        <div class="info-item">
          <span class="label">文件名：</span>
          <span class="value">{{ fileName }}</span>
        </div>
        <div class="info-item">
          <span class="label">大小：</span>
          <span class="value">{{ fileSize }}</span>
        </div>
      </div>
    </div>
    <div v-else class="empty-preview">
      <el-empty description="暂无图片" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  imageUrl: {
    type: String,
    default: ''
  },
  fileName: {
    type: String,
    default: ''
  },
  fileSize: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['clear'])

/**
 * 格式化文件大小
 */
const fileSize = computed(() => {
  if (!props.fileSize) return '-'

  const kb = props.fileSize / 1024
  if (kb < 1024) {
    return `${kb.toFixed(2)} KB`
  }

  const mb = kb / 1024
  return `${mb.toFixed(2)} MB`
})

/**
 * 清除图片
 */
const handleClear = () => {
  emit('clear')
}
</script>

<style scoped>
.image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header .title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.preview-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: auto;
  background-color: #f5f7fa;
}

.preview-content img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.preview-info {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  background-color: #fff;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  color: #909399;
  min-width: 60px;
}

.info-item .value {
  color: #606266;
  word-break: break-all;
}

.empty-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}
</style>
