import { request } from '@/utils/request'
import type { ApiResponse, MaintenanceRecord, MaintenanceSearchParams } from '@/types/common'

export const maintenanceApi = {
  // 获取运维记录列表
  getMaintenanceRecords: (params?: MaintenanceSearchParams): Promise<ApiResponse<{list: MaintenanceRecord[], total: number, page: number, page_size: number, total_pages: number}>> => 
    request.get('/maintenance', params),

  // 获取运维记录详情
  getMaintenance: (id: number): Promise<ApiResponse<MaintenanceRecord>> => 
    request.get(`/maintenance/${id}`),

  // 创建运维记录
  createMaintenance: (data: Partial<MaintenanceRecord>): Promise<ApiResponse<MaintenanceRecord>> => 
    request.post('/maintenance', data),

  // 更新运维记录
  updateMaintenance: (id: number, data: Partial<MaintenanceRecord>): Promise<ApiResponse<MaintenanceRecord>> => 
    request.put(`/maintenance/${id}`, data),

  // 删除运维记录
  deleteMaintenance: (id: number): Promise<ApiResponse<void>> => 
    request.delete(`/maintenance/${id}`),

  // 开始运维记录
  startMaintenance: (id: number, data: { start_time?: string, remark?: string }): Promise<ApiResponse<void>> => 
    request.post(`/maintenance/${id}/start`, data),

  // 完成运维记录
  completeMaintenance: (id: number, data: { summary: string, result_status: string, actual_duration?: number, cost?: number }): Promise<ApiResponse<void>> => 
    request.post(`/maintenance/${id}/complete`, data),

  // 取消运维记录
  cancelMaintenance: (id: number, data: { reason: string }): Promise<ApiResponse<void>> => 
    request.post(`/maintenance/${id}/cancel`, data),

  // 更新进度
  updateProgress: (id: number, data: { progress: number, description?: string }): Promise<ApiResponse<void>> => 
    request.post(`/maintenance/${id}/progress`, data),

  // 获取运维记录类型
  getMaintenanceTypes: (): Promise<ApiResponse<string[]>> => 
    request.get('/maintenance/types'),

  // 获取运维记录分类
  getMaintenanceCategories: (): Promise<ApiResponse<string[]>> => 
    request.get('/maintenance/categories'),

  // 获取运维记录统计
  getMaintenanceStatistics: (): Promise<ApiResponse<{total: number, by_status: Record<string, number>, by_type: Record<string, number>}>> => 
    request.get('/maintenance/statistics'),

  // 导出运维记录
  exportMaintenance: (params?: MaintenanceSearchParams): void => {
    const baseURL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : '')
    const queryString = params ? '?' + new URLSearchParams(params as any).toString() : ''
    window.open(`${baseURL}/api/maintenance/export${queryString}`)
  },

  // 获取执行步骤
  getExecutionSteps: (maintenanceId: number): Promise<ApiResponse<any[]>> => 
    request.get(`/maintenance/${maintenanceId}/steps`),

  // 添加执行步骤
  addExecutionStep: (maintenanceId: number, data: { title: string, description: string, estimated_time?: number, executor_id?: number }): Promise<ApiResponse<any>> => 
    request.post(`/maintenance/${maintenanceId}/steps`, data),

  // 更新执行步骤
  updateExecutionStep: (maintenanceId: number, stepId: number, data: any): Promise<ApiResponse<any>> => 
    request.put(`/maintenance/${maintenanceId}/steps/${stepId}`, data),

  // 开始执行步骤
  startExecutionStep: (maintenanceId: number, stepId: number): Promise<ApiResponse<void>> => 
    request.post(`/maintenance/${maintenanceId}/steps/${stepId}/start`),

  // 完成执行步骤
  completeExecutionStep: (maintenanceId: number, stepId: number, data: { actual_time?: number, notes?: string }): Promise<ApiResponse<void>> => 
    request.post(`/maintenance/${maintenanceId}/steps/${stepId}/complete`, data),

  // 获取执行记录
  getExecutionRecords: (maintenanceId: number): Promise<ApiResponse<any[]>> => 
    request.get(`/maintenance/${maintenanceId}/records`),

  // 添加执行记录
  addExecutionRecord: (maintenanceId: number, data: { record_type: string, description: string, time_spent?: number }): Promise<ApiResponse<any>> => 
    request.post(`/maintenance/${maintenanceId}/records`, data),

  // 获取涉及资产
  getAffectedAssets: (maintenanceId: number): Promise<ApiResponse<any[]>> => 
    request.get(`/maintenance/${maintenanceId}/assets`),

  // 添加涉及资产
  addAffectedAsset: (maintenanceId: number, data: { asset_id: number }): Promise<ApiResponse<void>> => 
    request.post(`/maintenance/${maintenanceId}/assets`, data),

  // 移除涉及资产
  removeAffectedAsset: (maintenanceId: number, assetId: number): Promise<ApiResponse<void>> => 
    request.delete(`/maintenance/${maintenanceId}/assets/${assetId}`),

  // 获取附件
  getAttachments: (maintenanceId: number): Promise<ApiResponse<any[]>> => 
    request.get(`/maintenance/${maintenanceId}/attachments`),

  // 上传附件
  uploadAttachment: (maintenanceId: number, file: File): Promise<ApiResponse<any>> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.upload(`/maintenance/${maintenanceId}/attachments`, formData)
  },

  // 删除附件
  deleteAttachment: (maintenanceId: number, attachmentId: number): Promise<ApiResponse<void>> => 
    request.delete(`/maintenance/${maintenanceId}/attachments/${attachmentId}`)
}