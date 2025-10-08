<template>
  <div class="device-detail-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
          <div class="device-title">
            <h2>{{ device.name || '设备详情' }}</h2>
            <el-tag 
              :type="device.status === 'online' ? 'success' : device.status === 'offline' ? 'danger' : 'warning'"
              class="status-tag"
            >
              {{ statusMap[device.status] || '未知' }}
            </el-tag>
          </div>
        </div>
        <div class="header-actions">
          <el-dropdown @command="handleAction">
            <el-button type="primary">
              操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="edit">编辑设备</el-dropdown-item>
                <el-dropdown-item command="ping">Ping测试</el-dropdown-item>
                <el-dropdown-item command="restart">重启设备</el-dropdown-item>
                <el-dropdown-item command="backup">备份配置</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除设备</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <div class="page-content">
      <el-row :gutter="24">
        <el-col :span="16">
          <!-- 基本信息 -->
          <el-card title="基本信息" class="info-card">
            <div class="device-info">
              <div class="info-grid">
                <div class="info-item">
                  <label>设备名称</label>
                  <span>{{ device.name }}</span>
                </div>
                <div class="info-item">
                  <label>设备类型</label>
                  <span>{{ typeMap[device.type] }}</span>
                </div>
                <div class="info-item">
                  <label>IP地址</label>
                  <span>{{ device.ip_address }}</span>
                </div>
                <div class="info-item">
                  <label>MAC地址</label>
                  <span>{{ device.mac_address }}</span>
                </div>
                <div class="info-item">
                  <label>品牌型号</label>
                  <span>{{ device.brand }} {{ device.model }}</span>
                </div>
                <div class="info-item">
                  <label>序列号</label>
                  <span>{{ device.serial_number }}</span>
                </div>
                <div class="info-item">
                  <label>固件版本</label>
                  <span>{{ device.firmware_version }}</span>
                </div>
                <div class="info-item">
                  <label>位置</label>
                  <span>{{ device.location }}</span>
                </div>
                <div class="info-item">
                  <label>管理员</label>
                  <span>{{ device.administrator }}</span>
                </div>
                <div class="info-item">
                  <label>创建时间</label>
                  <span>{{ formatDate(device.created_at) }}</span>
                </div>
                <div class="info-item">
                  <label>最后更新</label>
                  <span>{{ formatDate(device.updated_at) }}</span>
                </div>
                <div class="info-item full-width">
                  <label>备注</label>
                  <span>{{ device.remarks || '无' }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 性能监控 -->
          <el-card title="性能监控" class="info-card">
            <div class="performance-metrics">
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-title">CPU使用率</span>
                  <span class="metric-value" :class="getCpuClass(performance.cpu_usage)">
                    {{ performance.cpu_usage }}%
                  </span>
                </div>
                <el-progress 
                  :percentage="performance.cpu_usage" 
                  :status="getCpuStatus(performance.cpu_usage)"
                  :show-text="false"
                />
              </div>
              
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-title">内存使用率</span>
                  <span class="metric-value" :class="getMemoryClass(performance.memory_usage)">
                    {{ performance.memory_usage }}%
                  </span>
                </div>
                <el-progress 
                  :percentage="performance.memory_usage" 
                  :status="getMemoryStatus(performance.memory_usage)"
                  :show-text="false"
                />
              </div>
              
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-title">网络流量</span>
                  <span class="metric-value">{{ performance.network_traffic }}</span>
                </div>
                <div class="traffic-details">
                  <span>入流量: {{ performance.traffic_in }}</span>
                  <span>出流量: {{ performance.traffic_out }}</span>
                </div>
              </div>
              
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-title">连接数</span>
                  <span class="metric-value">{{ performance.connections }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 端口信息 -->
          <el-card title="端口信息" class="info-card">
            <el-table :data="ports" stripe>
              <el-table-column prop="port_number" label="端口" width="80" />
              <el-table-column prop="port_name" label="端口名称" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'up' ? 'success' : 'danger'" size="small">
                    {{ row.status === 'up' ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="speed" label="速率" width="120" />
              <el-table-column prop="duplex" label="双工模式" width="120" />
              <el-table-column prop="vlan" label="VLAN" width="80" />
              <el-table-column prop="connected_device" label="连接设备" />
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 实时状态 -->
          <el-card title="实时状态" class="status-card">
            <div class="status-indicators">
              <div class="status-item">
                <div class="status-icon online">●</div>
                <div class="status-content">
                  <div class="status-title">设备状态</div>
                  <div class="status-value">{{ statusMap[device.status] }}</div>
                </div>
              </div>
              
              <div class="status-item">
                <div class="status-icon">📡</div>
                <div class="status-content">
                  <div class="status-title">延迟</div>
                  <div class="status-value">{{ performance.latency }}ms</div>
                </div>
              </div>
              
              <div class="status-item">
                <div class="status-icon">⏱️</div>
                <div class="status-content">
                  <div class="status-title">运行时间</div>
                  <div class="status-value">{{ performance.uptime }}</div>
                </div>
              </div>
              
              <div class="status-item">
                <div class="status-icon">🌡️</div>
                <div class="status-content">
                  <div class="status-title">温度</div>
                  <div class="status-value" :class="getTempClass(performance.temperature)">
                    {{ performance.temperature }}°C
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 快速操作 -->
          <el-card title="快速操作" class="quick-actions-card">
            <div class="action-buttons">
              <el-button @click="pingDevice" :loading="pinging" type="primary" size="small" style="width: 100%">
                Ping测试
              </el-button>
              <el-button @click="refreshStatus" :loading="refreshing" size="small" style="width: 100%">
                刷新状态
              </el-button>
              <el-button @click="showConfig" size="small" style="width: 100%">
                查看配置
              </el-button>
              <el-button @click="downloadLogs" size="small" style="width: 100%">
                下载日志
              </el-button>
            </div>
          </el-card>

          <!-- 警告信息 -->
          <el-card title="警告信息" class="alerts-card" v-if="alerts.length > 0">
            <div class="alert-list">
              <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.level">
                <div class="alert-icon">⚠️</div>
                <div class="alert-content">
                  <div class="alert-title">{{ alert.title }}</div>
                  <div class="alert-time">{{ formatDate(alert.created_at) }}</div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 相关设备 -->
          <el-card title="相关设备" class="related-devices-card">
            <div class="related-list">
              <div v-for="related in relatedDevices" :key="related.id" class="related-item">
                <div class="related-info">
                  <div class="related-name">{{ related.name }}</div>
                  <div class="related-ip">{{ related.ip_address }}</div>
                </div>
                <el-tag :type="related.status === 'online' ? 'success' : 'danger'" size="small">
                  {{ statusMap[related.status] }}
                </el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 配置查看对话框 -->
    <el-dialog v-model="configVisible" title="设备配置" width="80%" :before-close="closeConfig">
      <pre class="config-content">{{ deviceConfig }}</pre>
      <template #footer>
        <el-button @click="configVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadConfig">下载配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const deviceId = route.params.id as string
const pinging = ref(false)
const refreshing = ref(false)
const configVisible = ref(false)

const device = ref({
  id: '',
  name: '',
  type: '',
  ip_address: '',
  mac_address: '',
  brand: '',
  model: '',
  serial_number: '',
  firmware_version: '',
  location: '',
  administrator: '',
  status: 'online',
  remarks: '',
  created_at: '',
  updated_at: ''
})

const performance = ref({
  cpu_usage: 0,
  memory_usage: 0,
  network_traffic: '',
  traffic_in: '',
  traffic_out: '',
  connections: 0,
  latency: 0,
  uptime: '',
  temperature: 0
})

const ports = ref([
  { port_number: 1, port_name: 'GigabitEthernet0/1', status: 'up', speed: '1000M', duplex: 'Full', vlan: '100', connected_device: 'Switch-001' },
  { port_number: 2, port_name: 'GigabitEthernet0/2', status: 'down', speed: '-', duplex: '-', vlan: '-', connected_device: '-' },
  { port_number: 3, port_name: 'GigabitEthernet0/3', status: 'up', speed: '1000M', duplex: 'Full', vlan: '200', connected_device: 'Router-002' }
])

const alerts = ref([
  { id: 1, title: 'CPU使用率过高', level: 'warning', created_at: '2024-01-15 14:30:00' },
  { id: 2, title: '端口2连接断开', level: 'error', created_at: '2024-01-15 13:15:00' }
])

const relatedDevices = ref([
  { id: 1, name: 'Switch-001', ip_address: '192.168.1.11', status: 'online' },
  { id: 2, name: 'Router-002', ip_address: '192.168.1.12', status: 'offline' },
  { id: 3, name: 'Firewall-001', ip_address: '192.168.1.13', status: 'online' }
])

const deviceConfig = ref('')

const statusMap: Record<string, string> = {
  online: '在线',
  offline: '离线',
  maintenance: '维护中',
  error: '故障'
}

const typeMap: Record<string, string> = {
  switch: '交换机',
  router: '路由器',
  firewall: '防火墙',
  server: '服务器',
  access_point: '无线接入点'
}

const loadDeviceData = async () => {
  try {
    // 模拟API调用
    const mockDevice = {
      id: deviceId,
      name: 'Core-Switch-001',
      type: 'switch',
      ip_address: '192.168.1.10',
      mac_address: '00:1A:2B:3C:4D:5E',
      brand: 'Cisco',
      model: 'Catalyst 3850-24P',
      serial_number: 'FCW2140L0ZK',
      firmware_version: '16.12.04',
      location: '机房A-机柜001',
      administrator: '张三',
      status: 'online',
      remarks: '核心交换机，负责主要网络流量转发',
      created_at: '2024-01-10 09:00:00',
      updated_at: '2024-01-15 14:30:00'
    }
    
    const mockPerformance = {
      cpu_usage: 45,
      memory_usage: 68,
      network_traffic: '1.2 GB/s',
      traffic_in: '650 MB/s',
      traffic_out: '550 MB/s',
      connections: 1250,
      latency: 2,
      uptime: '15天 3小时 45分钟',
      temperature: 42
    }
    
    device.value = mockDevice
    performance.value = mockPerformance
  } catch (error) {
    console.error('加载设备数据失败:', error)
    ElMessage.error('加载设备数据失败')
  }
}

const getCpuClass = (usage: number) => {
  if (usage > 80) return 'high'
  if (usage > 60) return 'medium'
  return 'normal'
}

const getCpuStatus = (usage: number) => {
  if (usage > 80) return 'exception'
  if (usage > 60) return 'warning'
  return 'success'
}

const getMemoryClass = (usage: number) => {
  if (usage > 85) return 'high'
  if (usage > 70) return 'medium'
  return 'normal'
}

const getMemoryStatus = (usage: number) => {
  if (usage > 85) return 'exception'
  if (usage > 70) return 'warning'
  return 'success'
}

const getTempClass = (temp: number) => {
  if (temp > 70) return 'high'
  if (temp > 50) return 'medium'
  return 'normal'
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const handleAction = (command: string) => {
  switch (command) {
    case 'edit':
      router.push(`/app/network/devices/${deviceId}/edit`)
      break
    case 'ping':
      pingDevice()
      break
    case 'restart':
      restartDevice()
      break
    case 'backup':
      backupConfig()
      break
    case 'delete':
      deleteDevice()
      break
  }
}

const pingDevice = async () => {
  pinging.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('Ping测试成功，延迟: 2ms')
  } catch (error) {
    ElMessage.error('Ping测试失败')
  } finally {
    pinging.value = false
  }
}

const refreshStatus = async () => {
  refreshing.value = true
  try {
    await loadDeviceData()
    ElMessage.success('状态刷新成功')
  } catch (error) {
    ElMessage.error('状态刷新失败')
  } finally {
    refreshing.value = false
  }
}

const showConfig = async () => {
  try {
    // 模拟获取配置
    deviceConfig.value = `hostname Core-Switch-001
!
version 16.12
!
interface GigabitEthernet0/1
 description Connection to Switch-001
 switchport mode access
 switchport access vlan 100
!
interface GigabitEthernet0/2
 description Unused
 shutdown
!
interface GigabitEthernet0/3
 description Connection to Router-002
 switchport mode access
 switchport access vlan 200
!
ip route 0.0.0.0 0.0.0.0 192.168.1.1
!
end`
    configVisible.value = true
  } catch (error) {
    ElMessage.error('获取配置失败')
  }
}

const downloadConfig = () => {
  const blob = new Blob([deviceConfig.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${device.value.name}-config.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const downloadLogs = () => {
  ElMessage.info('正在准备日志文件...')
  // 模拟下载日志
  setTimeout(() => {
    ElMessage.success('日志文件下载完成')
  }, 2000)
}

const closeConfig = () => {
  configVisible.value = false
}

const restartDevice = async () => {
  try {
    await ElMessageBox.confirm('确定要重启设备吗？设备将短暂离线。', '确认重启', {
      type: 'warning'
    })
    ElMessage.success('设备重启命令已发送')
  } catch {
    // 用户取消
  }
}

const backupConfig = async () => {
  try {
    ElMessage.info('正在备份配置...')
    await new Promise(resolve => setTimeout(resolve, 3000))
    ElMessage.success('配置备份完成')
  } catch (error) {
    ElMessage.error('配置备份失败')
  }
}

const deleteDevice = async () => {
  try {
    await ElMessageBox.confirm('确定要删除此设备吗？此操作不可恢复。', '确认删除', {
      type: 'warning'
    })
    ElMessage.success('设备删除成功')
    router.push('/app/network/devices')
  } catch {
    // 用户取消
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadDeviceData()
})
</script>

<style scoped>
.device-detail-page {
  background: #f5f7fa;
  min-height: 100%;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.device-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.device-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.status-tag {
  font-size: 12px;
}

.page-content {
  padding: 24px;
}

.info-card {
  margin-bottom: 24px;
}

.info-card :deep(.el-card__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  font-weight: 500;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.info-item span {
  color: #303133;
  word-break: break-word;
}

.performance-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-title {
  font-weight: 500;
  color: #303133;
}

.metric-value {
  font-weight: 600;
}

.metric-value.normal { color: #67c23a; }
.metric-value.medium { color: #e6a23c; }
.metric-value.high { color: #f56c6c; }

.traffic-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.status-card {
  margin-bottom: 24px;
}

.status-indicators {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.status-icon {
  font-size: 20px;
  min-width: 20px;
}

.status-icon.online {
  color: #67c23a;
}

.status-content {
  flex: 1;
}

.status-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.status-value {
  font-weight: 500;
  color: #303133;
}

.quick-actions-card {
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alerts-card {
  margin-bottom: 24px;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid;
}

.alert-item.warning {
  background: #fdf6ec;
  border-color: #e6a23c;
}

.alert-item.error {
  background: #fef0f0;
  border-color: #f56c6c;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.alert-time {
  font-size: 12px;
  color: #909399;
}

.related-devices-card {
  margin-bottom: 24px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.related-name {
  font-weight: 500;
  color: #303133;
}

.related-ip {
  font-size: 12px;
  color: #909399;
}

.config-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  max-height: 400px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .page-content {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    height: auto;
    padding: 16px 0;
  }
  
  .header-left {
    width: 100%;
    margin-bottom: 12px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .performance-metrics {
    grid-template-columns: 1fr;
  }
}
</style>