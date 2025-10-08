<template>
  <div class="topology-container">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h1>网络拓扑图</h1>
        <span class="update-time">最后更新: {{ updateTime }}</span>
        <div class="topology-stats">
          <span class="stat-item">设备: {{ filteredNodes.length }}</span>
          <span class="stat-item">连接: {{ filteredEdges.length }}</span>
        </div>
      </div>
      
      <!-- 中间区域：搜索和过滤 -->
      <div class="toolbar-center">
        <div class="search-box">
          <input 
            v-model="searchKeyword" 
            @keyup.enter="focusDevice"
            type="text" 
            placeholder="搜索设备名称、IP或类型..."
            class="search-input"
          >
          <button @click="handleSearch" class="search-btn">🔍</button>
          <button @click="focusDevice" class="focus-btn">🎯</button>
        </div>
        
        <div class="filter-controls">
          <button @click="showFilters = !showFilters" class="filter-toggle" :class="{ active: showFilters }">
            📊 过滤器
          </button>
          
          <div class="layout-controls">
            <label>布局:</label>
            <select v-model="layoutAlgorithm" @change="autoLayout" class="layout-select">
              <option value="manual">手动</option>
              <option value="force">力导向</option>
              <option value="circular">圆形</option>
              <option value="grid">网格</option>
            </select>
          </div>
          
          <div class="display-options">
            <label><input v-model="showPorts" @change="togglePorts" type="checkbox"> 端口</label>
            <label><input v-model="showLabels" type="checkbox"> 标签</label>
            <label><input v-model="showIPs" type="checkbox"> IP</label>
          </div>
        </div>
      </div>
      
      <div class="toolbar-right">
        <!-- 工具按钮 -->
        <button @click="openNewConnection" class="btn btn-success">
          🔗 新建连接
        </button>
        <button @click="refreshTopology" :disabled="loading" class="btn btn-secondary">
          🔄 {{ loading ? '刷新中...' : '刷新' }}
        </button>
        <button @click="saveTopology" class="btn btn-primary">
          💾 保存布局
        </button>
        <button @click="exportTopology" class="btn btn-secondary">
          📤 导出图片
        </button>
        <div class="view-controls">
          <button @click="zoomIn" class="btn-icon">🔍+</button>
          <button @click="zoomOut" class="btn-icon">🔍-</button>
          <button @click="resetView" class="btn-icon">🎯</button>
        </div>
      </div>
    </div>

    <!-- 过滤器面板 -->
    <div v-if="showFilters" class="filter-panel">
      <div class="filter-section">
        <h4>设备类型</h4>
        <div class="filter-options">
          <label v-for="type in deviceTypes" :key="type">
            <input 
              type="checkbox" 
              :value="type" 
              v-model="activeFilters.device_types"
              @change="applyFilters"
            >
            {{ type }}
          </label>
        </div>
      </div>
      
      <div class="filter-section">
        <h4>设备状态</h4>
        <div class="filter-options">
          <label v-for="status in deviceStatuses" :key="status">
            <input 
              type="checkbox" 
              :value="status" 
              v-model="activeFilters.statuses"
              @change="applyFilters"
            >
            <span :class="`status-dot status-${status}`"></span>
            {{ status }}
          </label>
        </div>
      </div>
      
      <div class="filter-section">
        <h4>显示选项</h4>
        <div class="filter-options">
          <label>
            <input 
              type="checkbox" 
              v-model="activeFilters.show_disconnected"
              @change="applyFilters"
            >
            显示未连接设备
          </label>
        </div>
      </div>
      
      <div class="filter-actions">
        <button @click="clearFilters" class="btn btn-secondary">清除过滤</button>
        <button @click="fitToScreen" class="btn btn-primary">适应屏幕</button>
      </div>
    </div>

    <!-- 拓扑图画布 -->
    <div class="topology-canvas-container">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>加载拓扑数据中...</p>
      </div>
      
      <svg 
        ref="topologySvg" 
        class="topology-svg"
        @click="handleCanvasClick"
      >
        <!-- 连接线 -->
        <g class="edges">
          <line
            v-for="edge in filteredEdges"
            :key="`${edge.source_id}-${edge.target_id}`"
            :x1="getNodeById(edge.source_id)?.x || 0"
            :y1="getNodeById(edge.source_id)?.y || 0"
            :x2="getNodeById(edge.target_id)?.x || 0"
            :y2="getNodeById(edge.target_id)?.y || 0"
            :class="getEdgeClass(edge)"
            :stroke="getEdgeColor(edge)"
            :stroke-width="2"
            @mouseenter="handleEdgeHover(edge, $event)"
            @mouseleave="handleEdgeLeave"
            @click="handleEdgeClick(edge)"
          />
        </g>
        
        <!-- 设备节点 -->
        <g class="nodes">
          <g
            v-for="node in filteredNodes"
            :key="node.id"
            :class="[getNodeClass(node), { 'dragging': isDragging && dragNode?.id === node.id }]"
            :transform="getNodeTransform(node)"
            @mousedown="handleNodeMouseDown(node, $event)"
            @click="handleNodeClick(node, $event)"
            @mouseenter="handleNodeHover(node, $event)"
            @mouseleave="handleNodeLeave"
          >
            <!-- 高亮光晕 -->
            <circle
              v-if="node.highlighted || node.selected"
              :r="nodeRadius + 8"
              class="node-glow"
              :class="{ selected: node.selected }"
            />
            
            <!-- 设备图标背景 -->
            <circle
              :r="nodeRadius"
              :class="getNodeBgClass(node)"
            />
            
            <!-- 设备图标 -->
            <text
              :class="`node-icon type-${node.type}`"
              text-anchor="middle"
              dy="0.35em"
              font-size="24"
            >
              {{ node.icon || getDeviceIcon(node.type) }}
            </text>
            
            <!-- 设备名称 -->
            <text
              v-if="showLabels"
              :class="`node-label`"
              text-anchor="middle"
              :dy="nodeRadius + 20"
              font-size="12"
            >
              {{ node.name }}
            </text>
            
            <!-- IP地址 -->
            <text
              v-if="showIPs && node.ip"
              :class="`node-ip`"
              text-anchor="middle"
              :dy="nodeRadius + (showLabels ? 35 : 20)"
              font-size="10"
              fill="#666"
            >
              {{ node.ip }}
            </text>
            
            <!-- 端口显示 -->
            <g v-if="showPorts && node.ports" class="node-ports">
              <circle
                v-for="(port, index) in node.ports.slice(0, 8)"
                :key="port.id"
                :cx="getPortPosition(index, node.ports.length).x"
                :cy="getPortPosition(index, node.ports.length).y"
                r="4"
                :class="`port-dot ${port.is_connected ? 'connected' : 'disconnected'}`"
                :title="port.port_name"
              />
            </g>
          </g>
          
          <!-- 拖拽预览 - 显示节点将要放置的位置，放在最后以免干扰事件 -->
          <g
            v-if="isDragging && dragNode"
            class="drag-preview"
            :transform="getDragPreviewTransform()"
          >
            <!-- 预览圆圈 -->
            <circle
              :r="nodeRadius"
              class="preview-circle"
            />
            <!-- 预览图标 -->
            <text
              class="preview-icon"
              text-anchor="middle"
              dy="0.35em"
              font-size="24"
            >
              {{ dragNode.icon || getDeviceIcon(dragNode.type) }}
            </text>
          </g>
        </g>
      </svg>
    </div>

    <!-- 设备详情弹窗 - 右上角位置 -->
    <transition name="slide-in">
      <div v-if="selectedNode" class="device-panel">
        <div class="panel-header">
          <div class="panel-title">
            <div class="device-icon">{{ getDeviceIcon(selectedNode.type) }}</div>
            <div class="device-name-status">
              <h3>{{ selectedNode.name }}</h3>
              <span :class="`status-badge status-${selectedNode.status}`">
                <span class="status-dot"></span>
                {{ selectedNode.status }}
              </span>
            </div>
          </div>
          <button @click="closePanel" class="close-button">✕</button>
        </div>
        
        <div class="panel-body">
          <!-- 精美的标签页导航 -->
          <div class="tab-navigation">
            <button 
              v-for="tab in detailTabs" 
              :key="tab.key"
              :class="['tab-button', { active: activeDetailTab === tab.key }]"
              @click="handleTabClick(tab.key)"
            >
              <span class="tab-icon">{{ getTabIcon(tab.key) }}</span>
              <span class="tab-text">{{ tab.label }}</span>
            </button>
          </div>

          <!-- 基本信息标签页 -->
          <div v-show="activeDetailTab === 'basic'" class="tab-content">
            <div class="device-info">
              <div class="info-card">
                <div class="info-header">
                  <span class="info-icon">🏷️</span>
                  <span class="info-title">设备标识</span>
                </div>
                <div class="info-grid">
                  <div class="info-item">
                    <label>设备名称</label>
                    <div class="info-value">
                      <input 
                        v-if="isEditingDevice" 
                        v-model="deviceEditForm.name" 
                        class="input-field"
                        placeholder="设备名称"
                      />
                      <span v-else class="value-text">{{ selectedNode.name }}</span>
                    </div>
                  </div>
                  
                  <div class="info-item">
                    <label>设备类型</label>
                    <div class="info-value">
                      <select 
                        v-if="isEditingDevice" 
                        v-model="deviceEditForm.type" 
                        class="select-field"
                      >
                        <option value="交换机">🔀 交换机</option>
                        <option value="路由器">📡 路由器</option>
                        <option value="防火墙">🛡️ 防火墙</option>
                        <option value="服务器">🖥️ 服务器</option>
                        <option value="工作站">💻 工作站</option>
                      </select>
                      <span v-else class="value-text type-tag">
                        {{ getDeviceIcon(selectedNode.type) }} {{ selectedNode.type }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="info-card">
                <div class="info-header">
                  <span class="info-icon">🌐</span>
                  <span class="info-title">网络配置</span>
                </div>
                <div class="info-grid">
                  <div class="info-item">
                    <label>IP地址</label>
                    <div class="info-value">
                      <input 
                        v-if="isEditingDevice" 
                        v-model="deviceEditForm.ip" 
                        class="input-field"
                        placeholder="IP地址"
                      />
                      <span v-else class="value-text ip-address">{{ selectedNode.ip || '-' }}</span>
                    </div>
                  </div>
                  
                  <div class="info-item">
                    <label>设备状态</label>
                    <div class="info-value">
                      <select 
                        v-if="isEditingDevice" 
                        v-model="deviceEditForm.status" 
                        class="select-field"
                      >
                        <option value="正常">🟢 正常</option>
                        <option value="维护">🟡 维护</option>
                        <option value="故障">🔴 故障</option>
                        <option value="离线">⚫ 离线</option>
                      </select>
                      <span v-else :class="`status-chip status-${selectedNode.status}`">
                        {{ selectedNode.status }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="info-card">
                <div class="info-header">
                  <span class="info-icon">📋</span>
                  <span class="info-title">设备详情</span>
                </div>
                <div class="info-grid">
                  <div class="info-item">
                    <label>设备型号</label>
                    <div class="info-value">
                      <input 
                        v-if="isEditingDevice" 
                        v-model="deviceEditForm.model" 
                        class="input-field"
                        placeholder="设备型号"
                      />
                      <span v-else class="value-text">{{ selectedNode.model || '-' }}</span>
                    </div>
                  </div>
                  
                  <div class="info-item">
                    <label>设备品牌</label>
                    <div class="info-value">
                      <input 
                        v-if="isEditingDevice" 
                        v-model="deviceEditForm.brand" 
                        class="input-field"
                        placeholder="设备品牌"
                      />
                      <span v-else class="value-text">{{ selectedNode.brand || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 端口管理标签页 -->
          <div v-show="activeDetailTab === 'ports'" class="tab-content">
            <div class="ports-section">
              <div class="section-header">
                <h4>端口信息 <span class="port-count">({{ selectedNode.ports?.length || 0 }})</span></h4>
                <button @click="refreshDevicePorts" class="refresh-button">
                  🔄 刷新
                </button>
              </div>
              
              <div v-if="selectedNode.ports?.length" class="ports-grid">
                <div 
                  v-for="port in selectedNode.ports" 
                  :key="port.id"
                  :class="['port-card', { 'port-connected': port.is_connected }]"
                >
                  <div class="port-header">
                    <div class="port-name-section">
                      <span class="port-name">{{ port.port_name }}</span>
                      <span v-if="port.port_type" class="port-type-badge">{{ getPortTypeIcon(port.port_type) }} {{ port.port_type }}</span>
                    </div>
                    <div class="port-actions">
                      <span :class="`connection-indicator ${port.is_connected ? 'connected' : 'disconnected'}`">
                        <span class="indicator-dot"></span>
                        {{ port.is_connected ? '已连接' : '未连接' }}
                      </span>
                      <!-- 端口操作按钮 -->
                      <button 
                        v-if="port.is_connected" 
                        @click="disconnectPort(port)"
                        class="port-action-btn disconnect-btn"
                        title="断开连接"
                      >
                        🔌 断开
                      </button>
                      <button 
                        v-else 
                        @click="connectPort(port)"
                        class="port-action-btn connect-btn"
                        title="创建连接"
                      >
                        🔗 连接
                      </button>
                    </div>
                  </div>
                  
                  <div class="port-details">
                    <div class="port-basic-info">
                      <div class="info-item">
                        <span class="info-label">状态:</span>
                        <div class="status-display">
                          <span :class="`status-dot status-${(port as any).status}`"></span>
                          <span class="status-text">{{ (port as any).status || '未知' }}</span>
                        </div>
                      </div>
                      <div v-if="port.port_speed" class="info-item">
                        <span class="info-label">速率:</span>
                        <span class="speed-badge">{{ port.port_speed }}</span>
                      </div>
                      <div v-if="port.vlan_id" class="info-item">
                        <span class="info-label">VLAN:</span>
                        <span class="vlan-badge">{{ port.vlan_id }}</span>
                      </div>
                    </div>
                    
                    <!-- 连接信息显示 -->
                    <div v-if="port.is_connected && (port as any).connection_info" class="connection-details">
                      <div class="connection-header">
                        <span class="connection-icon">🔗</span>
                        <span class="connection-title">连接信息</span>
                      </div>
                      
                      <div class="connected-device">
                        <!-- 目标设备信息突出显示 -->
                        <div class="target-device-card">
                          <div class="device-header">
                            <span class="device-icon">🎯</span>
                            <span class="target-label">连接到</span>
                          </div>
                          <div class="device-name-highlight">{{ (port as any).connection_info.device_name }}</div>
                          <div class="port-name-highlight">🔌 {{ (port as any).connection_info.port_name }}</div>
                        </div>
                        
                        <!-- 线缆信息 -->
                        <div v-if="(port as any).connection_info.cable_type" class="cable-info">
                          <div class="cable-type">
                            <span class="cable-icon">{{ getCableTypeIcon((port as any).connection_info.cable_type) }}</span>
                            <span>{{ getCableTypeName((port as any).connection_info.cable_type) }}</span>
                          </div>
                          <div v-if="(port as any).connection_info.cable_length" class="cable-length">
                            📌 {{ (port as any).connection_info.cable_length }}m
                          </div>
                        </div>
                        
                        <!-- 连接时间 -->
                        <div v-if="(port as any).connection_info.connection_time" class="connection-time">
                          🕰️ 连接时间: {{ formatConnectionTime((port as any).connection_info.connection_time) }}
                        </div>
                      </div>
                    </div>
                    
                    <!-- 未连接提示 -->
                    <div v-else-if="!port.is_connected" class="unconnected-hint">
                      <span class="hint-icon">💭</span>
                      <span class="hint-text">此端口尚未连接其他设备</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else class="empty-state">
                <div class="empty-icon">🔌</div>
                <p>暂无端口信息</p>
              </div>
            </div>
          </div>

          <!-- 故障管理标签页 -->
          <div v-show="activeDetailTab === 'fault'" class="tab-content">
            <div class="fault-section">
              <h4>故障报告</h4>
              
              <div class="fault-form">
                <div class="form-field">
                  <label>故障描述</label>
                  <textarea 
                    v-model="faultDescription" 
                    class="textarea-field"
                    placeholder="请详细描述故障现象，包括发生时间、具体症状等..."
                    rows="4"
                  ></textarea>
                </div>
                
                <div class="form-actions">
                  <button @click="submitDeviceFault" class="action-button warning" :disabled="!faultDescription">
                    📋 提交故障报告
                  </button>
                  <button @click="faultDescription = ''" class="action-button secondary">
                    🔄 重置
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-footer">
          <div class="footer-actions">
            <button v-if="activeDetailTab === 'basic' && !isEditingDevice" @click="startEditDevice" class="action-button primary">
              ✏️ 编辑设备
            </button>
            <button v-if="isEditingDevice" @click="saveDeviceEdit" class="action-button success" :disabled="savingDevice">
              💾 {{ savingDevice ? '保存中...' : '保存更改' }}
            </button>
            <button v-if="isEditingDevice" @click="cancelDeviceEdit" class="action-button secondary">
              ❌ 取消编辑
            </button>
            <button @click="closePanel" class="action-button secondary">
              关闭
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 连接线详情提示 -->
    <div v-if="hoveredEdge" class="edge-tooltip" :style="tooltipStyle">
      <div class="tooltip-content">
        <strong>网络连接</strong><br>
        {{ hoveredEdge.source_port }} ↔ {{ hoveredEdge.target_port }}
      </div>
    </div>

    <!-- 连接管理对话框 -->
    <ConnectionDialog 
      :show="showConnectionDialog" 
      :editConnection="editingConnection"
      :preSelectedSource="selectedSourcePort"
      @close="closeConnectionDialog"
      @connected="handleConnectionCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { networkApi, type TopologyNode, type TopologyEdge } from '@/api/network'
import { portApi } from '@/api/port'
import { assetApi } from '@/api/asset'
import type { NetworkPort, TopologyFilter } from '@/types/common'
import html2canvas from 'html2canvas'
import ConnectionDialog from '@/components/network/ConnectionDialog.vue'

// 响应式数据
const loading = ref(false)
const nodes = ref<TopologyNode[]>([])
const edges = ref<TopologyEdge[]>([])
const selectedNode = ref<TopologyNode | null>(null)
const hoveredEdge = ref<TopologyEdge | null>(null)
const editingConnection = ref<TopologyEdge | null>(null)
const updateTime = ref('')
const showConnectionDialog = ref(false)

// 拖拽状态
const isDragging = ref(false)
const dragNode = ref<TopologyNode | null>(null)
const dragStartPosition = reactive({ x: 0, y: 0 }) // 拖拽开始时的鼠标位置
const currentMousePosition = reactive({ x: 0, y: 0 }) // 当前鼠标位置
const dragOffset = reactive({ x: 0, y: 0 }) // 鼠标相对于节点的偏移

// 视图控制
const scale = ref(1)
const translate = reactive({ x: 0, y: 0 })
const nodeRadius = 30

// 设备详情弹窗状态
const activeDetailTab = ref('basic')
const isEditingDevice = ref(false)
const savingDevice = ref(false)
const faultDescription = ref('')

// 端口连接状态
const selectedSourcePort = ref<{
  asset_id?: number
  asset_name?: string
  port_id?: number
  port_name?: string
} | null>(null)

// 设备编辑表单
const deviceEditForm = reactive({
  name: '',
  type: '',
  ip: '',
  status: '',
  model: '',
  brand: ''
})

// 设备详情标签页配置
const detailTabs = [
  { key: 'basic', label: '基本信息' },
  { key: 'ports', label: '端口管理' },
  { key: 'fault', label: '故障管理' }
]

// 工具提示位置
const tooltipStyle = reactive({
  left: '0px',
  top: '0px'
})

// 加载拓扑数据
const loadTopology = async () => {
  loading.value = true
  try {
    const response = await networkApi.getNetworkTopology()
    if (response.success) {
      nodes.value = response.data.nodes
      edges.value = response.data.edges
      updateTime.value = response.data.updated_at
      
      // 初始化节点位置
      initializeNodePositions()
    }
  } catch (error) {
    console.error('加载拓扑失败:', error)
  } finally {
    loading.value = false
  }
}

// 初始化节点位置
const initializeNodePositions = () => {
  const centerX = 400
  const centerY = 300
  const radius = 200
  
  console.log('初始化节点位置，节点数量:', nodes.value.length)
  
  nodes.value.forEach((node: TopologyNode, index: number) => {
    if (typeof node.x !== 'number' || typeof node.y !== 'number') {
      const angle = (index * 2 * Math.PI) / nodes.value.length
      node.x = centerX + radius * Math.cos(angle)
      node.y = centerY + radius * Math.sin(angle)

    } else {

    }
  })
}

// 获取设备图标
const getDeviceIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    '交换机': '🔀',
    '路由器': '📡',
    '防火墙': '🛡️',
    '安全设备': '🔒',
    '服务器': '🖥️',
    '工作站': '💻',
    'switch': '🔀',
    'router': '📡',
    'firewall': '🛡️',
    'server': '🖥️',
    'workstation': '💻'
  }
  return iconMap[type.toLowerCase()] || '📱'
}

// 获取标签页图标
const getTabIcon = (tabKey: string) => {
  const iconMap: Record<string, string> = {
    'basic': '📋',
    'ports': '🔌',
    'fault': '⚠️'
  }
  return iconMap[tabKey] || '📄'
}

// 获取端口类型图标
const getPortTypeIcon = (portType: string) => {
  const iconMap: Record<string, string> = {
    'ethernet': '🔌',
    'fiber': '🔆',
    'console': '📺',
    'management': '⚙️',
    'power': '🔌',
    'usb': '🔌'
  }
  return iconMap[portType.toLowerCase()] || '🔌'
}

// 获取线缆类型图标
const getCableTypeIcon = (cableType: string) => {
  const iconMap: Record<string, string> = {
    'copper': '📞',
    'fiber': '🔆',
    'wireless': '📶'
  }
  return iconMap[cableType.toLowerCase()] || '📞'
}

// 获取线缆类型名称
const getCableTypeName = (cableType: string) => {
  const nameMap: Record<string, string> = {
    'copper': '铜缆',
    'fiber': '光纤',
    'wireless': '无线'
  }
  return nameMap[cableType.toLowerCase()] || cableType
}

// 格式化连接时间
const formatConnectionTime = (timeStr: string) => {
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return timeStr
  }
}

// 计算节点的实际显示位置
const getNodeTransform = (node: TopologyNode) => {
  // 拖拽时节点保持原位，不使用临时位置
  const x = node.x
  const y = node.y
  
  return `translate(${x}, ${y})`
}

// 计算拖拽预览位置
const getDragPreviewTransform = () => {
  if (!isDragging.value || !dragNode.value) return ''
  
  // 计算预览位置：当前鼠标位置减去偏移量
  const previewX = currentMousePosition.x - dragOffset.x
  const previewY = currentMousePosition.y - dragOffset.y
  
  return `translate(${previewX}, ${previewY})`
}

// 样式类名生成
const getNodeClass = (node: TopologyNode) => {
  const classes = ['node', `node-${node.type}`, `node-${node.status}`]
  if (node.highlighted) classes.push('highlighted')
  if (node.selected) classes.push('selected')
  if (node.device_category) classes.push(`category-${node.device_category}`)
  return classes.join(' ')
}

const getNodeBgClass = (node: TopologyNode) => {
  return `node-bg status-${node.status} category-${node.device_category || 'default'}`
}

const getEdgeClass = (edge: TopologyEdge) => {
  const classes = ['edge', 'edge-network']
  if (edge.highlighted) classes.push('highlighted')
  if (edge.link_status === 'down') classes.push('link-down')
  return classes.join(' ')
}

const getEdgeColor = (edge: TopologyEdge) => {
  if (edge.link_status === 'down') return '#f56c6c'
  if (edge.link_status === 'up') return '#67c23a'
  return '#409eff'
}

// 边事件处理
const handleEdgeHover = (edge: TopologyEdge, event: MouseEvent) => {
  hoveredEdge.value = edge
  
  // 更新工具提示位置
  tooltipStyle.left = event.clientX + 10 + 'px'
  tooltipStyle.top = event.clientY - 10 + 'px'
}

const handleEdgeLeave = () => {
  hoveredEdge.value = null
}

const handleEdgeClick = (edge: TopologyEdge) => {
  console.log('连接详情:', edge)
  // 打开编辑连接对话框
  editingConnection.value = edge
  showConnectionDialog.value = true
}

// 新增功能状态
const searchKeyword = ref('')
const showFilters = ref(false)
const layoutAlgorithm = ref('force')
const showPorts = ref(false)
const showLabels = ref(true)
const showIPs = ref(true)
const selectedNodes = ref<TopologyNode[]>([])

// 过滤器状态
const activeFilters = reactive<TopologyFilter>({
  device_types: [],
  statuses: [],
  categories: [],
  show_disconnected: true
})

// 设备类型和状态选项
const deviceTypes = computed(() => {
  const types = new Set(nodes.value.map(node => node.type))
  return Array.from(types)
})

const deviceStatuses = computed(() => {
  const statuses = new Set(nodes.value.map(node => node.status))
  return Array.from(statuses)
})

// 过滤后的节点和边
const filteredNodes = computed(() => {
  let filtered = nodes.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(node => 
      node.name.toLowerCase().includes(keyword) ||
      node.ip?.toLowerCase().includes(keyword) ||
      node.type.toLowerCase().includes(keyword)
    )
  }

  // 类型过滤
  if (activeFilters.device_types && activeFilters.device_types.length > 0) {
    filtered = filtered.filter(node => activeFilters.device_types!.includes(node.type))
  }

  // 状态过滤
  if (activeFilters.statuses && activeFilters.statuses.length > 0) {
    filtered = filtered.filter(node => activeFilters.statuses!.includes(node.status))
  }

  return filtered
})

const filteredEdges = computed(() => {
  const visibleNodeIds = new Set(filteredNodes.value.map(node => node.id))
  return edges.value.filter(edge => 
    visibleNodeIds.has(edge.source_id) && visibleNodeIds.has(edge.target_id)
  )
})

// 事件处理函数
const handleSearch = () => {
  nodes.value.forEach(node => node.highlighted = false)
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filteredNodes.value.forEach(node => {
      if (node.name.toLowerCase().includes(keyword) ||
          node.ip?.toLowerCase().includes(keyword)) {
        node.highlighted = true
      }
    })
  }
}

const focusDevice = () => {
  if (!searchKeyword.value) return
  
  const keyword = searchKeyword.value.toLowerCase()
  const targetNode = filteredNodes.value.find(node => 
    node.name.toLowerCase().includes(keyword) ||
    node.ip?.toLowerCase().includes(keyword)
  )
  
  if (targetNode && targetNode.x && targetNode.y) {
    const canvasRect = document.querySelector('.topology-svg')?.getBoundingClientRect()
    if (canvasRect) {
      translate.x = canvasRect.width / 2 - targetNode.x * scale.value
      translate.y = canvasRect.height / 2 - targetNode.y * scale.value
      targetNode.highlighted = true
      selectedNode.value = targetNode
    }
  }
}

const applyFilters = () => {
  // 过滤逻辑已在computed中实现
}

const clearFilters = () => {
  searchKeyword.value = ''
  activeFilters.device_types = []
  activeFilters.statuses = []
  activeFilters.show_disconnected = true
  
  // 清除高亮
  nodes.value.forEach(node => {
    node.highlighted = false
    node.selected = false
  })
}

const autoLayout = () => {
  if (layoutAlgorithm.value === 'manual') return
  applyLocalLayout()
}

const applyLocalLayout = () => {
  const centerX = 400
  const centerY = 300
  
  switch (layoutAlgorithm.value) {
    case 'circular':
      applyCircularLayout(centerX, centerY)
      break
    case 'grid':
      applyGridLayout()
      break
    case 'force':
      applyForceLayout()
      break
  }
}

const applyCircularLayout = (centerX: number, centerY: number) => {
  const radius = Math.min(200, nodes.value.length * 30)
  nodes.value.forEach((node, index) => {
    const angle = (index * 2 * Math.PI) / nodes.value.length
    node.x = centerX + radius * Math.cos(angle)
    node.y = centerY + radius * Math.sin(angle)
  })
}

const applyGridLayout = () => {
  const cols = Math.ceil(Math.sqrt(nodes.value.length))
  const spacing = 100
  nodes.value.forEach((node, index) => {
    node.x = (index % cols) * spacing + 100
    node.y = Math.floor(index / cols) * spacing + 100
  })
}

const applyForceLayout = () => {
  initializeNodePositions()
}

const togglePorts = () => {
  // 端口显示切换
}

const fitToScreen = () => {
  if (nodes.value.length === 0) return
  
  const canvasRect = document.querySelector('.topology-svg')?.getBoundingClientRect()
  if (!canvasRect) return
  
  const bounds = nodes.value.reduce((acc, node) => {
    if (node.x && node.y) {
      acc.minX = Math.min(acc.minX, node.x)
      acc.maxX = Math.max(acc.maxX, node.x)
      acc.minY = Math.min(acc.minY, node.y)
      acc.maxY = Math.max(acc.maxY, node.y)
    }
    return acc
  }, { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity })
  
  if (bounds.minX === Infinity) return
  
  const nodesBounds = {
    width: bounds.maxX - bounds.minX + nodeRadius * 2,
    height: bounds.maxY - bounds.minY + nodeRadius * 2,
    centerX: (bounds.minX + bounds.maxX) / 2,
    centerY: (bounds.minY + bounds.maxY) / 2
  }
  
  const scaleX = (canvasRect.width * 0.8) / nodesBounds.width
  const scaleY = (canvasRect.height * 0.8) / nodesBounds.height
  scale.value = Math.min(scaleX, scaleY, 2)
  
  translate.x = canvasRect.width / 2 - nodesBounds.centerX * scale.value
  translate.y = canvasRect.height / 2 - nodesBounds.centerY * scale.value
}

// 根据ID获取节点
const getNodeById = (id: number) => {
  return nodes.value.find(node => node.id === id)
}

// 节点交互事件
const handleNodeHover = (node: TopologyNode, event: MouseEvent) => {
  // 显示设备详情提示

}

const handleNodeLeave = () => {
  // 隐藏提示
}

// 端口位置计算
const getPortPosition = (index: number, totalPorts: number) => {
  const angle = (index * 2 * Math.PI) / Math.min(totalPorts, 8)
  const radius = nodeRadius + 12
  return {
    x: radius * Math.cos(angle),
    y: radius * Math.sin(angle)
  }
}
// 获取SVG坐标的辅助函数
const getSVGCoordinates = (event: MouseEvent) => {
  const svg = document.querySelector('.topology-svg') as SVGSVGElement
  if (!svg) return { x: 0, y: 0 }
  
  // 使用SVG的getScreenCTM方法获取变换矩阵
  const CTM = svg.getScreenCTM()
  if (!CTM) return { x: 0, y: 0 }
  
  // 将屏幕坐标转换为SVG坐标
  return {
    x: (event.clientX - CTM.e) / CTM.a,
    y: (event.clientY - CTM.f) / CTM.d
  }
}

// 拖拽事件处理器（需要在全局可访问）
let globalDragHandlers: {
  handleMouseMove: (event: MouseEvent) => void
  handleMouseUp: () => void
} | null = null

const handleNodeMouseDown = (node: TopologyNode, event: MouseEvent) => {
  event.stopPropagation()
  
  // 确保节点有初始位置
  if (typeof node.x !== 'number' || typeof node.y !== 'number') {
    console.warn('节点缺少有效位置:', node)
    return
  }
  

  // 计算鼠标相对于SVG的位置
  const svg = document.querySelector('.topology-svg') as SVGSVGElement
  if (!svg) {
    console.error('❌ 未找到SVG元素')
    return
  }
  
  const svgRect = svg.getBoundingClientRect()
  const mouseX = event.clientX - svgRect.left
  const mouseY = event.clientY - svgRect.top
  
  // 设置拖拽状态 - 节点保持原位！
  isDragging.value = true
  dragNode.value = node
  
  // 记录拖拽开始时的位置
  dragStartPosition.x = mouseX
  dragStartPosition.y = mouseY
  currentMousePosition.x = mouseX
  currentMousePosition.y = mouseY
  
  // 计算鼠标相对于节点中心的偏移量
  dragOffset.x = mouseX - node.x
  dragOffset.y = mouseY - node.y
  

  // 添加拖拽视觉反馈（光标变化）
  document.body.style.cursor = 'grabbing'
  
  // 阻止默认行为
  event.preventDefault()
  event.stopPropagation()
  
  // 创建拖拽事件处理器
  const handleMouseMove = (event: MouseEvent) => {
    if (!isDragging.value || !dragNode.value) return
    
    const svg = document.querySelector('.topology-svg') as SVGSVGElement
    if (!svg) return
    
    const svgRect = svg.getBoundingClientRect()
    const mouseX = event.clientX - svgRect.left
    const mouseY = event.clientY - svgRect.top
    
    // 只更新当前鼠标位置，节点不动
    currentMousePosition.x = mouseX
    currentMousePosition.y = mouseY
    

    event.preventDefault()
  }
  
  const handleMouseUp = (event: MouseEvent) => {
    if (!isDragging.value || !dragNode.value) return
    
    const svg = document.querySelector('.topology-svg') as SVGSVGElement
    if (!svg) return
    
    const svgRect = svg.getBoundingClientRect()
    const mouseX = event.clientX - svgRect.left
    const mouseY = event.clientY - svgRect.top
    
    // 计算节点的新位置（鼠标位置减去偏移量）
    const newX = mouseX - dragOffset.x
    const newY = mouseY - dragOffset.y
    

    // 现在才真正移动节点到最终位置
    dragNode.value.x = newX
    dragNode.value.y = newY
    
    // 重置拖拽状态
    isDragging.value = false
    dragNode.value = null
    dragStartPosition.x = 0
    dragStartPosition.y = 0
    currentMousePosition.x = 0
    currentMousePosition.y = 0
    dragOffset.x = 0
    dragOffset.y = 0
    
    // 恢复光标
    document.body.style.cursor = ''
    
    // 移除事件监听器
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  // 在document上添加事件监听器
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleNodeClick = (node: TopologyNode, event: MouseEvent) => {
  event.stopPropagation()
  // 只有在没有拖拽时才选中节点
  if (!isDragging.value) {
    selectedNode.value = node
    // 自动切换到端口管理标签页并刷新端口信息
    activeDetailTab.value = 'basic'
    // 延迟刷新端口信息，确保面板已渲染
    setTimeout(() => {
      refreshDevicePorts()
    }, 100)
  }
}

const handleCanvasClick = () => {
  selectedNode.value = null
}



// 工具栏功能
const refreshTopology = () => {
  loadTopology()
}

const saveTopology = async () => {
  try {
    const topologyData = { nodes, edges }
    await networkApi.saveNetworkTopology({
      name: '当前拓扑',
      description: '用户保存的网络拓扑',
      topology_data: topologyData
    })
    console.log('拓扑保存成功')
  } catch (error) {
    console.error('保存拓扑失败:', error)
  }
}

const exportTopology = async () => {
  try {
    const svgElement = document.querySelector('.topology-svg') as SVGElement
    if (!svgElement) {
      alert('找不到拓扑图元素')
      return
    }
    
    // 获取SVG的父容器
    const container = svgElement.parentElement as HTMLElement
    if (!container) {
      alert('找不到容器元素')
      return
    }
    
    // 使用html2canvas截取整个容器
    const canvas = await html2canvas(container, {
      backgroundColor: '#ffffff',
      scale: 2, // 提高分辨率
      useCORS: true,
      allowTaint: true,
      width: container.offsetWidth,
      height: container.offsetHeight
    })
    
    // 创建下载链接
    const link = document.createElement('a')
    link.download = `网络拓扑图_${new Date().toISOString().slice(0, 19).replace(/[T:]/g, '_')}.png`
    link.href = canvas.toDataURL('image/png')
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    console.log('拓扑图导出成功')
  } catch (error) {
    console.error('导出拓扑图失败:', error)
    alert('导出失败，请稍后重试')
  }
}

const zoomIn = () => {
  scale.value = Math.min(scale.value * 1.2, 3)
  updateTransform()
}

const zoomOut = () => {
  scale.value = Math.max(scale.value / 1.2, 0.5)
  updateTransform()
}

const resetView = () => {
  scale.value = 1
  translate.x = 0
  translate.y = 0
  updateTransform()
}

const updateTransform = () => {
  const svg = document.querySelector('.topology-svg') as HTMLElement
  if (svg) {
    // 为了防止双重变换冲突，暂时禁用CSS transform
    // svg.style.transform = `scale(${scale.value}) translate(${translate.x}px, ${translate.y}px)`
  }
}

// 处理标签页切换
const handleTabClick = (tabKey: string) => {
  activeDetailTab.value = tabKey
  // 如果切换到端口管理标签页，刷新端口信息
  if (tabKey === 'ports') {
    refreshDevicePorts()
  }
}

// 设备面板功能
const closePanel = () => {
  selectedNode.value = null
  isEditingDevice.value = false
  activeDetailTab.value = 'basic'
}

// 开始编辑设备
const startEditDevice = () => {
  if (selectedNode.value) {
    Object.assign(deviceEditForm, {
      name: selectedNode.value.name || '',
      type: selectedNode.value.type || '',
      ip: selectedNode.value.ip || '',
      status: selectedNode.value.status || '',
      model: selectedNode.value.model || '',
      brand: selectedNode.value.brand || ''
    })
    isEditingDevice.value = true
  }
}

// 取消编辑设备
const cancelDeviceEdit = () => {
  isEditingDevice.value = false
}

// 保存设备编辑
const saveDeviceEdit = async () => {
  if (!selectedNode.value) return
  
  savingDevice.value = true
  try {
    // 根据设备类型选择对应的API
    if (selectedNode.value.device_category === 'topology') {
      await networkApi.updateDevice(selectedNode.value.id, deviceEditForm as any)
    } else {
      await assetApi.updateAsset(selectedNode.value.id, deviceEditForm as any)
    }
    
    // 更新本地设备数据
    Object.assign(selectedNode.value, deviceEditForm)
    
    isEditingDevice.value = false
    alert('设备信息更新成功!')
  } catch (error) {
    console.error('更新设备失败:', error)
    alert('更新设备失败，请重试')
  } finally {
    savingDevice.value = false
  }
}

// 刷新设备端口
const refreshDevicePorts = async () => {
  if (!selectedNode.value) return
  
  try {
    const response = await portApi.getAssetPorts(selectedNode.value.id)
    if (response.success && selectedNode.value) {
      // 为每个端口设置详细的连接信息
      selectedNode.value.ports = response.data.ports?.map((port: any) => ({
        ...port,
        status: port.port_status || 'unknown',
        // 从后端数据中获取连接设备信息（尝试多个可能的字段名）
        connected_device_name: port.connected_asset_name || port.connected_device_name || port.target_device_name || null,
        connected_port_name: port.connected_port_name || port.target_port_name || null,
        connected_asset_id: port.connected_asset_id || port.target_asset_id || null,
        // 添加连接详情
        connection_info: port.is_connected ? {
          device_name: port.connected_asset_name || port.connected_device_name || port.target_device_name,
          port_name: port.connected_port_name || port.target_port_name,
          cable_type: port.cable_type,
          cable_length: port.cable_length,
          connection_time: port.last_link_time
        } : null
      })) as any || []
    }
  } catch (error) {
    console.error('刷新端口失败:', error)
  }
}

// 断开端口连接
const disconnectPort = async (port: any) => {
  if (!confirm(`确认断开端口 ${port.port_name} 的连接吗？`)) return
  
  try {
    const response = await portApi.disconnectPort(port.id)
    if (response.success) {
      // 刷新端口信息
      await refreshDevicePorts()
      // 重新加载拓扑数据以更新连接线
      await loadTopology()
      alert('端口连接已断开')
    }
  } catch (error) {
    console.error('断开端口连接失败:', error)
    alert('断开连接失败，请重试')
  }
}

// 连接端口
const connectPort = (port: any) => {
  // 打开连接对话框，并预填充源端口信息
  selectedSourcePort.value = {
    asset_id: selectedNode.value?.id,
    asset_name: selectedNode.value?.name,
    port_id: port.id,
    port_name: port.port_name
  }
  showConnectionDialog.value = true
}

// 提交故障报告
const submitDeviceFault = async () => {
  if (!selectedNode.value || !faultDescription.value.trim()) return
  
  try {
    await networkApi.markDeviceFault(selectedNode.value.id, faultDescription.value)
    
    // 更新设备状态为故障
    if (selectedNode.value) {
      selectedNode.value.status = '故障'
    }
    
    alert('故障报告提交成功!')
    faultDescription.value = ''
  } catch (error) {
    console.error('提交故障报告失败:', error)
    alert('提交故障报告失败，请重试')
  }
}

// 旧的操作按钮函数(保持兼容性)
const editDevice = () => {
  startEditDevice()
}

const markFault = () => {
  activeDetailTab.value = 'fault'
}

const viewPorts = () => {
  activeDetailTab.value = 'ports'
  refreshDevicePorts()
}

// 处理连接创建成功
const handleConnectionCreated = (connection: any) => {
  console.log('连接创建成功:', connection)
  // 重新加载拓扑数据以显示新连接
  loadTopology()
}

const closeConnectionDialog = () => {
  showConnectionDialog.value = false
  editingConnection.value = null
  selectedSourcePort.value = null
}

const openNewConnection = () => {
  editingConnection.value = null
  showConnectionDialog.value = true
}

// 初始化
loadTopology()
</script>

<style scoped>
.topology-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.toolbar-left h1 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
  justify-content: center;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input {
  width: 300px;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
}

.search-btn, .focus-btn {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-toggle {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.filter-toggle.active {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

.layout-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.layout-select {
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
}

.display-options {
  display: flex;
  gap: 12px;
}

.display-options label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  cursor: pointer;
}

.update-time {
  color: #909399;
  font-size: 14px;
  margin-left: 16px;
}

.topology-stats {
  display: flex;
  gap: 16px;
  margin-left: 20px;
}

.stat-item {
  color: #606266;
  font-size: 14px;
}

/* 过滤器面板 */
.filter-panel {
  background: white;
  border-bottom: 1px solid #ebeef5;
  padding: 16px 24px;
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.filter-section {
  min-width: 150px;
}

.filter-section h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-options label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  cursor: pointer;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.status-正常 { background: #67c23a; }
.status-dot.status-故障 { background: #f56c6c; }
.status-dot.status-维护 { background: #e6a23c; }
.status-dot.status-离线 { background: #909399; }

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.view-controls {
  display: flex;
  gap: 6px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary { background: #409eff; color: white; }
.btn-secondary { background: #909399; color: white; }

.btn-icon {
  padding: 6px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #f8f9fa;
  border: 1px solid #dcdfe6;
}

.topology-canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: white;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 5;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.topology-svg {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.topology-svg:active {
  cursor: grabbing;
}

/* 连接线样式 */
.edge {
  stroke: #606266;
  stroke-dasharray: none;
  cursor: pointer;
  transition: all 0.3s;
}

.edge:hover {
  stroke-width: 3 !important;
}

.edge.highlighted {
  stroke: #409eff;
  stroke-width: 3;
  filter: drop-shadow(0 0 4px rgba(64, 158, 255, 0.5));
}

.edge-network {
  stroke: #409eff;
  stroke-width: 2;
}

.edge.link-down {
  stroke: #f56c6c;
  stroke-dasharray: 5,5;
}

/* 拖拽预览样式 */
.drag-preview {
  pointer-events: none; /* 禁止鼠标事件，不干扰原始节点的点击 */
  opacity: 0.6;
  z-index: 1000; /* 确保在最上层 */
}

.preview-circle {
  fill: #409eff;
  stroke: white;
  stroke-width: 3;
  stroke-dasharray: 5,5;
  animation: dash 1s linear infinite;
}

.preview-icon {
  fill: white;
  font-family: 'Segoe UI Emoji', sans-serif;
  opacity: 0.8;
}

@keyframes dash {
  to {
    stroke-dashoffset: -10;
  }
}

/* 节点样式 */
.node {
  cursor: pointer;
  transition: all 0.3s;
}

.node:hover {
  filter: drop-shadow(0 0 4px rgba(64, 158, 255, 0.4));
}

.node.dragging {
  cursor: grabbing;
  filter: drop-shadow(0 0 8px rgba(64, 158, 255, 0.8));
  /* 移除 transform: scale，防止与 SVG transform 冲突 */
  transition: none; /* 拖拽时禁用过渡动画 */
}

.node.highlighted {
  filter: drop-shadow(0 0 8px rgba(64, 158, 255, 0.6));
}

.node.selected {
  filter: drop-shadow(0 0 12px rgba(255, 193, 7, 0.8));
}

.node-glow {
  fill: none;
  stroke: #409eff;
  stroke-width: 2;
  opacity: 0.6;
  animation: pulse 2s infinite;
}

.node-glow.selected {
  stroke: #ffc107;
}

@keyframes pulse {
  0% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
  100% { opacity: 0.6; transform: scale(1); }
}

.node-bg {
  fill: #409eff;
  stroke: white;
  stroke-width: 3;
  transition: all 0.3s;
}

.node-bg.status-正常 { fill: #67c23a; }
.node-bg.status-故障 { fill: #f56c6c; }
.node-bg.status-维护 { fill: #e6a23c; }
.node-bg.status-离线 { fill: #909399; }

.node-bg.category-topology { stroke: #409eff; stroke-width: 4; }
.node-bg.category-terminal { stroke: #67c23a; stroke-width: 2; }
.node-bg.category-legacy { stroke: #c0c4cc; stroke-width: 2; }

.node-icon {
  fill: white;
  font-family: 'Segoe UI Emoji', sans-serif;
  pointer-events: none;
}

.node-label {
  fill: #303133;
  font-weight: 500;
  pointer-events: none;
}

.node-ip {
  pointer-events: none;
}

/* 端口样式 */
.port-dot {
  stroke-width: 1;
  cursor: pointer;
  transition: all 0.3s;
}

.port-dot.connected {
  fill: #67c23a;
  stroke: #409eff;
}

.port-dot.disconnected {
  fill: #f4f4f5;
  stroke: #dcdfe6;
}

.port-dot:hover {
  r: 6;
  stroke-width: 2;
}

/* 设备详情面板 - 右上角位置 */
.device-panel {
  position: fixed;
  top: 100px;
  right: 24px;
  width: 400px;
  height: calc(100vh - 140px); /* 固定高度 */
  max-height: 800px; /* 最大高度限制 */
  background: white;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12),
              0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  z-index: 1000;
  border: 1px solid #e8eaed;
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column; /* 确保内容垂直布局 */
}

/* 面板头部 */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.device-icon {
  font-size: 32px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.device-name-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.device-name-status h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
}

.status-badge .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-badge.status-正常 .status-dot { background: #4caf50; }
.status-badge.status-故障 .status-dot { background: #f44336; }
.status-badge.status-维护 .status-dot { background: #ff9800; }
.status-badge.status-离线 .status-dot { background: #9e9e9e; }

.close-button {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  font-size: 18px;
  width: 36px;
  height: 36px;
  border-radius: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

/* 面板主体 */
.panel-body {
  display: flex;
  flex-direction: column;
  flex: 1; /* 占据剩余空间 */
  overflow: hidden; /* 防止内容溢出 */
}

/* 标签页导航 */
.tab-navigation {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.tab-button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
  font-size: 13px;
  position: relative;
}

.tab-button:hover {
  background: #f5f5f5;
  color: #333;
}

.tab-button.active {
  background: white;
  color: #667eea;
  font-weight: 600;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px 3px 0 0;
}

.tab-icon {
  font-size: 18px;
}

.tab-text {
  font-size: 12px;
}

/* 标签页内容 */
.tab-content {
  padding: 20px;
  flex: 1;
  overflow-y: auto; /* 内容溢出时显示垂直滚动条 */
  overflow-x: hidden; /* 隐藏水平滚动条 */
  /* 美化滚动条 */
  scrollbar-width: thin;
  scrollbar-color: #c0c0c0 transparent;
}

/* WebKit 浏览器滚动条样式 */
.tab-content::-webkit-scrollbar {
  width: 6px;
}

.tab-content::-webkit-scrollbar-track {
  background: transparent;
}

.tab-content::-webkit-scrollbar-thumb {
  background: #c0c0c0;
  border-radius: 3px;
}

.tab-content::-webkit-scrollbar-thumb:hover {
  background: #a0a0a0;
}

/* 基本信息区域 */
.device-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 信息卡片样式 */
.info-card {
  background: white;
  border: 1px solid #e8eaed;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.info-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #667eea;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.info-icon {
  font-size: 16px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.info-title {
  font-weight: 600;
  color: #333;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 40px;
}

.info-item label {
  font-size: 13px;
  font-weight: 500;
  color: #666;
  min-width: 80px;
  text-align: left;
}

.info-value {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.value-text {
  font-size: 14px;
  color: #333;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  min-height: 38px;
  display: flex;
  align-items: center;
  width: 100%;
}

.type-tag {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border-color: #90caf9;
  color: #1976d2;
  font-weight: 500;
}

.ip-address {
  font-family: 'Courier New', monospace;
  background: linear-gradient(135deg, #f3e5f5, #e1bee7);
  border-color: #ce93d8;
  color: #7b1fa2;
}

.status-chip {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-chip.status-正常 {
  background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
  color: #2e7d32;
}

.status-chip.status-故障 {
  background: linear-gradient(135deg, #ffebee, #ffcdd2);
  color: #c62828;
}

.status-chip.status-维护 {
  background: linear-gradient(135deg, #fff3e0, #ffcc02);
  color: #ef6c00;
}

.status-chip.status-离线 {
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
  color: #424242;
}

/* 输入框和选择框 */
.input-field, .select-field {
  padding: 10px 14px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  background: white;
  width: 100%;
}

.input-field:focus, .select-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 端口管理区域 */
.ports-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.port-count {
  color: #667eea;
  font-weight: 500;
  font-size: 14px;
}

.refresh-button {
  padding: 8px 16px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
}

.refresh-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.ports-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
  max-height: calc(100vh - 350px); /* 限制最大高度，确保显示滚动条 */
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: #c1c1c1 #f1f1f1; /* Firefox */
}

/* WebKit浏览器滚动条样式 */
.ports-grid::-webkit-scrollbar {
  width: 6px;
}

.ports-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.ports-grid::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.ports-grid::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.port-card {
  background: white;
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
  min-height: 140px; /* 设置最小高度，确保内容显示完整 */
  flex-shrink: 0; /* 防止被压缩 */
}

.port-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: #e0e0e0;
  transition: all 0.2s;
}

.port-card.port-connected::before {
  background: linear-gradient(135deg, #4caf50, #8bc34a);
}

.port-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.port-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.port-name-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.port-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* 端口操作按钮 */
.port-action-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 3px;
  min-width: 60px;
  justify-content: center;
}

.disconnect-btn {
  background: linear-gradient(135deg, #ffebee, #ffcdd2);
  color: #c62828;
  border: 1px solid #ffcdd2;
}

.disconnect-btn:hover {
  background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(198, 40, 40, 0.3);
}

.connect-btn {
  background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.connect-btn:hover {
  background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(46, 125, 50, 0.3);
}

.port-name {
  font-weight: 600;
  color: #333;
  font-size: 15px;
}

.port-type-badge {
  font-size: 11px;
  padding: 2px 6px;
  background: linear-gradient(135deg, #f0f7ff, #e1f2ff);
  border: 1px solid #b3d9ff;
  border-radius: 10px;
  color: #0066cc;
  font-weight: 500;
  width: fit-content;
}

.port-basic-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.status-display {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: #333;
}

.info-label {
  font-weight: 500;
  color: #666;
}

.speed-badge {
  padding: 2px 6px;
  background: linear-gradient(135deg, #f0f9f0, #e8f5e8);
  border: 1px solid #c8e6c9;
  border-radius: 8px;
  color: #2e7d32;
  font-weight: 600;
  font-size: 10px;
}

.vlan-badge {
  padding: 2px 6px;
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
  border: 1px solid #ffcc02;
  border-radius: 8px;
  color: #ef6c00;
  font-weight: 600;
  font-size: 10px;
}

/* 连接详情样式 */
.connection-details {
  background: linear-gradient(135deg, #f8fffe, #e8f8f5);
  border: 1px solid #4caf50;
  border-radius: 10px;
  padding: 12px;
  margin-top: 8px;
  min-height: 60px; /* 设置最小高度 */
}

.connection-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  font-weight: 600;
  color: #2e7d32;
  font-size: 13px;
}

.connection-icon {
  font-size: 16px;
}

.connected-device {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 目标设备卡片样式 */
.target-device-card {
  background: linear-gradient(135deg, #fff, #f8fff8);
  border: 2px solid #4caf50;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.1);
}

.device-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.target-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.device-name-highlight {
  font-size: 16px;
  font-weight: 700;
  color: #1976d2;
  margin-bottom: 4px;
  padding: 4px 8px;
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border-radius: 8px;
  border-left: 4px solid #1976d2;
}

.port-name-highlight {
  font-size: 14px;
  font-weight: 600;
  color: #388e3c;
  font-family: 'Courier New', monospace;
  padding: 3px 6px;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 6px;
  border-left: 3px solid #4caf50;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e8f5e8;
}

.device-icon {
  font-size: 20px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.device-details {
  flex: 1;
}

.device-name {
  font-weight: 600;
  color: #1976d2;
  font-size: 14px;
  margin-bottom: 2px;
}

.device-port {
  font-size: 12px;
  color: #666;
  font-family: 'Courier New', monospace;
}

.cable-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  font-size: 12px;
}

.cable-type {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-weight: 500;
}

.cable-icon {
  font-size: 14px;
}

.cable-length {
  color: #888;
  font-weight: 500;
  font-size: 11px;
}

.connection-time {
  font-size: 11px;
  color: #777;
  text-align: center;
  padding: 4px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 6px;
}

/* 未连接提示样式 */
.unconnected-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;
  background: linear-gradient(135deg, #fafafa, #f0f0f0);
  border: 1px dashed #ddd;
  border-radius: 8px;
  color: #999;
  font-size: 12px;
  margin-top: 8px;
}

.hint-icon {
  font-size: 14px;
  opacity: 0.7;
}

.hint-text {
  font-style: italic;
}

.connection-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
}

.connection-indicator.connected {
  background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
  color: #2e7d32;
}

.connection-indicator.disconnected {
  background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
  color: #616161;
}

.indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.connection-indicator.connected .indicator-dot {
  background: #4caf50;
  box-shadow: 0 0 4px rgba(76, 175, 80, 0.5);
}

.connection-indicator.disconnected .indicator-dot {
  background: #9e9e9e;
}

.port-details {
  color: #666;
  font-size: 13px;
  line-height: 1.4;
}

.port-status {
  margin-bottom: 4px;
}

.port-connection {
  color: #667eea;
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* 故障管理区域 */
.fault-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.fault-section h4 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.fault-form {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-field {
  margin-bottom: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-field label {
  font-size: 13px;
  font-weight: 600;
  color: #444;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.textarea-field {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  min-height: 120px;
  transition: all 0.2s;
  font-family: inherit;
}

.textarea-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 面板底部 */
.panel-footer {
  border-top: 1px solid #f0f0f0;
  padding: 16px 20px;
  background: #fafafa;
}

.footer-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 动作按钮 */
.action-button {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
  text-align: center;
}

.action-button.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.action-button.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.action-button.success {
  background: linear-gradient(135deg, #4caf50, #8bc34a);
  color: white;
}

.action-button.success:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.action-button.warning {
  background: linear-gradient(135deg, #ff9800, #ffc107);
  color: white;
}

.action-button.warning:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.action-button.secondary {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #e9ecef;
}

.action-button.secondary:hover {
  background: #e9ecef;
  color: #333;
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* 动画效果 */
.slide-in-enter-active {
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
}

.slide-in-leave-active {
  transition: all 0.3s cubic-bezier(0.755, 0.05, 0.855, 0.06);
}

.slide-in-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-in-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .device-panel {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .tab-button {
    padding: 12px 6px;
  }
  
  .tab-text {
    font-size: 11px;
  }
  
  .footer-actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
}



/* 连接线提示 */
.edge-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 30;
}

@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 12px;
  }
  
  .device-panel {
    width: 280px;
    right: 10px;
    top: 60px;
  }
  
  .panel-actions {
    flex-direction: column;
  }
}
</style>