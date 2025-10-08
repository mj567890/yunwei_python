<template>
  <div class="ports-management">
    <div class="page-header">
      <h1>端口管理</h1>
      <div class="header-actions">
        <input 
          v-model="searchKeyword" 
          type="text" 
          placeholder="搜索设备名称..."
          class="search-input"
        >
        <button @click="refreshData" :disabled="loading" class="btn btn-secondary">
          🔄 {{ loading ? '刷新中...' : '刷新' }}
        </button>
        <button @click="exportAll" class="btn btn-info">
          📤 导出全部
        </button>
      </div>
    </div>

    <!-- 设备统计信息 -->
    <div v-if="!loading && devices.length > 0" class="statistics-summary">
      <div class="stat-card">
        <div class="stat-number">{{ devices.length }}</div>
        <div class="stat-label">网络设备</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ totalPorts }}</div>
        <div class="stat-label">总端口数</div>
      </div>
      <div class="stat-card">
        <div class="stat-number connected">{{ totalConnectedPorts }}</div>
        <div class="stat-label">已连接</div>
      </div>
      <div class="stat-card">
        <div class="stat-number available">{{ totalAvailablePorts }}</div>
        <div class="stat-label">可用端口</div>
      </div>
    </div>

    <!-- 设备列表 -->
    <div class="device-grid">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载设备数据中...</p>
      </div>

      <div v-else-if="filteredDevices.length === 0 && searchKeyword.trim()" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>没有找到匹配的设备</p>
        <button @click="searchKeyword = ''" class="btn btn-secondary">清除搜索</button>
      </div>

      <div v-else-if="devices.length === 0" class="empty-state">
        <div class="empty-icon">📱</div>
        <p>暂无网络设备</p>
        <router-link to="/app/assets/create" class="btn btn-primary">添加设备</router-link>
      </div>

      <div v-else class="device-cards">
        <!-- 加载更多按钮 -->
        <div v-if="displayedDevices.length < filteredDevices.length" class="load-more-container">
          <button @click="loadMoreDevices" class="btn btn-outline load-more-btn">
            加载更多设备 ({{ displayedDevices.length }}/{{ filteredDevices.length }})
          </button>
        </div>
        
        <div
          v-for="device in displayedDevices"
          :key="device.id"
          class="device-card"
          @click="viewDevicePorts(device)"
        >
          <div class="device-header">
            <div class="device-icon">{{ getDeviceIcon(device.category) }}</div>
            <div class="device-info">
              <h3>{{ device.name }}</h3>
              <span class="device-category">{{ device.category }}</span>
            </div>
            <div :class="`device-status status-${getStatusClass(device.status)}`">
              {{ device.status }}
            </div>
          </div>

          <div class="device-details">
            <div class="detail-item">
              <label>IP地址:</label>
              <span>{{ device.ip_address || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>位置:</label>
              <span>{{ device.user_department || '-' }}</span>
            </div>
          </div>

          <div class="port-summary">
            <div class="port-stat">
              <span class="stat-number">{{ device.port_count || 0 }}</span>
              <span class="stat-label">总端口</span>
            </div>
            <div class="port-stat">
              <span class="stat-number connected">{{ device.connected_ports || 0 }}</span>
              <span class="stat-label">已连接</span>
            </div>
            <div class="port-stat">
              <span class="stat-number available">{{ (device.port_count || 0) - (device.connected_ports || 0) }}</span>
              <span class="stat-label">可用</span>
            </div>
          </div>

          <div class="device-actions">
            <button 
              @click.stop="viewDevicePorts(device)" 
              class="btn btn-primary btn-sm"
            >
              管理端口
            </button>
            <button 
              @click.stop="quickAddPort(device)" 
              class="btn btn-success btn-sm"
            >
              快速添加
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速添加端口对话框 -->
    <div v-if="showQuickAdd" class="modal-overlay" @click="closeQuickAdd">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>快速添加端口 - {{ selectedDevice?.name }}</h3>
          <button @click="closeQuickAdd" class="close-btn">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="quick-add-options">
            <div class="option-card" @click="batchAddPorts('switch')">
              <div class="option-icon">🔀</div>
              <div class="option-title">交换机端口</div>
              <div class="option-desc">自动创建24个千兆以太网端口</div>
            </div>
            
            <div class="option-card" @click="batchAddPorts('router')">
              <div class="option-icon">📡</div>
              <div class="option-title">路由器端口</div>
              <div class="option-desc">创建基础网络接口端口</div>
            </div>
            
            <div class="option-card" @click="batchAddPorts('server')">
              <div class="option-icon">🖥️</div>
              <div class="option-title">服务器端口</div>
              <div class="option-desc">创建网络和管理端口</div>
            </div>
            
            <div class="option-card" @click="batchAddPorts('custom')">
              <div class="option-icon">⚙️</div>
              <div class="option-title">自定义配置</div>
              <div class="option-desc">手动配置端口信息</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { assetApi, type Asset } from '@/api/asset'
import { portApi, type PortStatistics } from '@/api/port'

const router = useRouter()

// 数据
const loading = ref(false)
const devices = ref<Asset[]>([])
const selectedDevice = ref<Asset | null>(null)
const showQuickAdd = ref(false)
const searchKeyword = ref('')

// 分页相关
const pageSize = ref(20) // 每次显示20个设备
const currentPage = ref(1)

// 过滤后的设备列表
const filteredDevices = computed(() => {
  if (!searchKeyword.value.trim()) {
    return devices.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return devices.value.filter(device => 
    device.name.toLowerCase().includes(keyword) ||
    device.category?.toLowerCase().includes(keyword) ||
    device.ip_address?.toLowerCase().includes(keyword)
  )
})

// 显示的设备列表（分页）
const displayedDevices = computed(() => {
  const start = 0
  const end = currentPage.value * pageSize.value
  return filteredDevices.value.slice(start, end)
})

// 加载更多设备
const loadMoreDevices = () => {
  currentPage.value++
}

// 计算属性 - 统计信息
const totalPorts = computed(() => {
  return devices.value.reduce((sum, device) => sum + (device.port_count || 0), 0)
})

const totalConnectedPorts = computed(() => {
  return devices.value.reduce((sum, device) => sum + (device.connected_ports || 0), 0)
})

const totalAvailablePorts = computed(() => {
  return totalPorts.value - totalConnectedPorts.value
})

// 加载设备数据
const loadDevices = async () => {
  loading.value = true
  try {
    // 获取所有拓扑显示设备（基于can_topology字段）
    const response = await assetApi.getAssets({ 
      page: 1, 
      pageSize: 1000,
      topology_devices: 'true'  // 改为基于拓扑显示字段过滤
    } as any)
    
    if (response.success) {
      devices.value = response.data.list || []
      
      // 如果有设备，批量获取端口统计信息
      if (devices.value.length > 0) {
        try {
          const assetIds = devices.value.map(device => device.id)
          const statsResponse = await portApi.getPortsStatisticsBatch(assetIds)
          
          if (statsResponse.success) {
            const statsData = statsResponse.data
            // 为每个设备设置端口统计信息
            devices.value.forEach(device => {
              const stats = statsData[device.id]
              if (stats) {
                device.port_count = stats.port_count
                device.connected_ports = stats.connected_ports
              } else {
                device.port_count = 0
                device.connected_ports = 0
              }
            })
          }
        } catch (error) {
          console.warn('批量获取端口统计失败:', error)
          // 如果批量获取失败，设置默认值并刷新页面
          devices.value.forEach(device => {
            device.port_count = 0
            device.connected_ports = 0
          })
          // 立即重试加载数据
          setTimeout(() => {
            if (devices.value.length > 0) {
              loadDevices()
            }
          }, 2000)
        }
      }
    }
  } catch (error) {
    console.error('加载设备失败:', error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  currentPage.value = 1 // 重置分页
  loadDevices()
}

// 导出全部端口信息
const exportAll = () => {
  portApi.exportPorts()
}

// 查看设备端口
const viewDevicePorts = (device: Asset) => {
  router.push(`/app/network/ports/${device.id}`)
}

// 快速添加端口
const quickAddPort = (device: Asset) => {
  selectedDevice.value = device
  showQuickAdd.value = true
}

// 关闭快速添加对话框
const closeQuickAdd = () => {
  showQuickAdd.value = false
  selectedDevice.value = null
}

// 批量添加端口
const batchAddPorts = async (type: string) => {
  if (!selectedDevice.value) return
  
  try {
    let ports: any[] = []
    
    switch (type) {
      case 'switch':
        // 交换机：24个千兆以太网端口
        for (let i = 1; i <= 24; i++) {
          ports.push({
            port_name: `GE0/0/${i}`,
            port_type: 'ethernet',
            port_speed: '1G',
            port_index: i
          })
        }
        break
        
      case 'router':
        // 路由器：基础接口
        ports = [
          { port_name: 'GE0/0/0', port_type: 'ethernet', port_speed: '1G', is_uplink: true },
          { port_name: 'GE0/0/1', port_type: 'ethernet', port_speed: '1G' },
          { port_name: 'Console', port_type: 'console' },
          { port_name: 'Mgmt', port_type: 'management' }
        ]
        break
        
      case 'server':
        // 服务器：网络和管理端口
        ports = [
          { port_name: 'eth0', port_type: 'ethernet', port_speed: '1G' },
          { port_name: 'eth1', port_type: 'ethernet', port_speed: '1G' },
          { port_name: 'IPMI', port_type: 'management' }
        ]
        break
        
      case 'custom':
        // 自定义：跳转到详细管理页面
        closeQuickAdd()
        viewDevicePorts(selectedDevice.value)
        return
    }
    
    if (ports.length > 0) {
      const response = await portApi.createPortsBatch(selectedDevice.value.id, { ports })
      if (response.success) {
        alert(`成功创建 ${response.data.created.length} 个端口`)
        closeQuickAdd()
        // 立即刷新数据，确保主页显示最新的端口统计
        await refreshData()
      }
    }
  } catch (error) {
    console.error('批量创建端口失败:', error)
    alert('创建失败，请稍后重试')
  }
}

// 工具函数
const getDeviceIcon = (category: string) => {
  const icons: Record<string, string> = {
    '交换机': '🔀',
    '路由器': '📡',
    '防火墙': '🛡️',
    '服务器': '🖥️',
    '工作站': '💻',
    '网络设备': '📱'
  }
  return icons[category] || '📱'
}

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    '在用': 'success',
    '正常': 'success',
    '故障': 'error',
    '维护': 'warning',
    '离线': 'info'
  }
  return statusMap[status] || 'info'
}

// 扩展Asset类型以包含端口统计
declare module '@/api/asset' {
  interface Asset {
    port_count?: number
    connected_ports?: number
  }
}

onMounted(() => {
  loadDevices()
})

// 搜索关键词变化时重置分页
watch(searchKeyword, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.ports-management {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px 30px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  width: 200px;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #409eff;
}

.statistics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.stat-number.connected {
  color: #67c23a;
}

.stat-number.available {
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.device-grid {
  min-height: 400px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.device-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.load-more-container {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.load-more-btn {
  padding: 12px 24px;
  border: 2px dashed #dcdfe6;
  background: #f8f9fa;
  color: #606266;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.load-more-btn:hover {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}

.device-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.device-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.device-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.device-icon {
  font-size: 32px;
  margin-right: 12px;
}

.device-info {
  flex: 1;
}

.device-info h3 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 18px;
}

.device-category {
  color: #909399;
  font-size: 14px;
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.device-status {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-success { background: #f0f9ff; color: #67c23a; }
.status-error { background: #fef0f0; color: #f56c6c; }
.status-warning { background: #fdf6ec; color: #e6a23c; }
.status-info { background: #f4f4f5; color: #909399; }

.device-details {
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item label {
  color: #606266;
  font-weight: 500;
}

.port-summary {
  display: flex;
  justify-content: space-around;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.port-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.stat-number.connected {
  color: #67c23a;
}

.stat-number.available {
  color: #409eff;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.device-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary { background: #409eff; color: white; }
.btn-secondary { background: #909399; color: white; }
.btn-success { background: #67c23a; color: white; }
.btn-info { background: #17a2b8; color: white; }

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  flex: 1;
}

/* 快速添加对话框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.modal-header h3 {
  margin: 0;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #909399;
}

.modal-body {
  padding: 24px;
}

.quick-add-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.option-card {
  background: #f8f9fa;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.option-card:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.option-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.option-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.option-desc {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .device-cards {
    grid-template-columns: 1fr;
  }
  
  .quick-add-options {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 90%;
    margin: 20px;
  }
}
</style>