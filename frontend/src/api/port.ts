// 端口管理API
import { request } from '@/utils/request'
import type { ApiResponse } from '@/types/common'

export interface AssetPort {
  id?: number
  asset_id: number
  port_name: string
  port_type?: 'ethernet' | 'fiber' | 'console' | 'management' | 'power' | 'usb'
  port_speed?: '10M' | '100M' | '1G' | '10G' | '25G' | '40G' | '100G'
  port_status?: 'used' | 'unused' | 'error' | 'disabled'
  port_index?: number
  is_uplink?: boolean
  duplex_mode?: 'full' | 'half' | 'auto'
  vlan_id?: number
  ip_address?: string
  mac_address?: string
  description?: string
  is_connected?: boolean
  connected_port_id?: number
  cable_type?: 'copper' | 'fiber' | 'wireless'
  cable_length?: number
  last_link_time?: string
  
  // 连接设备信息（后端返回）
  connected_asset_name?: string
  connected_port_name?: string
  connected_asset_id?: number
  asset_name?: string
  asset_code?: string
  asset_category?: string
  
  asset?: {
    id: number
    name: string
    category: string
  }
  connected_port?: AssetPort
  
  // 用于显示的连接信息
  connection_info?: {
    device_name?: string
    port_name?: string
    cable_type?: string
    cable_length?: number
    connection_time?: string
  }
}

export interface PortConnection {
  id?: number
  source_port_id: number
  target_port_id: number
  cable_type?: 'copper' | 'fiber' | 'wireless'
  cable_length?: number
  notes?: string
  connection_date?: string
  source_port?: AssetPort
  target_port?: AssetPort
}

export interface TopologyConnection {
  source_asset_id: number
  target_asset_id: number
  source_port: {
    id: number
    name: string
    type: string
  }
  target_port: {
    id: number
    name: string
    type: string
  }
  cable: {
    type?: string
    length?: number
  }
  connection_time?: string
}

// 端口管理API
export const portApi = {
  // 获取资产端口列表
  getAssetPorts: (assetId: number): Promise<ApiResponse<{ ports: AssetPort[], asset: any }>> =>
    request.get(`/api/ports/assets/${assetId}/ports`),

  // 创建端口
  createPort: (assetId: number, data: Partial<AssetPort>): Promise<ApiResponse<AssetPort>> =>
    request.post(`/api/ports/assets/${assetId}/ports`, data),

  // 批量创建端口
  createPortsBatch: (assetId: number, data: { ports: Partial<AssetPort>[] }): Promise<ApiResponse<{ created: AssetPort[], errors: string[] }>> =>
    request.post(`/api/ports/assets/${assetId}/ports/batch`, data),

  // 更新端口
  updatePort: (portId: number, data: Partial<AssetPort>): Promise<ApiResponse<AssetPort>> =>
    request.put(`/api/ports/${portId}`, data),

  // 删除端口
  deletePort: (portId: number): Promise<ApiResponse<void>> =>
    request.delete(`/api/ports/${portId}`),

  // 连接端口
  connectPorts: (data: Partial<PortConnection>): Promise<ApiResponse<PortConnection>> =>
    request.post('/api/ports/connect', data),

  // 断开端口连接
  disconnectPort: (portId: number): Promise<ApiResponse<void>> =>
    request.post(`/api/ports/${portId}/disconnect`),

  // 获取拓扑连接关系
  getTopologyConnections: (): Promise<ApiResponse<{ connections: TopologyConnection[], total_count: number }>> =>
    request.get('/api/ports/topology/connections'),

  // 获取连接历史
  getConnectionHistory: (params?: { page?: number, page_size?: number, asset_id?: number }): Promise<ApiResponse<{ connections: PortConnection[], total: number }>> =>
    request.get('/api/ports/connections/history', params),

  // 导出端口信息
  exportPorts: (assetId?: number): void => {
    const baseURL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : '')
    const params = assetId ? `?asset_id=${assetId}` : ''
    window.open(`${baseURL}/api/ports/export${params}`)
  },

  // 导入端口信息
  importPorts: (file: File, assetId?: number): Promise<ApiResponse<{ created: AssetPort[], errors: string[] }>> => {
    const formData = new FormData()
    formData.append('file', file)
    if (assetId) {
      formData.append('asset_id', assetId.toString())
    }
    return request.upload('/api/ports/import', formData)
  },

  // 获取端口连接建议（自动发现功能）
  getConnectionSuggestions: (portId: number): Promise<ApiResponse<AssetPort[]>> =>
    request.get(`/api/ports/${portId}/suggestions`),

  // 批量获取设备端口统计信息
  getPortsStatisticsBatch: (assetIds: number[]): Promise<ApiResponse<Record<number, PortStatistics>>> =>
    request.get(`/api/ports/statistics/batch?asset_ids=${assetIds.join(',')}`)
}

// 端口统计信息类型
export interface PortStatistics {
  port_count: number
  connected_ports: number
  available_ports: number
}