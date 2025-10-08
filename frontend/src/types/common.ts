// 通用类型定义文件
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: number
}

export interface PaginationParams {
  page: number
  pageSize: number  // 保持前端一致性，在API层转换
}

export interface PaginationInfo {
  total: number
  page: number
  pageSize: number
}

// 状态映射类型
export type StatusType = '在用' | '闲置' | '维修' | '报废' | '在线' | '离线' | '故障'
export type PriorityType = '低' | '中' | '高' | '紧急'
export type FaultStatusType = '新建' | '处理中' | '已解决' | '已关闭'
export type MaintenanceStatusType = '计划中' | '进行中' | '已完成' | '已取消'
export type WarrantyStatusType = '保修中' | '已过保' | '即将到期' | '未设置'

// 状态样式映射
export const STATUS_CLASS_MAP: Record<StatusType, string> = {
  '在用': 'success',
  '闲置': 'info',
  '维修': 'warning',
  '报废': 'danger',
  '在线': 'success',
  '离线': 'danger',
  '故障': 'warning'
}

export const PRIORITY_CLASS_MAP: Record<PriorityType, string> = {
  '低': 'low',
  '中': 'medium', 
  '高': 'high',
  '紧急': 'urgent'
}

export const FAULT_STATUS_CLASS_MAP: Record<FaultStatusType, string> = {
  '新建': 'info',
  '处理中': 'warning',
  '已解决': 'success',
  '已关闭': 'secondary'
}

export const MAINTENANCE_STATUS_CLASS_MAP: Record<MaintenanceStatusType, string> = {
  '计划中': 'info',
  '进行中': 'warning', 
  '已完成': 'success',
  '已取消': 'danger'
}

export const WARRANTY_STATUS_CLASS_MAP: Record<WarrantyStatusType, string> = {
  '保修中': 'success',
  '已过保': 'danger',
  '即将到期': 'warning',
  '未设置': 'info'
}

// 通用工具函数类型安全版本
export const getStatusClass = (status: string): string => {
  return STATUS_CLASS_MAP[status as StatusType] || 'info'
}

export const getPriorityClass = (priority: string): string => {
  return PRIORITY_CLASS_MAP[priority as PriorityType] || 'medium'
}

export const getFaultStatusClass = (status: string): string => {
  return FAULT_STATUS_CLASS_MAP[status as FaultStatusType] || 'info'
}

export const getMaintenanceStatusClass = (status: string): string => {
  return MAINTENANCE_STATUS_CLASS_MAP[status as MaintenanceStatusType] || 'info'
}

export const getWarrantyStatusClass = (status: string): string => {
  return WARRANTY_STATUS_CLASS_MAP[status as WarrantyStatusType] || 'info'
}

// 基础实体接口
export interface BaseEntity {
  id: number
  created_at: string
  updated_at?: string
}

// 用户相关类型
export interface UserRole {
  id: number
  name: string
  code: string
}

export interface UserInfo extends BaseEntity {
  username: string
  real_name: string
  email: string
  phone: string
  avatar: string
  department: string
  status: number
  roles: UserRole[]
  last_login_time: string
  last_login_ip: string
}

// 资产相关类型
export interface Asset extends BaseEntity {
  asset_code: string
  name: string
  category: string
  model: string
  brand: string
  serial_number: string
  purchase_date: string
  warranty_date: string
  warranty_start_date?: string // 保修开始日期
  warranty_end_date?: string // 保修结束日期
  warranty_period?: number // 保修期（月）
  status: StatusType
  location: string
  manager: string
  price?: number
  purchase_price?: number // 采购价格
  warranty_status?: WarrantyStatusType
  user_name?: string // 使用人姓名
  user_department?: string // 使用部门
  deploy_date?: string // 部署日期
  condition_rating?: string // 状态评级
  full_location?: string // 完整位置信息
  warranty_days_left?: number // 保修剩余天数
  usage_days?: number // 使用天数
  specifications?: AssetSpecification[] // 技术规格
  specification?: string // 规格说明
  // 位置信息
  building_id?: number // 楼宇ID
  floor_id?: number // 楼层ID
  room_id?: number // 房间ID
  location_detail?: string // 详细位置
  // 采购信息
  supplier?: string // 供应商
  purchase_order?: string // 采购订单
  // 网络信息
  ip_address?: string // IP地址
  mac_address?: string // MAC地址
  // 网络设备专用字段
  device_type?: string // 设备类型：交换机/路由器/防火墙/服务器等
  subnet_mask?: string // 子网掩码
  gateway?: string // 网关
  dns_servers?: string // DNS服务器
  firmware_version?: string // 固件版本
  port_count?: number // 端口数量
  is_managed?: boolean // 是否纳管
  x_position?: number // 拓扑图X坐标
  y_position?: number // 拓扑图Y坐标
  is_network_device?: boolean // 是否为网络设备
  // 其他信息
  remark?: string // 备注
}

// 资产技术规格
export interface AssetSpecification {
  name: string
  value: string
  unit?: string
}

// 故障相关类型
export interface Fault extends BaseEntity {
  fault_code?: string // 故障编码，创建时可选（由后端自动生成）
  title: string
  fault_type: string
  severity: string
  priority: PriorityType
  status: FaultStatusType
  reporter_name: string
  report_time: string
  assignee_name: string | null
  assign_time: string | null
  response_time: string | null
  sla_breach: boolean
  affected_assets: Array<{ id: number; name: string; asset_code?: string }>
  description?: string // 故障描述
  solution?: string // 解决方案
  solution_time?: string // 解决时间
  solver_name?: string // 解决人
}

// 运维记录相关类型
export interface MaintenanceRecord extends BaseEntity {
  record_code: string
  title: string
  record_type: string
  category: string
  responsible_person: string
  department: string
  start_time: string
  status: MaintenanceStatusType
  priority: PriorityType
  progress: number
  asset_count: number
  planned_end_time?: string // 计划完成时间
  actual_end_time?: string // 实际完成时间
  description?: string // 维护描述
  summary?: string // 结果总结
  result_status?: string // 维护结果
  actual_duration?: number // 实际耗时(小时)
  cost?: number // 成本费用
  estimated_duration?: number // 预计耗时(小时)
  estimated_cost?: number // 预算成本(元)
  risk_level?: string // 风险级别
  potential_risks?: string // 潜在风险
  risk_mitigation?: string // 应对措施
  responsible_person_id?: number // 责任人ID
}

// 网络设备相关类型
export interface NetworkDevice extends BaseEntity {
  name: string
  device_type: string
  brand?: string
  model?: string
  ip_address?: string
  mac_address?: string
  subnet_mask?: string
  gateway?: string
  dns_servers?: string
  building_id?: number
  floor_id?: number
  room_id?: number
  location_detail?: string
  full_location?: string
  status: StatusType
  is_managed?: boolean
  x_position?: number
  y_position?: number
  serial_number?: string
  firmware_version?: string
  purchase_date?: string
  warranty_end_date?: string
  description?: string
  vlan_id?: number
  port_count?: number
  ports?: NetworkPort[]
}

export interface NetworkPort {
  id?: number
  device_id?: number
  port_name: string
  port_type?: string
  port_speed?: string
  status: string
  is_connected: boolean
  connected_device_id?: number
  connected_port_id?: number
  connected_device_name?: string
  connected_port_name?: string
  vlan_id?: number
  description?: string
}

// 网络拓扑相关类型
export interface TopologyNode extends BaseEntity {
  name: string
  type: string
  ip?: string
  status: string
  x?: number
  y?: number
  ports?: NetworkPort[]
  device_category?: 'topology' | 'terminal' | 'legacy'  // 设备分类
  icon?: string  // 设备图标
  color?: string  // 设备颜色
  asset_id?: number  // 关联的资产ID
  legacy?: boolean  // 是否为传统设备
  port_count?: number  // 端口数量
  connected_ports?: number  // 已连接端口数
  model?: string  // 设备型号
  brand?: string  // 设备品牌
  firmware_version?: string  // 固件版本
  location?: string  // 设备位置
  highlighted?: boolean  // 是否高亮显示
  selected?: boolean  // 是否被选中
}

export interface TopologyEdge {
  id?: number
  source_id: number
  target_id: number
  source_port: string
  target_port: string
  cable_type?: string  // 线缆类型：copper/fiber/wireless
  cable_length?: number  // 线缆长度
  link_status?: 'up' | 'down'  // 链路状态
  bandwidth?: string  // 带宽
  source_port_details?: {
    id: number
    name: string
    type: string
    speed?: string
  }
  target_port_details?: {
    id: number
    name: string
    type: string
    speed?: string
  }
  highlighted?: boolean  // 是否高亮显示
}

// 拓扑数据接口
export interface TopologyData {
  nodes: TopologyNode[]
  edges: TopologyEdge[]
  updated_at: string
  mixed_mode?: boolean
  topology_count?: number
  terminal_count?: number
  legacy_count?: number
}

// 拓扑配置接口
export interface TopologyConfig {
  layout: 'force' | 'circular' | 'grid' | 'manual'  // 布局方式
  show_ports: boolean  // 是否显示端口
  show_labels: boolean  // 是否显示标签
  show_ips: boolean  // 是否显示IP地址
  enable_physics: boolean  // 是否启用物理引擎
  node_spacing: number  // 节点间距
  link_distance: number  // 连接线长度
  enable_clustering: boolean  // 是否启用聚类
}

// 搜索和过滤接口
export interface TopologyFilter {
  device_types?: string[]  // 设备类型过滤
  statuses?: string[]  // 状态过滤
  categories?: string[]  // 分类过滤
  search_keyword?: string  // 搜索关键词
  show_disconnected?: boolean  // 是否显示未连接设备
}

// 搜索参数类型
export interface AssetSearchParams extends PaginationParams {
  keyword?: string
  category?: string
  status?: string
  location?: string
  name?: string
  brand?: string
  model?: string
  user_name?: string
  warranty_status?: string
  network_devices?: string  // 网络设备过滤标记
}

export interface FaultSearchParams extends PaginationParams {
  keyword?: string
  fault_type?: string
  priority?: string
  status?: string
}

export interface MaintenanceSearchParams extends PaginationParams {
  keyword?: string
  record_type?: string
  status?: string
  date_start?: string
  date_end?: string
}

export interface UserSearchParams extends PaginationParams {
  keyword?: string
  role?: string
  status?: string
  department?: string
}

export interface NetworkDeviceSearchParams extends PaginationParams {
  name?: string
  device_type?: string
  status?: string
}