<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ isEditMode ? '编辑连接' : '端口连接管理' }}</h3>
        <button @click="$emit('close')" class="close-btn">✕</button>
      </div>
      
      <div class="modal-body">
        <!-- 源端口信息 -->
        <div class="connection-section">
          <h4>源端口</h4>
          <div class="port-selector">
            <div class="device-select">
              <label>设备：</label>
              <select v-model="sourceDevice" @change="loadSourcePorts">
                <option value="">请选择设备</option>
                <option v-for="device in devices" :key="device.id" :value="device.id">
                  {{ device.name }} ({{ device.category }})
                </option>
              </select>
            </div>
            
            <div v-if="sourcePorts.length > 0" class="port-select">
              <label>端口：</label>
              <select v-model="sourcePort">
                <option value="">请选择端口</option>
                <option 
                  v-for="port in availableSourcePorts" 
                  :key="port.id" 
                  :value="port.id"
                >
                  {{ port.port_name }} ({{ getPortTypeLabel(port.port_type) }})
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- 目标端口信息 -->
        <div class="connection-section">
          <h4>目标端口</h4>
          <div class="port-selector">
            <div class="device-select">
              <label>设备：</label>
              <select v-model="targetDevice" @change="loadTargetPorts">
                <option value="">请选择设备</option>
                <option 
                  v-for="device in devices" 
                  :key="device.id" 
                  :value="device.id"
                  :disabled="device.id === sourceDevice"
                >
                  {{ device.name }} ({{ device.category }})
                </option>
              </select>
            </div>
            
            <div v-if="targetPorts.length > 0" class="port-select">
              <label>端口：</label>
              <select v-model="targetPort">
                <option value="">请选择端口</option>
                <option 
                  v-for="port in availableTargetPorts" 
                  :key="port.id" 
                  :value="port.id"
                >
                  {{ port.port_name }} ({{ getPortTypeLabel(port.port_type) }})
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- 连接配置 -->
        <div class="connection-section">
          <h4>连接配置</h4>
          <div class="connection-config">
            <div class="form-group">
              <label>线缆类型：</label>
              <select v-model="connectionForm.cable_type">
                <option value="copper">铜缆</option>
                <option value="fiber">光纤</option>
                <option value="wireless">无线</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>线缆长度(米)：</label>
              <input 
                v-model.number="connectionForm.cable_length" 
                type="number" 
                step="0.1" 
                min="0"
                placeholder="可选"
              >
            </div>
            
            <div class="form-group full-width">
              <label>备注：</label>
              <textarea 
                v-model="connectionForm.notes" 
                rows="3" 
                placeholder="连接备注信息"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 连接预览 -->
        <div v-if="canConnect" class="connection-preview">
          <h4>连接预览</h4>
          <div class="preview-content">
            <div class="device-info">
              <span class="device-name">{{ getDeviceName(sourceDevice) }}</span>
              <span class="port-name">{{ getPortName(sourcePort) }}</span>
            </div>
            <div class="connection-arrow">
              <span class="arrow">⟷</span>
              <span class="cable-type">{{ getCableTypeLabel(connectionForm.cable_type) }}</span>
            </div>
            <div class="device-info">
              <span class="device-name">{{ getDeviceName(targetDevice) }}</span>
              <span class="port-name">{{ getPortName(targetPort) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn btn-secondary">取消</button>
        <button 
          @click="createConnection" 
          :disabled="!canConnect || connecting" 
          class="btn btn-primary"
        >
          {{ connecting ? '连接中...' : '创建连接' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { portApi, type AssetPort } from '@/api/port'
import { assetApi, type Asset } from '@/api/asset'
import type { TopologyEdge } from '@/api/network'

interface Props {
  show: boolean
  editConnection?: TopologyEdge | null
  preSelectedSource?: {
    asset_id?: number
    asset_name?: string
    port_id?: number
    port_name?: string
  } | null
}

interface Emits {
  (e: 'close'): void
  (e: 'connected', connection: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 数据
const devices = ref<Asset[]>([])
const sourcePorts = ref<AssetPort[]>([])
const targetPorts = ref<AssetPort[]>([])
const connecting = ref(false)

// 选择的设备和端口
const sourceDevice = ref<number | ''>('')
const targetDevice = ref<number | ''>('')
const sourcePort = ref<number | ''>('')
const targetPort = ref<number | ''>('')

// 连接表单
const connectionForm = ref({
  cable_type: 'copper',
  cable_length: undefined as number | undefined,
  notes: ''
})

// 计算属性
const isEditMode = computed(() => !!props.editConnection)

const availableSourcePorts = computed(() => {
  return sourcePorts.value.filter(port => !port.is_connected)
})

const availableTargetPorts = computed(() => {
  return targetPorts.value.filter(port => !port.is_connected)
})

const canConnect = computed(() => {
  return sourceDevice.value && targetDevice.value && 
         sourcePort.value && targetPort.value &&
         sourceDevice.value !== targetDevice.value
})

// 加载设备列表
const loadDevices = async () => {
  try {
    // 获取所有拓扑显示设备（基于can_topology字段）
    const response = await assetApi.getAssets({ 
      page: 1, 
      pageSize: 1000,
      topology_devices: 'true'  // 改为基于拓扑显示字段过滤
    } as any)
    if (response.success) {
      devices.value = response.data.list || []
    }
  } catch (error) {
    console.error('加载设备失败:', error)
  }
}

// 加载源设备端口
const loadSourcePorts = async () => {
  if (!sourceDevice.value) {
    sourcePorts.value = []
    sourcePort.value = ''
    return
  }
  
  try {
    const response = await portApi.getAssetPorts(sourceDevice.value as number)
    if (response.success) {
      sourcePorts.value = response.data.ports
    }
  } catch (error) {
    console.error('加载源端口失败:', error)
  }
}

// 加载目标设备端口
const loadTargetPorts = async () => {
  if (!targetDevice.value) {
    targetPorts.value = []
    targetPort.value = ''
    return
  }
  
  try {
    const response = await portApi.getAssetPorts(targetDevice.value as number)
    if (response.success) {
      targetPorts.value = response.data.ports
    }
  } catch (error) {
    console.error('加载目标端口失败:', error)
  }
}

// 创建连接
const createConnection = async () => {
  if (!canConnect.value) return
  
  connecting.value = true
  try {
    const response = await portApi.connectPorts({
      source_port_id: sourcePort.value as number,
      target_port_id: targetPort.value as number,
      cable_type: connectionForm.value.cable_type as any,
      cable_length: connectionForm.value.cable_length,
      notes: connectionForm.value.notes
    })
    
    if (response.success) {
      emit('connected', response.data)
      emit('close')
      resetForm()
    }
  } catch (error) {
    console.error('创建连接失败:', error)
    alert('连接失败，请稍后重试')
  } finally {
    connecting.value = false
  }
}

// 重置表单
const resetForm = () => {
  sourceDevice.value = ''
  targetDevice.value = ''
  sourcePort.value = ''
  targetPort.value = ''
  sourcePorts.value = []
  targetPorts.value = []
  connectionForm.value = {
    cable_type: 'copper',
    cable_length: undefined,
    notes: ''
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
  return labels[type || ''] || type || ''
}

const getCableTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    copper: '铜缆',
    fiber: '光纤',
    wireless: '无线'
  }
  return labels[type] || type
}

const getDeviceName = (deviceId: number | '') => {
  if (!deviceId) return ''
  const device = devices.value.find(d => d.id === deviceId)
  return device?.name || ''
}

const getPortName = (portId: number | '') => {
  if (!portId) return ''
  const port = [...sourcePorts.value, ...targetPorts.value].find(p => p.id === portId)
  return port?.port_name || ''
}

// 监听显示状态
watch(() => props.show, (show) => {
  if (show) {
    loadDevices().then(() => {
      // 设备列表加载完成后，设置预选的源端口
      if (props.preSelectedSource) {
        sourceDevice.value = props.preSelectedSource.asset_id || ''
        if (sourceDevice.value) {
          loadSourcePorts().then(() => {
            sourcePort.value = props.preSelectedSource?.port_id || ''
          })
        }
      }
    })
  } else {
    resetForm()
  }
})

onMounted(() => {
  if (props.show) {
    loadDevices()
  }
})
</script>

<style scoped>
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
  width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
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
  padding: 4px;
}

.modal-body {
  padding: 24px;
}

.connection-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.connection-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.port-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.device-select,
.port-select {
  display: flex;
  flex-direction: column;
}

.device-select label,
.port-select label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 6px;
  font-weight: 500;
}

.device-select select,
.port-select select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.connection-config {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
}

.connection-preview {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 8px;
  padding: 16px;
}

.connection-preview h4 {
  margin: 0 0 12px 0;
  color: #1890ff;
  font-size: 14px;
}

.preview-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.device-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.device-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.port-name {
  color: #1890ff;
  font-size: 12px;
}

.connection-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 16px;
}

.arrow {
  font-size: 18px;
  color: #52c41a;
  margin-bottom: 4px;
}

.cable-type {
  font-size: 12px;
  color: #606266;
  background: white;
  padding: 2px 6px;
  border-radius: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #337ecc;
}

.btn-secondary {
  background: #dcdfe6;
  color: #606266;
}

.btn-secondary:hover {
  background: #c0c4cc;
}
</style>