/**
 * OCR API 封装
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 120000, // 120秒超时（OCR 处理可能较慢）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 错误处理
    let message = '请求失败'

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          message = data.error || '请求参数错误'
          break
        case 413:
          message = '文件大小超过限制'
          break
        case 429:
          message = '服务繁忙，请稍后重试'
          break
        case 500:
          message = data.error || '服务器内部错误'
          break
        case 504:
          message = 'OCR 处理超时，请尝试更小的图片'
          break
        default:
          message = data.error || `请求失败 (${status})`
      }
    } else if (error.request) {
      message = '网络连接失败，请检查后端服务是否启动'
    } else {
      message = error.message || '未知错误'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

/**
 * 健康检查
 */
export function healthCheck() {
  return request({
    url: '/health',
    method: 'get'
  })
}

/**
 * OCR 识别
 * @param {string} imageBase64 - Base64 编码的图片
 */
export function ocrRecognize(imageBase64) {
  return request({
    url: '/api/ocr',
    method: 'post',
    data: {
      image: imageBase64
    }
  })
}

export default {
  healthCheck,
  ocrRecognize
}
