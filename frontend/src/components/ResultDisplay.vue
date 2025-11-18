<template>
  <div class="result-display">
    <div v-if="hasResult" class="result-container">
      <div class="result-header">
        <span class="title">识别结果</span>
        <el-button type="primary" size="small" @click="handleCopy">
          <el-icon><CopyDocument /></el-icon>
          复制文本
        </el-button>
      </div>

      <el-tabs v-model="activeTab" class="result-tabs">
        <!-- 纯文本页签 -->
        <el-tab-pane label="纯文本" name="plain">
          <div class="plain-text-content">
            <el-input
              v-model="result.plain_text"
              type="textarea"
              :rows="20"
              readonly
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
              max-height="500"
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

const activeTab = ref('plain')

/**
 * 是否有结果
 */
const hasResult = computed(() => {
  return props.result && (props.result.plain_text || props.result.detailed?.length > 0)
})

/**
 * 复制纯文本
 */
const handleCopy = () => {
  copyToClipboard(props.result.plain_text)
}

/**
 * 获取置信度标签类型
 */
const getConfidenceType = (confidence) => {
  if (confidence >= 0.9) return 'success'
  if (confidence >= 0.7) return 'warning'
  return 'danger'
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
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.result-header .title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.result-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 20px;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}

.plain-text-content,
.detailed-content {
  padding: 16px 0;
}

:deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
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
