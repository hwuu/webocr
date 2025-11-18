<template>
  <div class="image-preview">
    <div v-if="imageUrl" class="preview-container">
      <div class="preview-header">
        <span class="title">图片预览</span>
      </div>
      <div class="preview-content" ref="contentRef">
        <div class="image-wrapper" ref="wrapperRef">
          <el-image
            ref="imageRef"
            :src="imageUrl"
            :preview-src-list="[imageUrl]"
            fit="contain"
            class="preview-image"
            alt="预览图片"
            @load="handleImageLoad"
          />
          <canvas ref="canvasRef" class="box-canvas"></canvas>
        </div>
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
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

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
  },
  ocrResult: {
    type: Object,
    default: () => ({ plain_text: '', detailed: [] })
  },
  highlightIndex: {
    type: Number,
    default: -1
  }
})

// Refs
const imageRef = ref(null)
const canvasRef = ref(null)
const contentRef = ref(null)
const wrapperRef = ref(null)

// 图片实际尺寸
const imageNaturalSize = ref({ width: 0, height: 0 })

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
 * 图片加载完成
 */
const handleImageLoad = () => {
  nextTick(() => {
    const img = imageRef.value?.$el?.querySelector('img')
    if (img) {
      imageNaturalSize.value = {
        width: img.naturalWidth,
        height: img.naturalHeight
      }
      drawBoxes()
    }
  })
}

/**
 * 绘制边界框
 */
const drawBoxes = () => {
  const canvas = canvasRef.value
  const wrapper = wrapperRef.value
  const img = imageRef.value?.$el?.querySelector('img')

  if (!canvas || !wrapper || !img) return

  // 设置 canvas 尺寸匹配图片显示尺寸
  const rect = img.getBoundingClientRect()
  const wrapperRect = wrapper.getBoundingClientRect()

  canvas.width = rect.width
  canvas.height = rect.height
  canvas.style.left = `${rect.left - wrapperRect.left}px`
  canvas.style.top = `${rect.top - wrapperRect.top}px`

  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // 如果没有识别结果，不绘制
  if (!props.ocrResult?.detailed?.length) return

  // 计算缩放比例
  const scaleX = rect.width / imageNaturalSize.value.width
  const scaleY = rect.height / imageNaturalSize.value.height

  // 绘制所有边界框
  props.ocrResult.detailed.forEach((item, index) => {
    if (!item.box) return

    const isHighlight = index === props.highlightIndex

    ctx.strokeStyle = isHighlight ? '#409eff' : '#67c23a'
    ctx.lineWidth = isHighlight ? 3 : 2
    ctx.fillStyle = isHighlight ? 'rgba(64, 158, 255, 0.1)' : 'rgba(103, 194, 58, 0.05)'

    ctx.beginPath()
    // box 格式: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    const scaledBox = item.box.map(([x, y]) => [x * scaleX, y * scaleY])

    ctx.moveTo(scaledBox[0][0], scaledBox[0][1])
    for (let i = 1; i < scaledBox.length; i++) {
      ctx.lineTo(scaledBox[i][0], scaledBox[i][1])
    }
    ctx.closePath()

    ctx.fill()
    ctx.stroke()
  })
}

// 监听高亮索引变化
watch(() => props.highlightIndex, () => {
  drawBoxes()
})

// 监听 OCR 结果变化
watch(() => props.ocrResult, () => {
  nextTick(() => {
    drawBoxes()
  })
}, { deep: true })

// 窗口大小变化时重绘
const handleResize = () => {
  drawBoxes()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
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

.image-wrapper {
  position: relative;
  display: inline-block;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.preview-image :deep(img) {
  display: block;
}

.box-canvas {
  position: absolute;
  pointer-events: none;
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
