<template>
  <div class="port-manager">
    <div class="port-header">
      <h3>端口管理 - {{ asset?.name }}</h3>
      <div class="port-actions">
        <button @click="showCreateDialog = true" class="btn btn-primary">
          ➕ 添加端口
        </button>
        <button @click="autoCreatePorts" class="btn btn-success" v-if="canAutoCreate">
          🔧 自动创建
        </button>
        <button @click="refreshPorts" class="btn btn-secondary">
          🔄 刷新
        </button>
      </div>
    </div>

    <!-- 端口统计 -->
    <div class="port-stats">
      <div class="stat-item">
        <span class="stat-label">总端口数</span>
        <span class="stat-value">{{ portStats.total_count }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">已连接</span>
        <span class="stat-value connected">{{ portStats.connected_count }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">未使用</span>
        <span class="stat-value unused">{{ portStats.unused_count }}</span>
      </div>
    </div>

    <!-- 端口列表 -->
    <div class="port-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="ports.length === 0" class="empty-state">
        <p>暂无端口数据</p>
        <button @click="showCreateDialog = true" class="btn btn-primary">添加第一个端口</button>
      </div>
      <div v-else class="port-grid">
        <div 
          v-for="port in ports" 
          :key="port.id" 
          class="port-card"
          :class="getPortStatusClass(port)"
          @click="selectPort(port)"
        >
          <div class="port-name">{{ port.port_name }}</div>
          <div class="port-type">{{ port.port_type || '未设置' }}</div>
          <div class="port-status">
            <span :class="`status-badge status-${port.port_status}`">
              {{ getPortStatusText(port.port_status) }}
            </span>
          </div>
          <div v-if="port.is_connected" class="port-connection">
            <span class="connection-info">
              → {{ port.connected_asset_name }}:{{ port.connected_port_name }}
            </span>
          </div>
          <div class="port-actions">
            <button @click.stop="editPort(port)" class="btn-sm btn-primary">编辑</button>
            <button 
              v-if="!port.is_connected" 
              @click.stop="connectPort(port)" 
              class="btn-sm btn-success"
            >
              连接
            </button>
            <button 
              v-else 
              @click.stop="disconnectPort(port)" 
              class="btn-sm btn-warning"
            >
              断开
            </button>
            <button @click.stop="deletePort(port)" class="btn-sm btn-danger">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建端口对话框 -->
    <div v-if="showCreateDialog" class="modal-overlay" @click="showCreateDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingPort ? '编辑端口' : '创建端口' }}</h3>
          <button @click="closeCreateDialog" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="savePort">
            <div class="form-group">
              <label>端口名称</label>
              <input v-model="portForm.port_name" required placeholder="如：Port1, GE0/0/1" />
            </div>
            <div class="form-group">
              <label>端口类型</label>
              <select v-model="portForm.port_type">
                <option value="">请选择</option>
                <option value="ethernet">以太网</option>
                <option value="fiber">光纤</option>
                <option value="console">控制台</option>
                <option value="management">管理</option>
                <option value="power">电源</option>
                <option value="usb">USB</option>
              </select>
            </div>
            <div class="form-group">
              <label>端口速率</label>
              <select v-model="portForm.port_speed">
                <option value="">请选择</option>
                <option value="10M">10M</option>
                <option value="100M">100M</option>
                <option value="1G">1G</option>
                <option value="10G">10G</option>
                <option value="25G">25G</option>
                <option value="40G">40G</option>
                <option value="100G">100G</option>
              </select>
            </div>
            <div class="form-group">
              <label>端口序号</label>
              <input v-model.number="portForm.port_index" type="number" min="1" />
            </div>
            <div class="form-group">
              <label>
                <input type="checkbox" v-model="portForm.is_uplink" />
                上联端口
              </label>
            </div>
            <div class="form-group">
              <label>描述</label>
              <textarea v-model="portForm.description" rows="3"></textarea>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button @click="closeCreateDialog" class="btn btn-secondary">取消</button>
          <button @click="savePort" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>

    <!-- 连接端口对话框 -->
    <div v-if="showConnectDialog" class="modal-overlay" @click="showConnectDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>连接端口 - {{ selectedPort?.port_name }}</h3>
          <button @click="showConnectDialog = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="connection-form">
            <div class="form-group">
              <label>目标资产</label>
              <select v-model="connectionForm.target_asset_id" @change="loadTargetPorts">
                <option value="">请选择资产</option>
                <option v-for="asset in availableAssets" :key="asset.id" :value="asset.id">
                  {{ asset.name }} ({{ asset.category }})
                </option>
              </select>
            </div>
            <div class="form-group" v-if="targetPorts.length > 0">
              <label>目标端口</label>
              <select v-model="connectionForm.target_port_id">
                <option value="">请选择端口</option>
                <option 
                  v-for="port in targetPorts" 
                  :key="port.id" 
                  :value="port.id"
                  :disabled="port.is_connected"
                >
                  {{ port.port_name }} {{ port.is_connected ? '(已连接)' : '' }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>线缆类型</label>
              <select v-model="connectionForm.cable_type">
                <option value="copper">铜缆</option>
                <option value="fiber">光纤</option>
                <option value="wireless">无线</option>
              </select>
            </div>
            <div class="form-group">
              <label>线缆长度(米)</label>
              <input v-model.number="connectionForm.cable_length" type="number" step="0.1" min="0" />
            </div>
            <div class="form-group">
              <label>备注</label>
              <textarea v-model="connectionForm.notes" rows="2"></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showConnectDialog = false" class="btn btn-secondary">取消</button>
          <button @click="confirmConnect" class="btn btn-primary">连接</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'

interface Port {
  id: number
  asset_id: number
  port_name: string
  port_type?: string
  port_speed?: string
  port_status: string
  port_index?: number
  is_uplink: boolean
  is_connected: boolean
  connected_asset_name?: string
  connected_port_name?: string
  description?: string
}

interface Asset {
  id: number
  name: string
  category: string
}

interface PortStats {
  total_count: number
  connected_count: number
  unused_count: number
}

const props = defineProps<{
  asset: Asset
}>()

const emit = defineEmits<{
  'port-updated': []
}>()

// 响应式数据
const loading = ref(false)
const ports = ref<Port[]>([])
const portStats = ref<PortStats>({ total_count: 0, connected_count: 0, unused_count: 0 })
const showCreateDialog = ref(false)
const showConnectDialog = ref(false)
const editingPort = ref<Port | null>(null)
const selectedPort = ref<Port | null>(null)
const availableAssets = ref<Asset[]>([])
const targetPorts = ref<Port[]>([])

// 表单数据
const portForm = reactive({
  port_name: '',
  port_type: '',
  port_speed: '',
  port_index: null as number | null,
  is_uplink: false,
  description: ''
})

const connectionForm = reactive({
  target_asset_id: '',
  target_port_id: '',
  cable_type: 'copper',
  cable_length: null as number | null,
  notes: ''
})

// 计算属性
const canAutoCreate = computed(() => {
  // 这里需要检查资产类别是否配置了默认端口数量
  return props.asset && ports.value.length === 0
})

// 方法
const refreshPorts = async () => {
  if (!props.asset) return
  
  loading.value = true
  try {
    // 这里调用端口API
    const response = await fetch(`/api/assets/${props.asset.id}/ports`)
    const data = await response.json()
    
    if (data.success) {
      ports.value = data.data.ports
      portStats.value = {
        total_count: data.data.total_count,
        connected_count: data.data.connected_count,
        unused_count: data.data.unused_count
      }
    }
  } catch (error) {
    console.error('加载端口失败:', error)
  } finally {
    loading.value = false
  }
}

const getPortStatusClass = (port: Port) => {
  if (port.is_connected) return 'port-connected'
  if (port.port_status === 'error') return 'port-error'
  if (port.port_status === 'disabled') return 'port-disabled'
  return 'port-unused'
}

const getPortStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'used': '使用中',
    'unused': '未使用',
    'error': '故障',
    'disabled': '禁用'
  }
  return statusMap[status] || status
}

const selectPort = (port: Port) => {
  selectedPort.value = port
}

const editPort = (port: Port) => {
  editingPort.value = port
  Object.assign(portForm, {
    port_name: port.port_name,
    port_type: port.port_type || '',
    port_speed: port.port_speed || '',
    port_index: port.port_index,
    is_uplink: port.is_uplink,
    description: port.description || ''
  })
  showCreateDialog.value = true
}

const closeCreateDialog = () => {
  showCreateDialog.value = false
  editingPort.value = null
  Object.assign(portForm, {
    port_name: '',
    port_type: '',
    port_speed: '',
    port_index: null,
    is_uplink: false,
    description: ''
  })
}

const savePort = async () => {
  try {
    const url = editingPort.value 
      ? `/api/ports/${editingPort.value.id}`
      : `/api/assets/${props.asset.id}/ports`
    
    const method = editingPort.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(portForm)
    })
    
    const data = await response.json()
    
    if (data.success) {
      closeCreateDialog()
      refreshPorts()
      emit('port-updated')
    } else {
      alert(data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存端口失败:', error)
    alert('保存失败')
  }
}

const connectPort = (port: Port) => {
  selectedPort.value = port
  showConnectDialog.value = true
  loadAvailableAssets()
}

const loadAvailableAssets = async () => {
  try {
    // 加载可连接的资产（网络设备）
    const response = await fetch('/api/assets?network_devices=true')
    const data = await response.json()
    
    if (data.success) {
      // 排除当前资产
      availableAssets.value = data.data.list.filter(
        (asset: Asset) => asset.id !== props.asset.id
      )
    }
  } catch (error) {
    console.error('加载可用资产失败:', error)
  }
}

const loadTargetPorts = async () => {
  if (!connectionForm.target_asset_id) {
    targetPorts.value = []
    return
  }
  
  try {
    const response = await fetch(`/api/assets/${connectionForm.target_asset_id}/ports`)
    const data = await response.json()
    
    if (data.success) {
      targetPorts.value = data.data.ports
    }
  } catch (error) {
    console.error('加载目标端口失败:', error)
  }
}

const confirmConnect = async () => {
  if (!selectedPort.value || !connectionForm.target_port_id) {
    alert('请选择目标端口')
    return
  }
  
  try {
    const response = await fetch('/api/ports/connect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_port_id: selectedPort.value.id,
        target_port_id: connectionForm.target_port_id,
        cable_type: connectionForm.cable_type,
        cable_length: connectionForm.cable_length,
        notes: connectionForm.notes
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      showConnectDialog.value = false
      refreshPorts()
      emit('port-updated')
    } else {
      alert(data.message || '连接失败')
    }
  } catch (error) {
    console.error('连接端口失败:', error)
    alert('连接失败')
  }
}

const disconnectPort = async (port: Port) => {
  if (!confirm(`确认断开端口 ${port.port_name} 的连接吗？`)) return
  
  try {
    const response = await fetch(`/api/ports/${port.id}/disconnect`, {
      method: 'POST'
    })
    
    const data = await response.json()
    
    if (data.success) {
      refreshPorts()
      emit('port-updated')
    } else {
      alert(data.message || '断开失败')
    }
  } catch (error) {
    console.error('断开端口失败:', error)
    alert('断开失败')
  }
}

const deletePort = async (port: Port) => {
  if (!confirm(`确认删除端口 ${port.port_name} 吗？`)) return
  
  try {
    const response = await fetch(`/api/ports/${port.id}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    
    if (data.success) {
      refreshPorts()
      emit('port-updated')
    } else {
      alert(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除端口失败:', error)
    alert('删除失败')
  }
}

const autoCreatePorts = async () => {
  if (!confirm('根据设备类别自动创建端口？')) return
  
  try {
    const response = await fetch(`/api/assets/${props.asset.id}/ports/auto-create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        port_name_pattern: 'Port{index}',
        port_type: 'ethernet'
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      refreshPorts()
      emit('port-updated')
      alert(`成功创建 ${data.data.created_count} 个端口`)
    } else {
      alert(data.message || '自动创建失败')
    }
  } catch (error) {
    console.error('自动创建端口失败:', error)
    alert('自动创建失败')
  }
}

// 生命周期
onMounted(() => {
  refreshPorts()
})
</script>

<style scoped>
.port-manager {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.port-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.port-actions {
  display: flex;
  gap: 12px;
}

.port-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.connected {
  color: #67c23a;
}

.stat-value.unused {
  color: #909399;
}

.port-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.port-card {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.port-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.port-card.port-connected {
  border-color: #67c23a;
  background: #f0f9ff;
}

.port-card.port-error {
  border-color: #f56c6c;
  background: #fef0f0;
}

.port-card.port-disabled {
  border-color: #c0c4cc;
  background: #f5f7fa;
  opacity: 0.7;
}

.port-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.port-type {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-used {
  background: #e1f5fe;
  color: #1976d2;
}

.status-unused {
  background: #f5f5f5;
  color: #616161;
}

.status-error {
  background: #ffebee;
  color: #d32f2f;
}

.status-disabled {
  background: #fafafa;
  color: #9e9e9e;
}

.port-connection {
  margin: 8px 0;
  font-size: 14px;
  color: #67c23a;
}

.connection-info {
  font-weight: 500;
}

.port-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary { background: #409eff; color: white; }
.btn-success { background: #67c23a; color: white; }
.btn-warning { background: #e6a23c; color: white; }
.btn-danger { background: #f56c6c; color: white; }
.btn-secondary { background: #909399; color: white; }

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e4e7ed;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #606266;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

.loading,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #606266;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #909399;
}

.close-btn:hover {
  color: #303133;
}
</style>