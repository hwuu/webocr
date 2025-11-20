<template>
  <div class="result-display">
    <div v-if="hasResult" class="result-container">
      <div class="result-header">
        <span class="title">识别结果</span>
        <div class="button-group">
          <el-button type="primary" @click="handleCopy">
            复制到剪贴板
          </el-button>
          <el-button type="danger" @click="handleClear">清除</el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="result-tabs">
        <!-- 纯文本页签 -->
        <el-tab-pane label="纯文本" name="plain">
          <div class="plain-text-content">
            <el-input
              v-model="result.plain_text"
              type="textarea"
              readonly
              resize="none"
              placeholder="识别结果将显示在这里..."
            />
          </div>
        </el-tab-pane>

        <!-- 完整结果页签 -->
        <el-tab-pane label="完整结果" name="detailed">
          <div class="detailed-content">
            <el-table
              :data="result.detailed"
              stripe
              style="width: 100%"
              height="100%"
              @cell-mouse-enter="handleCellHover"
              @cell-mouse-leave="handleCellLeave"
            >
              <el-table-column type="index" label="序号" width="60" />
              <el-table-column prop="text" label="文本内容" min-width="200" />
              <el-table-column prop="confidence" label="置信度" width="100">
                <template #default="{ row }">
                  <el-tag :type="getConfidenceType(row.confidence)">
                    {{ (row.confidence * 100).toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div v-else-if="loading" class="loading-container" v-loading="loading" :element-loading-text="loadingText">
      <div style="height: 100px;"></div>
    </div>

    <div v-else class="empty-result">
      <el-empty description="上传图片后，识别结果将显示在这里" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { CopyDocument } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { copyToClipboard } from '@/utils/clipboard'

const props = defineProps({
  result: {
    type: Object,
    default: () => ({ plain_text: '', detailed: [] })
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: '正在识别中...'
  }
})

const emit = defineEmits(['clear', 'highlight'])

const activeTab = ref('plain')

/**
 * 是否有结果
 */
const hasResult = computed(() => {
  return props.result && (props.result.plain_text || props.result.detailed?.length > 0)
})

/**
 * 复制内容到剪贴板
 */
const handleCopy = () => {
  if (activeTab.value === 'plain') {
    // 纯文本页签：复制纯文本
    copyToClipboard(props.result.plain_text)
  } else {
    // 完整结果页签：复制 JSON
    const jsonData = JSON.stringify(props.result.detailed, null, 2)
    copyToClipboard(jsonData)
  }
}

/**
 * 清除图片和结果
 */
const handleClear = async () => {
  const promise = ElMessageBox.confirm(
    '确定要清除当前图片和识别结果吗？',
    '确认清除',
    {
      distinguishCancelAndClose: true,
      confirmButtonText: '是',
      cancelButtonText: '否',
      confirmButtonClass: 'confirm-button-danger',
      cancelButtonClass: 'cancel-button-primary',
      type: 'warning',
      showClose: false,
      lockScroll: true
    }
  )

  // 延迟设置焦点，确保对话框完全渲染
  const setFocus = () => {
    const cancelButton = document.querySelector('.cancel-button-primary')
    if (cancelButton) {
      cancelButton.focus()
    } else {
      // 如果还没找到，再等待一会
      setTimeout(setFocus, 50)
    }
  }
  setTimeout(setFocus, 150)

  try {
    await promise
    emit('clear')
  } catch {
    // 用户取消，不做任何操作
  }
}

/**
 * 获取置信度标签类型
 */
const getConfidenceType = (confidence) => {
  if (confidence >= 0.9) return 'success'
  if (confidence >= 0.7) return 'warning'
  return 'danger'
}

/**
 * 单元格鼠标进入
 */
const handleCellHover = (row) => {
  const index = props.result.detailed.indexOf(row)
  emit('highlight', index)
}

/**
 * 单元格鼠标离开
 */
const handleCellLeave = () => {
  emit('highlight', -1)
}
</script>

<style scoped>
.result-display {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.result-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 56px;
  padding: 0 20px;
  border-bottom: 1px solid #e4e7ed;
}

.result-header .title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.button-group {
  display: flex;
  gap: 10px;
}

/* 自定义确认对话框按钮样式 */
:global(.confirm-button-danger) {
  background-color: #f56c6c !important;
  border-color: #f56c6c !important;
  color: #fff !important;
}

:global(.confirm-button-danger:hover),
:global(.confirm-button-danger:focus) {
  background-color: #f78989 !important;
  border-color: #f78989 !important;
}

:global(.cancel-button-primary) {
  background-color: #409eff !important;
  border-color: #409eff !important;
  color: #fff !important;
}

:global(.cancel-button-primary:hover),
:global(.cancel-button-primary:focus) {
  background-color: #66b1ff !important;
  border-color: #66b1ff !important;
}

.result-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 20px;
}

:deep(.el-tabs__content) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.el-tab-pane) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.plain-text-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  overflow: hidden;
}

.plain-text-content :deep(.el-textarea) {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.plain-text-content :deep(.el-textarea__inner) {
  height: 100%;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none !important;
  cursor: default;
  overflow-y: auto;
  border: none !important;
  border-radius: 0;
  box-shadow: none !important;
  outline: none !important;
}

.plain-text-content :deep(.el-textarea__inner:focus) {
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}

.detailed-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px 0;
  overflow: hidden;
}

.loading-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.empty-result {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}
</style>
