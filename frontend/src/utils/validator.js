/**
 * 文件验证工具
 */

// 允许的文件类型
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/bmp']

// 最大文件大小 (10MB)
const MAX_FILE_SIZE = 10 * 1024 * 1024

/**
 * 验证文件类型
 * @param {File} file - 文件对象
 * @returns {boolean}
 */
export function validateFileType(file) {
  if (!file) {
    return false
  }
  return ALLOWED_TYPES.includes(file.type)
}

/**
 * 验证文件大小
 * @param {File} file - 文件对象
 * @returns {boolean}
 */
export function validateFileSize(file) {
  if (!file) {
    return false
  }
  return file.size <= MAX_FILE_SIZE
}

/**
 * 验证文件（类型和大小）
 * @param {File} file - 文件对象
 * @returns {{ valid: boolean, message: string }}
 */
export function validateFile(file) {
  if (!file) {
    return { valid: false, message: '请选择文件' }
  }

  if (!validateFileType(file)) {
    return {
      valid: false,
      message: '不支持的文件格式，仅支持 JPG/PNG/BMP 格式'
    }
  }

  if (!validateFileSize(file)) {
    const sizeMB = (file.size / 1024 / 1024).toFixed(2)
    return {
      valid: false,
      message: `文件大小超过限制（${sizeMB}MB > 10MB）`
    }
  }

  return { valid: true, message: '' }
}

/**
 * 将文件转为 Base64
 * @param {File} file - 文件对象
 * @returns {Promise<string>} Base64 字符串（不含前缀）
 */
export function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = () => {
      // 移除 data:image/xxx;base64, 前缀
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }

    reader.onerror = error => {
      reject(error)
    }

    reader.readAsDataURL(file)
  })
}

export default {
  validateFileType,
  validateFileSize,
  validateFile,
  fileToBase64
}
