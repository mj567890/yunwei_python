// 资产管理API
import { request } from '@/utils/request'
import type { Asset, AssetSearchParams, ApiResponse } from '@/types/common'

export type { Asset, AssetSearchParams }

// 资产管理API
export const assetApi = {
  // 获取资产列表 - 加强调试版本
  getAssets: (params?: AssetSearchParams): Promise<ApiResponse<{list: Asset[], total: number, page: number, page_size: number, total_pages: number}>> => {
    console.log('🔥 assetApi.getAssets 被调用:', params)
    
    // 简化参数处理
    if (!params) {
      console.log('🔥 无参数，直接请求')
      return request.get('/api/assets')
    }
    
    // 过滤undefined值，避免传递无效参数
    const cleanParams: any = {}
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        cleanParams[key] = value
      }
    })
    
    console.log('🔥 清理后的参数:', cleanParams)
    return request.get('/api/assets', cleanParams)
  },

  // 获取资产详情
  getAsset: (id: number): Promise<ApiResponse<Asset>> => 
    request.get(`/api/assets/${id}`),

  // 创建资产
  createAsset: (data: Partial<Asset>): Promise<ApiResponse<Asset>> => 
    request.post('/api/assets', data),

  // 更新资产
  updateAsset: (id: number, data: Partial<Asset>): Promise<ApiResponse<Asset>> => 
    request.put(`/api/assets/${id}`, data),

  // 删除资产
  deleteAsset: (id: number): Promise<ApiResponse<void>> => 
    request.delete(`/api/assets/${id}`),

  // 变更资产状态
  changeAssetStatus: (id: number, data: { status: string, remark?: string }): Promise<ApiResponse<void>> => 
    request.post(`/api/assets/${id}/change-status`, data),

  // 获取资产类别
  getAssetCategories: (): Promise<ApiResponse<string[]>> => 
    request.get('/api/assets/categories'),

  // 导出资产
  exportAssets: (params?: AssetSearchParams): void => {
    const baseURL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : '')
    const queryString = params ? '?' + new URLSearchParams(params as any).toString() : ''
    window.open(`${baseURL}/api/assets/export${queryString}`)
  },

  // 下载导入模板
  downloadTemplate: (): void => {
    const baseURL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : '')
    window.open(`${baseURL}/api/assets/import-template`)
  },

  // 导入资产
  importAssets: (file: File): Promise<ApiResponse<{success_count: number, error_count: number, errors?: string[]}>> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.upload('/api/assets/import', formData)
  },

  // 获取保修预警
  getWarrantyAlerts: (days = 30): Promise<ApiResponse<Asset[]>> => 
    request.get('/api/assets/warranty-alerts', { days }),

  // 获取资产统计
  getAssetStatistics: (): Promise<ApiResponse<{total: number, by_status: Record<string, number>, by_category: Record<string, number>}>> => 
    request.get('/api/assets/statistics')
}