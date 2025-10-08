// 网络设备管理API
import { request } from '@/utils/request'
import type { 
  NetworkDevice, 
  NetworkDeviceSearchParams, 
  ApiResponse, 
  TopologyNode, 
  TopologyEdge, 
  TopologyData,
  TopologyConfig,
  TopologyFilter,
  NetworkPort 
} from '@/types/common'

export type { NetworkDevice, TopologyNode, TopologyEdge, TopologyData }

// 网络设备管理API
export const networkApi = {
  // 获取设备列表
  getDevices: (params?: NetworkDeviceSearchParams): Promise<ApiResponse<{list: NetworkDevice[]}>> => 
    request.get('/api/network/devices', params),

  // 获取设备详情
  getDevice: (id: number): Promise<ApiResponse<NetworkDevice>> => 
    request.get(`/api/network/devices/${id}`),

  // 创建设备
  createDevice: (data: Partial<NetworkDevice>): Promise<ApiResponse<NetworkDevice>> => 
    request.post('/api/network/devices', data),

  // 更新设备
  updateDevice: (id: number, data: Partial<NetworkDevice>): Promise<ApiResponse<NetworkDevice>> => 
    request.put(`/api/network/devices/${id}`, data),

  // 删除设备
  deleteDevice: (id: number): Promise<ApiResponse<void>> => 
    request.delete(`/api/network/devices/${id}`),

  // 获取设备端口
  getDevicePorts: (deviceId: number): Promise<ApiResponse<NetworkPort[]>> => 
    request.get(`/api/network/devices/${deviceId}/ports`),

  // 创建设备端口
  createDevicePort: (deviceId: number, data: Partial<NetworkPort>): Promise<ApiResponse<NetworkPort>> => 
    request.post(`/api/network/devices/${deviceId}/ports`, data),

  // 连接端口
  connectPorts: (portId: number, targetPortId: number): Promise<ApiResponse<void>> => 
    request.post(`/api/network/ports/${portId}/connect`, { target_port_id: targetPortId }),

  // 断开端口
  disconnectPort: (portId: number): Promise<ApiResponse<void>> => 
    request.post(`/api/network/ports/${portId}/disconnect`),

  // 获取网络拓扑
  getNetworkTopology: (filter?: TopologyFilter): Promise<ApiResponse<TopologyData>> => 
    request.get('/api/network/topology', filter),

  // 保存网络拓扑
  saveNetworkTopology: (data: { name?: string, description?: string, topology_data: any }): Promise<ApiResponse<void>> => 
    request.post('/api/network/topology/save', data),

  // 获取拓扑连接关系
  getTopologyConnections: (): Promise<ApiResponse<{ connections: TopologyEdge[], total_count: number }>> => 
    request.get('/api/ports/topology/connections'),

  // 搜索设备
  searchDevices: (keyword: string): Promise<ApiResponse<TopologyNode[]>> => 
    request.get('/api/network/devices/search', { keyword }),

  // 获取设备详细信息（用于悬浮显示）
  getDeviceDetails: (deviceId: number, isLegacy = false): Promise<ApiResponse<TopologyNode>> => {
    const endpoint = isLegacy ? `/api/network/devices/legacy/${deviceId}` : `/api/network/devices/${deviceId}`
    return request.get(endpoint)
  },

  // 获取端口详细信息（用于悬浮显示）
  getPortDetails: (portId: number): Promise<ApiResponse<NetworkPort>> => 
    request.get(`/api/ports/${portId}`),

  // 更新设备位置
  updateDevicePosition: (deviceId: number, x: number, y: number, isLegacy = false): Promise<ApiResponse<void>> => {
    const endpoint = isLegacy ? `/api/network/devices/legacy/${deviceId}/position` : `/api/network/devices/${deviceId}/position`
    return request.put(endpoint, { x, y })
  },

  // 批量更新设备位置
  batchUpdatePositions: (positions: Array<{ id: number, x: number, y: number, isLegacy?: boolean }>): Promise<ApiResponse<void>> => 
    request.put('/api/network/topology/positions', { positions }),

  // 获取拓扑配置
  getTopologyConfig: (): Promise<ApiResponse<TopologyConfig>> => 
    request.get('/api/network/topology/config'),

  // 保存拓扑配置
  saveTopologyConfig: (config: TopologyConfig): Promise<ApiResponse<void>> => 
    request.post('/api/network/topology/config', config),

  // 自动布局
  autoLayout: (algorithm: 'force' | 'circular' | 'grid'): Promise<ApiResponse<{ nodes: TopologyNode[] }>> => 
    request.post('/api/network/topology/auto-layout', { algorithm }),

  // 导出拓扑图像
  exportTopologyImage: (format: 'png' | 'svg' | 'pdf' = 'png'): Promise<ApiResponse<{ download_url: string }>> => 
    request.post('/api/network/topology/export', { format }),

  // 标记设备故障
  markDeviceFault: (deviceId: number, description: string): Promise<ApiResponse<void>> => 
    request.post(`/api/network/devices/${deviceId}/fault`, { description })
}