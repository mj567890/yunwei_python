<template>
  <div class="location-detail-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
          <div class="location-title">
            <h2>{{ locationInfo.name }}</h2>
            <el-tag :type="getStatusType(locationInfo.status)" size="small">
              {{ getStatusText(locationInfo.status) }}
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
                <el-dropdown-item command="edit">编辑位置</el-dropdown-item>
                <el-dropdown-item command="scan">扫描设备</el-dropdown-item>
                <el-dropdown-item command="export">导出信息</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除位置</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <div class="page-content">
      <el-row :gutter="24">
        <el-col :span="16">
          <!-- 位置信息 -->
          <el-card title="位置信息" class="info-card">
            <div class="location-info">
              <div class="info-grid">
                <div class="info-item">
                  <label>位置名称</label>
                  <span>{{ locationInfo.name }}</span>
                </div>
                <div class="info-item">
                  <label>位置代码</label>
                  <span>{{ locationInfo.code }}</span>
                </div>
                <div class="info-item">
                  <label>位置类型</label>
                  <span>{{ getLocationTypeName(locationInfo.type) }}</span>
                </div>
                <div class="info-item">
                  <label>详细地址</label>
                  <span>{{ locationInfo.address }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 设备列表 -->
          <el-card title="设备清单" class="devices-card">
            <el-table :data="deviceList" stripe>
              <el-table-column prop="name" label="设备名称" />
              <el-table-column prop="type" label="设备类型" width="120" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
                    {{ row.status === 'online' ? '在线' : '离线' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 快速操作 -->
          <el-card title="快速操作" class="actions-card">
            <div class="action-buttons">
              <el-button @click="editLocation" style="width: 100%">编辑信息</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const locationId = route.params.id as string

const locationInfo = ref({
  id: '',
  name: '主机房A',
  code: 'DC-A-001',
  type: 'datacenter',
  address: '北京市朝阳区科技园区1号楼',
  status: 'active'
})

const deviceList = ref([
  {
    id: 1,
    name: 'Core-Switch-001',
    type: 'switch',
    status: 'online'
  }
])

const getLocationTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'datacenter': '数据中心',
    'room': '房间'
  }
  return typeMap[type] || '未知'
}

const getStatusType = (status: string) => {
  return status === 'active' ? 'success' : 'info'
}

const getStatusText = (status: string) => {
  return status === 'active' ? '正常' : '停用'
}

const handleAction = (command: string) => {
  console.log(command)
}

const editLocation = () => {
  router.push(`/app/locations/${locationId}/edit`)
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  // 加载位置数据
})
</script>

<style scoped>
.location-detail-page {
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

.location-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.location-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.page-content {
  padding: 24px;
}

.info-card,
.devices-card {
  margin-bottom: 24px;
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

.info-item label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.info-item span {
  color: #303133;
}

.actions-card {
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>