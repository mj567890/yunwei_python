<template>
  <div class="device-list-container">
    <div class="page-header">
      <h1>网络设备管理</h1>
      <div class="header-actions">
        <button @click="refreshDevices" class="btn btn-secondary">🔄 刷新</button>
        <button @click="createDevice" class="btn btn-primary">➕ 新增设备</button>
      </div>
    </div>

    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>设备名称</label>
          <input v-model="searchParams.name" placeholder="请输入设备名称" />
        </div>
        <div class="form-group">
          <label>设备类型</label>
          <select v-model="searchParams.device_type">
            <option value="">全部类型</option>
            <option value="交换机">交换机</option>
            <option value="路由器">路由器</option>
            <option value="防火墙">防火墙</option>
            <option value="服务器">服务器</option>
          </select>
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="searchParams.status">
            <option value="">全部状态</option>
            <option value="在线">在线</option>
            <option value="离线">离线</option>
            <option value="故障">故障</option>
          </select>
        </div>
        <div class="form-group">
          <button @click="searchDevices" class="btn btn-primary">🔍 搜索</button>
          <button @click="resetSearch" class="btn btn-secondary">🔄 重置</button>
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="device-table">
        <thead>
          <tr>
            <th width="60">序号</th>
            <th>设备名称</th>
            <th>设备类型</th>
            <th>IP地址</th>
            <th>位置</th>
            <th>状态</th>
            <th>端口数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(device, index) in deviceList" :key="device.id">
            <td class="row-number">{{ index + 1 }}</td>
            <td>{{ device.name }}</td>
            <td>{{ device.device_type }}</td>
            <td>{{ device.ip_address || '-' }}</td>
            <td>{{ device.full_location || '-' }}</td>
            <td>
              <span :class="`status-tag status-${getStatusClass(device.status)}`">
                {{ device.status }}
              </span>
            </td>
            <td>{{ device.port_count || 0 }}</td>
            <td class="actions">
              <button @click="viewDevice(device)" class="btn-sm btn-info">查看</button>
              <button @click="editDevice(device)" class="btn-sm btn-primary">编辑</button>
              <button @click="deleteDevice(device)" class="btn-sm btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 简单分页统计 -->
      <div v-if="deviceList.length > 0" class="device-stats">
        <span class="device-count">共 {{ deviceList.length }} 台设备</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, onMounted } from 'vue'
import { networkApi, type NetworkDevice } from '@/api/network'

const deviceList = ref<NetworkDevice[]>([])
const searchParams = ref({
  name: '',
  device_type: '',
  status: '',
  page: 1,
  page_size: 20
})

const loadDevices = async () => {
  try {
    const response = await networkApi.getDevices(searchParams.value)
    if (response.success) {
      deviceList.value = response.data.list || []
    }
  } catch (error) {
    console.error('加载设备列表失败:', error)
    // 模拟数据
    deviceList.value = [
      {
        id: 1,
        name: 'SW-001',
        device_type: '交换机',
        ip_address: '192.168.1.1',
        full_location: '机房A-机柜01',
        status: '在线',
        port_count: 24
      },
      {
        id: 2,
        name: 'RT-001',
        device_type: '路由器',
        ip_address: '192.168.1.254',
        full_location: '机房A-机柜02',
        status: '在线',
        port_count: 8
      }
    ]
  }
}

const getStatusClass = (status: string) => {
  return getCommonStatusClass(status)
}

const searchDevices = () => loadDevices()
const resetSearch = () => {
  searchParams.name = ''
  searchParams.device_type = ''
  searchParams.status = ''
  searchParams.page = 1
  searchParams.pageSize = 20
  loadDevices()
}
const refreshDevices = () => loadDevices()
const createDevice = () => console.log('新增设备')
const viewDevice = (device) => console.log('查看设备', device)
const editDevice = (device) => console.log('编辑设备', device)
const deleteDevice = (device) => console.log('删除设备', device)

onMounted(() => loadDevices())
</script>

<style scoped>
.device-list-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
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
}

.search-form {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-row {
  display: flex;
  gap: 20px;
  align-items: end;
}

.form-group {
  flex: 1;
  min-width: 150px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.device-table {
  width: 100%;
  border-collapse: collapse;
}

.device-table th,
.device-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.device-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.device-table tbody tr:hover {
  background: #f8f9fa;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-success {
  background: #f0f9ff;
  color: #67c23a;
  border: 1px solid #95de64;
}

.status-danger {
  background: #fff2f0;
  color: #f5222d;
  border: 1px solid #ffccc7;
}

.status-warning {
  background: #fffbf0;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-info { background: #409eff; color: white; }
.btn-primary { background: #67c23a; color: white; }
.btn-danger { background: #f56c6c; color: white; }

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-secondary {
  background: #909399;
  color: white;
}

.row-number {
  text-align: center;
  font-weight: 500;
  color: #909399;
  font-size: 13px;
  width: 60px;
}

.device-stats {
  padding: 16px;
  text-align: center;
  color: #606266;
  font-size: 14px;
  border-top: 1px solid #ebeef5;
}

.device-count {
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 4px;
}
</style>