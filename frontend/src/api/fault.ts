import { request } from '@/utils/request'
import type { ApiResponse, Fault, FaultSearchParams } from '@/types/common'

export const faultApi = {
  // 获取故障列表
  getFaults: (params?: FaultSearchParams): Promise<ApiResponse<{list: Fault[], total: number, page: number, page_size: number, total_pages: number}>> => 
    request.get('/faults', params),

  // 获取故障详情
  getFault: (id: number): Promise<ApiResponse<Fault>> => 
    request.get(`/faults/${id}`),

  // 创建故障
  createFault: (data: Partial<Fault>): Promise<ApiResponse<Fault>> => 
    request.post('/faults', data),

  // 更新故障
  updateFault: (id: number, data: Partial<Fault>): Promise<ApiResponse<Fault>> => 
    request.put(`/faults/${id}`, data),

  // 删除故障
  deleteFault: (id: number): Promise<ApiResponse<void>> => 
    request.delete(`/faults/${id}`),

  // 指派故障
  assignFault: (id: number, data: { assignee_id: number, remark?: string }): Promise<ApiResponse<void>> => 
    request.post(`/faults/${id}/assign`, data),

  // 处理故障
  processFault: (id: number, data: { description: string, time_spent?: number }): Promise<ApiResponse<void>> => 
    request.post(`/faults/${id}/process`, data),

  // 解决故障
  resolveFault: (id: number, data: { solution: string, time_spent?: number }): Promise<ApiResponse<void>> => 
    request.post(`/faults/${id}/resolve`, data),

  // 关闭故障
  closeFault: (id: number, data: { remark?: string }): Promise<ApiResponse<void>> => 
    request.post(`/faults/${id}/close`, data),

  // 重新打开故障
  reopenFault: (id: number, data: { reason: string }): Promise<ApiResponse<void>> => 
    request.post(`/faults/${id}/reopen`, data),

  // 获取故障类型
  getFaultTypes: (): Promise<ApiResponse<string[]>> => 
    request.get('/faults/types'),

  // 获取故障统计
  getFaultStatistics: (): Promise<ApiResponse<{total: number, by_status: Record<string, number>, by_priority: Record<string, number>}>> => 
    request.get('/faults/statistics'),

  // 导出故障
  exportFaults: (params?: FaultSearchParams): void => {
    const baseURL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : '')
    const queryString = params ? '?' + new URLSearchParams(params as any).toString() : ''
    window.open(`${baseURL}/api/faults/export${queryString}`)
  },

  // 获取故障处理记录
  getFaultProgressRecords: (faultId: number): Promise<ApiResponse<any[]>> => 
    request.get(`/faults/${faultId}/progress`),

  // 添加故障处理记录
  addFaultProgress: (faultId: number, data: { description: string, time_spent?: number }): Promise<ApiResponse<void>> => 
    request.post(`/faults/${faultId}/progress`, data),

  // 获取故障附件
  getFaultAttachments: (faultId: number): Promise<ApiResponse<any[]>> => 
    request.get(`/faults/${faultId}/attachments`),

  // 上传故障附件
  uploadFaultAttachment: (faultId: number, file: File): Promise<ApiResponse<any>> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.upload(`/faults/${faultId}/attachments`, formData)
  },

  // 删除故障附件
  deleteFaultAttachment: (faultId: number, attachmentId: number): Promise<ApiResponse<void>> => 
    request.delete(`/faults/${faultId}/attachments/${attachmentId}`),

  // 获取故障操作日志
  getFaultLogs: (faultId: number): Promise<ApiResponse<any[]>> => 
    request.get(`/faults/${faultId}/logs`)
}