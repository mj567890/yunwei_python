import { request } from '@/utils/request'
import type { ApiResponse } from '@/types/common'

export interface AssetStatistics {
  total: number
  byCategory: Record<string, number>
  byStatus: Record<string, number>
  byLocation: Record<string, number>
  recentChanges: Array<{
    date: string
    added: number
    removed: number
  }>
}

export interface MaintenanceStatistics {
  total: number
  byType: Record<string, number>
  byStatus: Record<string, number>
  monthlyTrend: Array<{
    month: string
    count: number
    cost: number
  }>
  avgCost: number
}

export interface FaultStatistics {
  total: number
  resolved: number
  pending: number
  byLevel: Record<string, number>
  byCategory: Record<string, number>
  resolutionTime: {
    avg: number
    trend: Array<{
      date: string
      avgTime: number
    }>
  }
}

export interface NetworkStatistics {
  totalDevices: number
  onlineDevices: number
  offlineDevices: number
  byType: Record<string, number>
  performanceMetrics: Array<{
    device: string
    cpu: number
    memory: number
    bandwidth: number
  }>
}

export interface DashboardData {
  assets: AssetStatistics
  maintenance: MaintenanceStatistics
  faults: FaultStatistics
  network: NetworkStatistics
}

const statisticsApi = {
  // 获取仪表板统计数据
  getDashboardData: (): Promise<ApiResponse<DashboardData>> => {
    return request.get('/api/statistics/dashboard')
  },

  // 获取资产统计
  getAssetStatistics: (params?: {
    startDate?: string
    endDate?: string
    category?: string
    location?: string
  }): Promise<ApiResponse<AssetStatistics>> => {
    return request.get('/api/statistics/assets', params)
  },

  // 获取运维统计
  getMaintenanceStatistics: (params?: {
    startDate?: string
    endDate?: string
    type?: string
  }): Promise<ApiResponse<MaintenanceStatistics>> => {
    return request.get('/api/statistics/maintenance', params)
  },

  // 获取故障统计
  getFaultStatistics: (params?: {
    startDate?: string
    endDate?: string
    level?: string
  }): Promise<ApiResponse<FaultStatistics>> => {
    return request.get('/api/statistics/faults', params)
  },

  // 获取网络统计
  getNetworkStatistics: (): Promise<ApiResponse<NetworkStatistics>> => {
    return request.get('/api/statistics/network')
  },

  // 导出统计报告
  exportReport: async (params: {
    type: 'assets' | 'maintenance' | 'faults' | 'network'
    format: 'excel' | 'pdf'
    startDate: string
    endDate: string
  }): Promise<Blob> => {
    const response = await request.get('/api/statistics/export', {
      ...params,
      responseType: 'blob'
    })
    return response as any // 返回原始 blob 数据
  }
}

export default statisticsApi