<template>
  <div class="port-manager">
    <!-- 功能按钮区域 -->
    <div class="port-header">
      <div class="header-actions">
        <button @click="showBatchCreate = true" class="btn btn-secondary">
          ➕ 批量添加
        </button>
        <button @click="showCreateDialog = true" class="btn btn-primary">
          ➕ 新增端口
        </button>
        <button @click="exportPorts" class="btn btn-info">
          📤 导出
        </button>
        <button @click="fileInput?.click()" class="btn btn-success">
          📥 导入
        </button>
        <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv" @change="importPorts" style="display: none">
      </div>
    </div>

    <!-- 端口列表 -->
    <div class="port-grid">
      <div
        v-for="port in ports"
        :key="port.id"
        :class="`port-card ${port.port_status} ${port.is_connected ? 'connected' : ''}`"
        @click="selectPort(port)"
        @contextmenu.prevent="showPortContextMenu(port, $event)"
      >
        <div class="port-header-small">
          <span class="port-name">{{ port.port_name }}</span>
          <span :class="`port-type-badge ${port.port_type}`">{{ getPortTypeLabel(port.port_type) }}</span>
        </div>
        
        <div class="port-details">
          <div class="port-speed">{{ port.port_speed || '-' }}</div>
          <div :class="`port-status status-${port.port_status}`">
            {{ getStatusLabel(port.port_status) }}
          </div>
        </div>
        
        <div v-if="port.is_connected && port.connected_port" class="port-connection">
          <div class="connection-info">
            <span class="connection-icon">🔗</span>
            <span class="connection-target">{{ port.connected_port.asset?.name }}</span>
          </div>
          <div class="connection-port">{{ port.connected_port.port_name }}</div>
        </div>
        
        <div v-if="port.is_uplink" class="uplink-badge">上联</div>
      </div>
    </div>

    <!-- 端口详情面板 -->
    <div v-if="selectedPort" class="port-detail-panel">
      <div class="panel-header">
        <h4>{{ selectedPort.port_name }}</h4>
        <button @click="selectedPort = null" class="close-btn">✕</button>
      </div>
      
      <div class="panel-content">
        <div class="detail-section">
          <h5>基本信息</h5>
          <div class="detail-item">
            <label>端口类型：</label>
            <span>{{ getPortTypeLabel(selectedPort.port_type) }}</span>
          </div>
          <div class="detail-item">
            <label>端口速率：</label>
            <span>{{ selectedPort.port_speed || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>状态：</label>
            <span :class="`status-${selectedPort.port_status}`">{{ getStatusLabel(selectedPort.port_status) }}</span>
          </div>
          <div class="detail-item">
            <label>VLAN：</label>
            <span>{{ selectedPort.vlan_id || '-' }}</span>
          </div>
        </div>

        <div v-if="selectedPort.is_connected" class="detail-section">
          <h5>连接信息</h5>
          <div class="connection-detail">
            <div class="connection-target-device">
              <strong>{{ selectedPort.connected_port?.asset?.name }}</strong>
            </div>
            <div class="connection-target-port">{{ selectedPort.connected_port?.port_name }}</div>
            <div class="cable-info">
              <span>{{ getCableTypeLabel(selectedPort.cable_type) }}</span>
              <span v-if="selectedPort.cable_length"> - {{ selectedPort.cable_length }}m</span>
            </div>
          </div>
        </div>

        <div class="panel-actions">
          <button @click="editPort(selectedPort)" class="btn btn-primary btn-sm">编辑</button>
          <button v-if="!selectedPort.is_connected" @click="connectPort(selectedPort)" class="btn btn-success btn-sm">连接</button>
          <button v-else @click="disconnectPort(selectedPort)" class="btn btn-warning btn-sm">断开</button>
          <button @click="deletePort(selectedPort)" class="btn btn-danger btn-sm">删除</button>
        </div>
      </div>
    </div>

    <!-- 创建/编辑端口对话框 -->
    <div v-if="showCreateDialog" class="modal-overlay" @click="closeCreateDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑端口' : '新增端口' }}</h3>
          <button @click="closeCreateDialog" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="savePort">
            <div class="form-row">
              <div class="form-group">
                <label>端口名称 *</label>
                <input v-model="portForm.port_name" required placeholder="如：GE0/0/1">
              </div>
              <div class="form-group">
                <label>端口类型</label>
                <select v-model="portForm.port_type">
                  <option value="ethernet">以太网口</option>
                  <option value="fiber">光纤口</option>
                  <option value="console">控制台口</option>
                  <option value="management">管理口</option>
                  <option value="power">电源口</option>
                  <option value="usb">USB口</option>
                </select>
              </div>
            </div>
            
            <div class="form-row">
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
                <label>端口状态</label>
                <select v-model="portForm.port_status">
                  <option value="unused">未使用</option>
                  <option value="used">使用中</option>
                  <option value="error">故障</option>
                  <option value="disabled">禁用</option>
                </select>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>端口序号</label>
                <input v-model.number="portForm.port_index" type="number" min="1">
              </div>
              <div class="form-group">
                <label>VLAN ID</label>
                <input v-model.number="portForm.vlan_id" type="number" min="1" max="4094">
              </div>
            </div>
            
            <div class="form-group">
              <label>
                <input v-model="portForm.is_uplink" type="checkbox">
                上联端口
              </label>
            </div>
            
            <div class="form-group">
              <label>描述</label>
              <textarea v-model="portForm.description" rows="3" placeholder="端口描述信息"></textarea>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button @click="closeCreateDialog" class="btn btn-secondary">取消</button>
          <button @click="savePort" :disabled="saving" class="btn btn-primary">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 批量添加端口对话框 -->
    <div v-if="showBatchCreate" class="modal-overlay" @click="closeBatchDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>批量添加端口</h3>
          <button @click="closeBatchDialog" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="batch-options">
            <div class="option-section">
              <h4>快速预设</h4>
              <div class="preset-buttons">
                <button @click="setBatchPreset('switch24')" class="preset-btn">
                  24口交换机 (GE1/0/1-24)
                </button>
                <button @click="setBatchPreset('switch48')" class="preset-btn">
                  48口交换机 (GE1/0/1-48)
                </button>
                <button @click="setBatchPreset('router')" class="preset-btn">
                  路由器 (GE0/0/0-3 + Console)
                </button>
              </div>
            </div>
            
            <div class="option-section">
              <h4>自定义批量添加</h4>
              <div class="custom-batch">
                <div class="form-group">
                  <label>端口名称前缀</label>
                  <input v-model="batchForm.prefix" placeholder="如：GE1/0/">
                </div>
                <div class="form-group">
                  <label>起始编号</label>
                  <input v-model.number="batchForm.startIndex" type="number" min="1" value="1">
                </div>
                <div class="form-group">
                  <label>结束编号</label>
                  <input v-model.number="batchForm.endIndex" type="number" min="1" value="24">
                </div>
                <div class="form-group">
                  <label>端口类型</label>
                  <select v-model="batchForm.portType">
                    <option value="ethernet">以太网口</option>
                    <option value="fiber">光纤口</option>
                    <option value="console">控制台口</option>
                    <option value="management">管理口</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>端口速率</label>
                  <select v-model="batchForm.portSpeed">
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
                  <label>端口状态</label>
                  <select v-model="batchForm.portStatus">
                    <option value="unused">未使用</option>
                    <option value="used">使用中</option>
                    <option value="disabled">禁用</option>
                  </select>
                </div>
                <button @click="createBatchPorts" :disabled="batchSaving" class="btn btn-primary">
                  {{ batchSaving ? '创建中...' : '批量创建' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 端口连接对话框 -->
    <ConnectionDialog 
      :show="showConnectionDialog" 
      @close="closeConnectionDialog"
      @connected="handlePortConnected"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { portApi, type AssetPort } from '@/api/port'
import ConnectionDialog from './ConnectionDialog.vue'

interface Props {
  assetId: number
}

const props = defineProps<Props>()

// 文件输入引用
const fileInput = ref<HTMLInputElement>()

// 数据
const ports = ref<AssetPort[]>([])
const asset = ref<any>(null)
const selectedPort = ref<AssetPort | null>(null)
const loading = ref(false)
const saving = ref(false)
const batchSaving = ref(false)

// 对话框状态
const showCreateDialog = ref(false)
const showBatchCreate = ref(false)
const showConnectionDialog = ref(false)
const isEditing = ref(false)

// 表单数据
const portForm = reactive<Partial<AssetPort>>({
  port_name: '',
  port_type: 'ethernet' as const,
  port_speed: undefined,
  port_status: 'unused' as const,
  port_index: undefined,
  vlan_id: undefined,
  is_uplink: false,
  description: ''
})

// 批量添加表单数据
const batchForm = reactive({
  prefix: 'GE1/0/',
  startIndex: 1,
  endIndex: 24,
  portType: 'ethernet',
  portSpeed: '1G',
  portStatus: 'unused'
})

// 加载端口数据
const loadPorts = async () => {
  loading.value = true
  try {
    const response = await portApi.getAssetPorts(props.assetId)
    if (response.success) {
      ports.value = response.data.ports
      asset.value = response.data.asset
    }
  } catch (error) {
    console.error('加载端口失败:', error)
  } finally {
    loading.value = false
  }
}

// 选择端口
const selectPort = (port: AssetPort) => {
  selectedPort.value = port
}

// 关闭创建对话框
const closeCreateDialog = () => {
  showCreateDialog.value = false
  isEditing.value = false
  resetForm()
}

// 重置表单
const resetForm = () => {
  Object.assign(portForm, {
    port_name: '',
    port_type: 'ethernet',
    port_speed: '',
    port_status: 'unused',
    port_index: null,
    vlan_id: null,
    is_uplink: false,
    description: ''
  })
}

// 保存端口
const savePort = async () => {
  if (!portForm.port_name?.trim()) {
    alert('请输入端口名称')
    return
  }
  
  saving.value = true
  try {
    const data = { ...portForm }
    if (isEditing.value && selectedPort.value) {
      const response = await portApi.updatePort(selectedPort.value.id!, data)
      if (response.success) {
        alert('端口更新成功')
      } else {
        alert('更新失败：' + (response.message || '未知错误'))
        return
      }
    } else {
      const response = await portApi.createPort(props.assetId, data)
      if (response.success) {
        alert('端口创建成功')
      } else {
        alert('创建失败：' + (response.message || '未知错误'))
        return
      }
    }
    await loadPorts()
    closeCreateDialog()
  } catch (error) {
    console.error('保存端口失败:', error)
    alert('保存失败：' + (error as Error).message)
  } finally {
    saving.value = false
  }
}

// 编辑端口
const editPort = (port: AssetPort) => {
  Object.assign(portForm, port)
  isEditing.value = true
  showCreateDialog.value = true
}

// 连接端口
const connectPort = (port: AssetPort) => {
  selectedPort.value = port
  showConnectionDialog.value = true
}

// 关闭连接对话框
const closeConnectionDialog = () => {
  showConnectionDialog.value = false
  selectedPort.value = null
}

// 处理端口连接成功
const handlePortConnected = () => {
  loadPorts() // 重新加载端口数据
}

// 断开端口连接
const disconnectPort = async (port: AssetPort) => {
  if (!confirm('确认断开连接吗？')) return
  
  try {
    await portApi.disconnectPort(port.id!)
    await loadPorts()
    selectedPort.value = null
  } catch (error) {
    console.error('断开连接失败:', error)
  }
}

// 删除端口
const deletePort = async (port: AssetPort) => {
  if (!confirm('确认删除此端口吗？')) return
  
  try {
    await portApi.deletePort(port.id!)
    await loadPorts()
    selectedPort.value = null
  } catch (error) {
    console.error('删除端口失败:', error)
  }
}

// 工具函数
const getPortTypeLabel = (type?: string) => {
  const labels: Record<string, string> = {
    ethernet: '以太网',
    fiber: '光纤',
    console: '控制台',
    management: '管理',
    power: '电源',
    usb: 'USB'
  }
  return labels[type || ''] || type
}

const getStatusLabel = (status?: string) => {
  const labels: Record<string, string> = {
    used: '使用中',
    unused: '未使用',
    error: '故障',
    disabled: '禁用'
  }
  return labels[status || ''] || status
}

const getCableTypeLabel = (type?: string) => {
  const labels: Record<string, string> = {
    copper: '铜缆',
    fiber: '光纤',
    wireless: '无线'
  }
  return labels[type || ''] || type
}

// 关闭批量添加对话框
const closeBatchDialog = () => {
  showBatchCreate.value = false
}

// 设置批量添加预设
const setBatchPreset = (preset: string) => {
  switch (preset) {
    case 'switch24':
      Object.assign(batchForm, {
        prefix: 'GE1/0/',
        startIndex: 1,
        endIndex: 24,
        portType: 'ethernet',
        portSpeed: '1G',
        portStatus: 'unused'
      })
      break
    case 'switch48':
      Object.assign(batchForm, {
        prefix: 'GE1/0/',
        startIndex: 1,
        endIndex: 48,
        portType: 'ethernet',
        portSpeed: '1G',
        portStatus: 'unused'
      })
      break
    case 'router':
      Object.assign(batchForm, {
        prefix: 'GE0/0/',
        startIndex: 0,
        endIndex: 3,
        portType: 'ethernet',
        portSpeed: '1G',
        portStatus: 'unused'
      })
      break
  }
}

// 批量创建端口
const createBatchPorts = async () => {
  if (!batchForm.prefix?.trim()) {
    alert('请输入端口名称前缀')
    return
  }
  
  if (batchForm.endIndex <= batchForm.startIndex) {
    alert('结束编号必须大于起始编号')
    return
  }
  
  if (batchForm.endIndex - batchForm.startIndex > 100) {
    alert('一次最多创建100个端口')
    return
  }
  
  batchSaving.value = true
  try {
    const ports: Partial<AssetPort>[] = []
    for (let i = batchForm.startIndex; i <= batchForm.endIndex; i++) {
      ports.push({
        port_name: `${batchForm.prefix}${i}`,
        port_type: batchForm.portType as AssetPort['port_type'],
        port_speed: batchForm.portSpeed as AssetPort['port_speed'] || undefined,
        port_status: batchForm.portStatus as AssetPort['port_status'],
        port_index: i
      })
    }
    
    const response = await portApi.createPortsBatch(props.assetId, { ports })
    if (response.success) {
      const { created, errors } = response.data
      let message = `成功创建 ${created.length} 个端口`
      if (errors.length > 0) {
        message += `\n${errors.length} 个端口创建失败：\n${errors.join('\n')}`
      }
      alert(message)
      await loadPorts()
      closeBatchDialog()
    } else {
      alert('批量创建失败：' + (response.message || '未知错误'))
    }
  } catch (error) {
    console.error('批量创建端口失败:', error)
    alert('批量创建失败：' + (error as Error).message)
  } finally {
    batchSaving.value = false
  }
}

// 显示端口右键菜单
const showPortContextMenu = (port: AssetPort, event: MouseEvent) => {
  // TODO: 实现右键菜单功能
  console.log('右键点击端口:', port)
}
// 导出端口
const exportPorts = () => {
  portApi.exportPorts(props.assetId)
}

// 导入端口
const importPorts = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  
  try {
    const response = await portApi.importPorts(file, props.assetId)
    if (response.success) {
      await loadPorts()
      alert(`导入成功：${response.data.created.length} 个端口`)
    }
  } catch (error) {
    console.error('导入失败:', error)
  }
}

onMounted(() => {
  loadPorts()
})
</script>

<style scoped>
.port-manager {
  padding: 0;
}

.port-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.port-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.port-card {
  background: white;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.port-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.2);
}

.port-card.connected {
  border-color: #67c23a;
  background: #f0f9ff;
}

.port-card.used {
  border-left: 4px solid #409eff;
}

.port-card.error {
  border-left: 4px solid #f56c6c;
}

.port-header-small {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.port-name {
  font-weight: 600;
  color: #303133;
}

.port-type-badge {
  background: #e6f7ff;
  color: #1890ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.port-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.port-connection {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 4px;
  padding: 8px;
  margin-top: 8px;
}

.connection-info {
  display: flex;
  align-items: center;
  font-weight: 500;
  color: #52c41a;
}

.connection-icon {
  margin-right: 6px;
}

.uplink-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #fa8c16;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.port-detail-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 8px rgba(0,0,0,0.1);
  z-index: 1000;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.panel-content {
  padding: 20px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h5 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 6px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item label {
  color: #606266;
  width: 100px;
}

.connection-detail {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
}

.connection-target-device {
  color: #303133;
  margin-bottom: 4px;
}

.connection-target-port {
  color: #409eff;
  font-weight: 500;
  margin-bottom: 6px;
}

.cable-info {
  color: #909399;
  font-size: 12px;
}

.panel-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 6px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.status-used { color: #409eff; }
.status-unused { color: #909399; }
.status-error { color: #f56c6c; }
.status-disabled { color: #c0c4cc; }

/* 批量添加对话框样式 */
.batch-options {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.option-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.preset-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.preset-btn {
  background: #f8f9fa;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.preset-btn:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.custom-batch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.custom-batch .btn {
  grid-column: 1 / -1;
  justify-self: start;
}
</style>