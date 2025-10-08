<template>
  <div class="device-form-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>{{ isEdit ? '编辑网络设备' : '新增网络设备' }}</h1>
      <div class="header-actions">
        <button @click="goBack" class="btn btn-secondary">← 返回</button>
        <button @click="resetForm" class="btn btn-secondary">🔄 重置</button>
        <button @click="saveDevice" :disabled="saving" class="btn btn-primary">
          {{ saving ? '保存中...' : '💾 保存' }}
        </button>
      </div>
    </div>

    <!-- 设备表单 -->
    <div class="form-container">
      <form @submit.prevent="saveDevice" class="device-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <h2>基本信息</h2>
          <div class="form-grid">
            <div class="form-group">
              <label for="name">设备名称 <span class="required">*</span></label>
              <input
                id="name"
                v-model="formData.name"
                type="text"
                placeholder="请输入设备名称"
                :class="{ error: errors.name }"
                @blur="validateField('name')"
              />
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label for="device_type">设备类型 <span class="required">*</span></label>
              <select
                id="device_type"
                v-model="formData.device_type"
                :class="{ error: errors.device_type }"
                @change="validateField('device_type')"
              >
                <option value="">请选择设备类型</option>
                <option value="交换机">交换机</option>
                <option value="路由器">路由器</option>
                <option value="防火墙">防火墙</option>
                <option value="安全设备">安全设备</option>
                <option value="服务器">服务器</option>
                <option value="工作站">工作站</option>
                <option value="其他">其他</option>
              </select>
              <span v-if="errors.device_type" class="error-text">{{ errors.device_type }}</span>
            </div>

            <div class="form-group">
              <label for="brand">设备品牌</label>
              <input
                id="brand"
                v-model="formData.brand"
                type="text"
                placeholder="请输入设备品牌"
              />
            </div>

            <div class="form-group">
              <label for="model">设备型号</label>
              <input
                id="model"
                v-model="formData.model"
                type="text"
                placeholder="请输入设备型号"
              />
            </div>

            <div class="form-group">
              <label for="serial_number">序列号</label>
              <input
                id="serial_number"
                v-model="formData.serial_number"
                type="text"
                placeholder="请输入设备序列号"
              />
            </div>

            <div class="form-group">
              <label for="status">设备状态 <span class="required">*</span></label>
              <select
                id="status"
                v-model="formData.status"
                :class="{ error: errors.status }"
                @change="validateField('status')"
              >
                <option value="">请选择设备状态</option>
                <option value="在线">在线</option>
                <option value="离线">离线</option>
                <option value="故障">故障</option>
                <option value="维护">维护</option>
              </select>
              <span v-if="errors.status" class="error-text">{{ errors.status }}</span>
            </div>
          </div>
        </div>

        <!-- 网络配置 -->
        <div class="form-section">
          <h2>网络配置</h2>
          <div class="form-grid">
            <div class="form-group">
              <label for="ip_address">IP地址</label>
              <input
                id="ip_address"
                v-model="formData.ip_address"
                type="text"
                placeholder="例如: 192.168.1.100"
                :class="{ error: errors.ip_address }"
                @blur="validateField('ip_address')"
              />
              <span v-if="errors.ip_address" class="error-text">{{ errors.ip_address }}</span>
            </div>

            <div class="form-group">
              <label for="mac_address">MAC地址</label>
              <input
                id="mac_address"
                v-model="formData.mac_address"
                type="text"
                placeholder="例如: 00:1B:44:11:3A:B7"
                :class="{ error: errors.mac_address }"
                @blur="validateField('mac_address')"
              />
              <span v-if="errors.mac_address" class="error-text">{{ errors.mac_address }}</span>
            </div>

            <div class="form-group">
              <label for="subnet_mask">子网掩码</label>
              <input
                id="subnet_mask"
                v-model="formData.subnet_mask"
                type="text"
                placeholder="例如: 255.255.255.0"
              />
            </div>

            <div class="form-group">
              <label for="gateway">网关</label>
              <input
                id="gateway"
                v-model="formData.gateway"
                type="text"
                placeholder="例如: 192.168.1.1"
              />
            </div>

            <div class="form-group">
              <label for="dns_servers">DNS服务器</label>
              <input
                id="dns_servers"
                v-model="formData.dns_servers"
                type="text"
                placeholder="多个DNS用逗号分隔"
              />
            </div>

            <div class="form-group">
              <label for="vlan_id">VLAN ID</label>
              <input
                id="vlan_id"
                v-model.number="formData.vlan_id"
                type="number"
                placeholder="请输入VLAN ID"
                min="1"
                max="4094"
              />
            </div>
          </div>
        </div>

        <!-- 位置信息 -->
        <div class="form-section">
          <h2>位置信息</h2>
          <div class="form-grid">
            <div class="form-group">
              <label for="building_id">建筑</label>
              <select id="building_id" v-model="formData.building_id" @change="loadFloors">
                <option value="">请选择建筑</option>
                <option v-for="building in buildings" :key="building.id" :value="building.id">
                  {{ building.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="floor_id">楼层</label>
              <select id="floor_id" v-model="formData.floor_id" @change="loadRooms" :disabled="!formData.building_id">
                <option value="">请选择楼层</option>
                <option v-for="floor in floors" :key="floor.id" :value="floor.id">
                  {{ floor.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="room_id">房间</label>
              <select id="room_id" v-model="formData.room_id" :disabled="!formData.floor_id">
                <option value="">请选择房间</option>
                <option v-for="room in rooms" :key="room.id" :value="room.id">
                  {{ room.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="location_detail">详细位置</label>
              <input
                id="location_detail"
                v-model="formData.location_detail"
                type="text"
                placeholder="例如: A机柜第3层"
              />
            </div>

            <div class="form-group">
              <label for="x_position">X坐标</label>
              <input
                id="x_position"
                v-model.number="formData.x_position"
                type="number"
                placeholder="网络拓扑X坐标"
              />
            </div>

            <div class="form-group">
              <label for="y_position">Y坐标</label>
              <input
                id="y_position"
                v-model.number="formData.y_position"
                type="number"
                placeholder="网络拓扑Y坐标"
              />
            </div>
          </div>
        </div>

        <!-- 设备属性 -->
        <div class="form-section">
          <h2>设备属性</h2>
          <div class="form-grid">
            <div class="form-group">
              <label for="firmware_version">固件版本</label>
              <input
                id="firmware_version"
                v-model="formData.firmware_version"
                type="text"
                placeholder="请输入固件版本"
              />
            </div>

            <div class="form-group">
              <label for="purchase_date">购买日期</label>
              <input
                id="purchase_date"
                v-model="formData.purchase_date"
                type="date"
              />
            </div>

            <div class="form-group">
              <label for="warranty_end_date">保修到期日期</label>
              <input
                id="warranty_end_date"
                v-model="formData.warranty_end_date"
                type="date"
              />
            </div>

            <div class="form-group">
              <label for="is_managed">是否托管</label>
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input
                    id="is_managed"
                    v-model="formData.is_managed"
                    type="checkbox"
                  />
                  <span class="checkmark"></span>
                  托管设备（可远程管理）
                </label>
              </div>
            </div>

            <div class="form-group full-width">
              <label for="description">设备描述</label>
              <textarea
                id="description"
                v-model="formData.description"
                rows="3"
                placeholder="请输入设备描述信息"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 端口配置 -->
        <div class="form-section">
          <h2>端口配置</h2>
          <div class="port-management">
            <div class="port-header">
              <button type="button" @click="addPort" class="btn btn-primary btn-sm">
                ➕ 添加端口
              </button>
              <span class="port-count">共 {{ formData.ports.length }} 个端口</span>
            </div>
            
            <div v-if="formData.ports.length > 0" class="port-list">
              <div
                v-for="(port, index) in formData.ports"
                :key="`port-${index}`"
                class="port-item"
              >
                <div class="port-fields">
                  <div class="form-group">
                    <label>端口名称</label>
                    <input
                      v-model="port.port_name"
                      type="text"
                      placeholder="例如: GE0/0/1"
                    />
                  </div>
                  <div class="form-group">
                    <label>端口类型</label>
                    <select v-model="port.port_type">
                      <option value="">选择类型</option>
                      <option value="FastEthernet">FastEthernet</option>
                      <option value="GigabitEthernet">GigabitEthernet</option>
                      <option value="10GigabitEthernet">10GigabitEthernet</option>
                      <option value="Serial">Serial</option>
                      <option value="Console">Console</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>端口速度</label>
                    <select v-model="port.port_speed">
                      <option value="">选择速度</option>
                      <option value="10Mbps">10Mbps</option>
                      <option value="100Mbps">100Mbps</option>
                      <option value="1Gbps">1Gbps</option>
                      <option value="10Gbps">10Gbps</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>状态</label>
                    <select v-model="port.status">
                      <option value="up">启用</option>
                      <option value="down">禁用</option>
                    </select>
                  </div>
                </div>
                <button type="button" @click="removePort(index)" class="btn btn-danger btn-sm">
                  🗑️ 删除
                </button>
              </div>
            </div>
            
            <div v-else class="no-ports">
              <p>暂无端口配置，点击"添加端口"按钮开始配置</p>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { networkApi } from '@/api/network'
import { locationApi } from '@/api/location'
import type { NetworkDevice, NetworkPort, StatusType } from '@/types/common'

const router = useRouter()
const route = useRoute()

// 响应式数据
const saving = ref(false)
const loading = ref(false)

// 表单数据
const formData = reactive<Partial<NetworkDevice> & { ports: Partial<NetworkPort>[] }>({
  name: '',
  device_type: '',
  brand: '',
  model: '',
  ip_address: '',
  mac_address: '',
  subnet_mask: '',
  gateway: '',
  dns_servers: '',
  building_id: undefined,
  floor_id: undefined,
  room_id: undefined,
  location_detail: '',
  status: 'offline' as StatusType,
  is_managed: false,
  x_position: undefined,
  y_position: undefined,
  serial_number: '',
  firmware_version: '',
  purchase_date: '',
  warranty_end_date: '',
  description: '',
  vlan_id: undefined,
  ports: []
})

// 验证错误
const errors = reactive<Record<string, string>>({})

// 位置数据
const buildings = ref<any[]>([])
const floors = ref<any[]>([])
const rooms = ref<any[]>([])

// 计算属性
const isEdit = computed(() => !!route.params.id)
const deviceId = computed(() => route.params.id ? Number(route.params.id) : null)

// 表单验证
const validateField = (field: string) => {
  errors[field] = ''
  
  switch (field) {
    case 'name':
      if (!formData.name?.trim()) {
        errors[field] = '设备名称不能为空'
      }
      break
    case 'device_type':
      if (!formData.device_type) {
        errors[field] = '请选择设备类型'
      }
      break
    case 'status':
      if (!formData.status) {
        errors[field] = '请选择设备状态'
      }
      break
    case 'ip_address':
      if (formData.ip_address && !isValidIP(formData.ip_address)) {
        errors[field] = 'IP地址格式不正确'
      }
      break
    case 'mac_address':
      if (formData.mac_address && !isValidMAC(formData.mac_address)) {
        errors[field] = 'MAC地址格式不正确'
      }
      break
  }
}

const validateForm = (): boolean => {
  validateField('name')
  validateField('device_type')
  validateField('status')
  validateField('ip_address')
  validateField('mac_address')
  
  return Object.values(errors).every(error => !error)
}

// 工具函数
const isValidIP = (ip: string): boolean => {
  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/
  if (!ipRegex.test(ip)) return false
  
  const parts = ip.split('.')
  return parts.every(part => {
    const num = parseInt(part)
    return num >= 0 && num <= 255
  })
}

const isValidMAC = (mac: string): boolean => {
  const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/
  return macRegex.test(mac)
}

// 数据加载
const loadBuildings = async () => {
  try {
    const response = await locationApi.getBuildings()
    if (response.success) {
      buildings.value = response.data
    }
  } catch (error) {
    console.error('加载建筑列表失败:', error)
  }
}

const loadFloors = async () => {
  if (!formData.building_id) {
    floors.value = []
    rooms.value = []
    formData.floor_id = undefined
    formData.room_id = undefined
    return
  }
  
  try {
    const response = await locationApi.getFloors(formData.building_id)
    if (response.success) {
      floors.value = response.data
    }
  } catch (error) {
    console.error('加载楼层列表失败:', error)
  }
}

const loadRooms = async () => {
  if (!formData.floor_id) {
    rooms.value = []
    formData.room_id = undefined
    return
  }
  
  try {
    const response = await locationApi.getRooms(formData.floor_id)
    if (response.success) {
      rooms.value = response.data
    }
  } catch (error) {
    console.error('加载房间列表失败:', error)
  }
}

const loadDevice = async () => {
  if (!deviceId.value) return
  
  loading.value = true
  try {
    const response = await networkApi.getDevice(deviceId.value)
    if (response.success) {
      Object.assign(formData, response.data)
      
      // 加载设备端口
      const portsResponse = await networkApi.getDevicePorts(deviceId.value)
      if (portsResponse.success) {
        formData.ports = portsResponse.data
      }
    }
  } catch (error) {
    console.error('加载设备信息失败:', error)
  } finally {
    loading.value = false
  }
}

// 端口管理
const addPort = () => {
  formData.ports.push({
    port_name: '',
    port_type: '',
    port_speed: '',
    status: 'up',
    is_connected: false
  })
}

const removePort = (index: number) => {
  formData.ports.splice(index, 1)
}

// 表单操作
const saveDevice = async () => {
  if (!validateForm()) {
    return
  }
  
  saving.value = true
  try {
    const deviceData = { ...formData }
    // @ts-ignore
    delete deviceData.ports // 端口单独处理
    
    let response
    if (isEdit.value && deviceId.value) {
      response = await networkApi.updateDevice(deviceId.value, deviceData)
    } else {
      response = await networkApi.createDevice(deviceData)
    }
    
    if (response.success) {
      console.log('设备保存成功')
      goBack()
    }
  } catch (error) {
    console.error('保存设备失败:', error)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  if (isEdit.value) {
    loadDevice()
  } else {
    // 重置基本字段
    formData.name = ''
    formData.device_type = ''
    formData.brand = ''
    formData.model = ''
    formData.ip_address = ''
    formData.mac_address = ''
    formData.subnet_mask = ''
    formData.gateway = ''
    formData.dns_servers = ''
    formData.building_id = undefined
    formData.floor_id = undefined
    formData.room_id = undefined
    formData.location_detail = ''
    formData.status = 'offline' as StatusType
    formData.is_managed = false
    formData.x_position = undefined
    formData.y_position = undefined
    formData.serial_number = ''
    formData.firmware_version = ''
    formData.purchase_date = ''
    formData.warranty_end_date = ''
    formData.description = ''
    formData.vlan_id = undefined
    formData.ports = []
  }
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
}

const goBack = () => {
  router.push('/app/network/devices')
}

// 初始化
onMounted(async () => {
  await loadBuildings()
  
  if (isEdit.value) {
    await loadDevice()
    if (formData.building_id) {
      await loadFloors()
      if (formData.floor_id) {
        await loadRooms()
      }
    }
  }
})
</script>

<style scoped>
.device-form-container {
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
  font-size: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.form-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.device-form {
  padding: 30px;
}

.form-section {
  margin-bottom: 40px;
}

.form-section h2 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 2px solid #e4e7ed;
  padding-bottom: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.required {
  color: #f56c6c;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #409eff;
}

.form-group input.error,
.form-group select.error {
  border-color: #f56c6c;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}

.checkbox-group {
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 8px;
  transform: scale(1.2);
}

.port-management {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
}

.port-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.port-count {
  color: #909399;
  font-size: 14px;
}

.port-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.port-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
  display: flex;
  gap: 16px;
  align-items: end;
}

.port-fields {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.port-fields .form-group {
  margin-bottom: 0;
}

.no-ports {
  text-align: center;
  color: #909399;
  padding: 40px 20px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-secondary {
  background: #909399;
  color: white;
}

.btn-secondary:hover {
  background: #a6a9ad;
}

.btn-danger {
  background: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background: #f78989;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .device-form-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .port-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .port-fields {
    grid-template-columns: 1fr;
  }
}
</style>