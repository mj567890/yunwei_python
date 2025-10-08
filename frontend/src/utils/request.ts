// HTTP请求工具类
// @ts-nocheck

import { getSecureToken } from './crypto'

// 根据环境设置API基础URL - 开发环境使用相对路径让Vite代理生效
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : '')

interface ApiResponse<T = any> {
  code: number
  success: boolean
  message: string
  data: T
  timestamp: string
}

interface PageResponse<T = any> extends ApiResponse<{
  list: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}> {}

class RequestClient {
  private baseURL: string = API_BASE_URL

  constructor() {
    // 拦截器设置
    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 不要重写全局fetch，而是在请求时处理
    // 这样可以避免与CORS预检请求冲突
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      // 首先检查HTTP状态码（200-299都是成功）
      if (!response.ok) {
        // 对于4xx和5xx错误，尝试获取错误信息
        try {
          const errorData = await response.json()
          throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`)
        } catch {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
      }
      
      const data = await response.json()
      console.log('📋 API响应数据:', data) // 调试日志
      
      // 适配多种后端返回格式
      if (data.success === true || data.status === 'success' || response.status === 200) {
        return {
          code: data.code || response.status,
          success: true,
          message: data.message || '请求成功',
          data: data.data,
          timestamp: data.timestamp || new Date().toISOString()
        }
      } else {
        console.error('API响应失败:', data)
        throw new Error(data.message || '请求失败')
      }
    } catch (error) {
      console.error('处理响应失败:', error)
      
      // 特别处理网络错误（如CORS问题）
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('网络连接失败，请检查网络或服务器状态')
      }
      
      if (error instanceof Error) {
        throw error
      }
      throw new Error('网络请求失败')
    }
  }

  async get<T = any>(url: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
    const token = getSecureToken()
    const queryString = params ? '?' + new URLSearchParams(params).toString() : ''
    
    const response = await fetch(`${this.baseURL}${url}${queryString}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    })
    
    return this.handleResponse<T>(response)
  }

  async post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    const token = getSecureToken()
    
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: JSON.stringify(data)
    })
    
    return this.handleResponse<T>(response)
  }

  async put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    const token = getSecureToken()
    
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: JSON.stringify(data)
    })
    return this.handleResponse<T>(response)
  }

  async delete<T = any>(url: string): Promise<ApiResponse<T>> {
    const token = getSecureToken()
    
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    })
    return this.handleResponse<T>(response)
  }

  async upload(url: string, formData: FormData): Promise<ApiResponse> {
    const token = getSecureToken()
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: formData
    })
    return this.handleResponse(response)
  }
}

export const request = new RequestClient()
export type { ApiResponse, PageResponse }