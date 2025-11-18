/**
 * 剪贴板工具
 */
import { ElMessage } from 'element-plus'

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<boolean>} 是否成功
 */
export async function copyToClipboard(text) {
  if (!text) {
    ElMessage.warning('没有可复制的内容')
    return false
  }

  try {
    // 使用现代 Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text)
      ElMessage.success('已复制到剪贴板')
      return true
    }

    // 降级方案：使用 document.execCommand (已废弃但兼容性好)
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()

    const success = document.execCommand('copy')
    document.body.removeChild(textarea)

    if (success) {
      ElMessage.success('已复制到剪贴板')
      return true
    } else {
      throw new Error('复制失败')
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
    return false
  }
}

/**
 * 从剪贴板获取图片
 * @param {ClipboardEvent} event - 粘贴事件
 * @returns {File|null} 图片文件或 null
 */
export function getImageFromClipboard(event) {
  const items = event.clipboardData?.items

  if (!items) {
    return null
  }

  for (let i = 0; i < items.length; i++) {
    const item = items[i]

    // 检查是否为图片
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile()
      return file
    }
  }

  return null
}

export default {
  copyToClipboard,
  getImageFromClipboard
}
