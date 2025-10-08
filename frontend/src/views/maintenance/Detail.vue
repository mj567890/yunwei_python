<template>
  <div class="maintenance-detail-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="btn btn-secondary">← 返回</button>
        <div class="title-info">
          <h1>{{ maintenance?.title || '运维记录详情' }}</h1>
          <div class="maintenance-meta">
            <span class="maintenance-code">{{ maintenance?.record_code }}</span>
            <span :class="`status-tag status-${getMaintenanceStatusClass(maintenance?.status || '')}`">
              {{ maintenance?.status }}
            </span>
            <span :class="`priority-tag priority-${getPriorityClass(maintenance?.priority || '')}`">
              {{ maintenance?.priority }}
            </span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button @click="refreshData" :disabled="loading" class="btn btn-secondary">🔄 刷新</button>
        <button @click="printMaintenance" class="btn btn-secondary">🖨️ 打印</button>
        <button v-if="canEdit" @click="editMaintenance" class="btn btn-primary">✏️ 编辑</button>
        <button v-if="canStart" @click="startMaintenance" class="btn btn-warning">▶️ 开始</button>
        <button v-if="canComplete" @click="completeMaintenance" class="btn btn-success">✅ 完成</button>
        <button v-if="canCancel" @click="cancelMaintenance" class="btn btn-danger">❌ 取消</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner">🔄</div>
      <p>加载中...</p>
    </div>

    <div v-else-if="maintenance" class="detail-content">
      <!-- 基本信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📋 基本信息</h2>
          <div class="card-actions">
            <button v-if="canEdit" @click="editBasicInfo" class="btn-sm btn-primary">编辑</button>
          </div>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label>记录编码</label>
              <span class="maintenance-code">{{ maintenance.record_code }}</span>
            </div>
            <div class="info-item">
              <label>维护标题</label>
              <span>{{ maintenance.title }}</span>
            </div>
            <div class="info-item">
              <label>记录类型</label>
              <span>{{ maintenance.record_type }}</span>
            </div>
            <div class="info-item">
              <label>维护类别</label>
              <span>{{ maintenance.category }}</span>
            </div>
            <div class="info-item">
              <label>责任人</label>
              <span>{{ maintenance.responsible_person }}</span>
            </div>
            <div class="info-item">
              <label>所属部门</label>
              <span>{{ maintenance.department }}</span>
            </div>
            <div class="info-item">
              <label>优先级</label>
              <span :class="`priority-tag priority-${getPriorityClass(maintenance.priority)}`">
                {{ maintenance.priority }}
              </span>
            </div>
            <div class="info-item">
              <label>当前状态</label>
              <span :class="`status-tag status-${getMaintenanceStatusClass(maintenance.status)}`">
                {{ maintenance.status }}
              </span>
            </div>
            <div class="info-item">
              <label>开始时间</label>
              <span>{{ formatDate(maintenance.start_time) }}</span>
            </div>
            <div class="info-item">
              <label>计划完成</label>
              <span>{{ maintenance.planned_end_time ? formatDate(maintenance.planned_end_time) : '-' }}</span>
            </div>
            <div class="info-item">
              <label>实际完成</label>
              <span>{{ maintenance.actual_end_time ? formatDate(maintenance.actual_end_time) : '-' }}</span>
            </div>
            <div class="info-item">
              <label>涉及资产</label>
              <span>{{ maintenance.asset_count }}个</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 进度概览 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📊 进度概览</h2>
        </div>
        <div class="card-body">
          <div class="progress-overview">
            <div class="progress-stats">
              <div class="stat-item">
                <div class="stat-value">{{ maintenance.progress }}%</div>
                <div class="stat-label">完成进度</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ completedTasks }}</div>
                <div class="stat-label">已完成任务</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ totalTasks }}</div>
                <div class="stat-label">总任务数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ timeSpent }}</div>
                <div class="stat-label">已用时间(小时)</div>
              </div>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: maintenance.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ maintenance.progress }}% 完成</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 维护描述 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📝 维护描述</h2>
        </div>
        <div class="card-body">
          <div class="description-content">
            <p>{{ maintenance.description || '暂无描述' }}</p>
          </div>
        </div>
      </div>

      <!-- 涉及资产 -->
      <div class="info-card">
        <div class="card-header">
          <h2>💻 涉及资产</h2>
          <div class="card-actions">
            <button @click="addAsset" class="btn-sm btn-primary">添加资产</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="affectedAssets.length > 0" class="asset-list">
            <div v-for="asset in affectedAssets" :key="asset.id" class="asset-item">
              <div class="asset-info">
                <div class="asset-name">{{ asset.name }}</div>
                <div class="asset-code">{{ asset.asset_code }}</div>
                <div class="asset-location">{{ asset.location }}</div>
                <div class="asset-status">
                  <span :class="`status-tag status-${getStatusClass(asset.status)}`">
                    {{ asset.status }}
                  </span>
                </div>
              </div>
              <div class="asset-actions">
                <button @click="viewAsset(asset)" class="btn-sm btn-info">查看</button>
                <button @click="removeAsset(asset)" class="btn-sm btn-danger">移除</button>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无涉及资产</p>
          </div>
        </div>
      </div>

      <!-- 执行步骤 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📋 执行步骤</h2>
          <div class="card-actions">
            <button v-if="canAddStep" @click="addStep" class="btn-sm btn-primary">添加步骤</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="executionSteps.length > 0" class="steps-list">
            <div v-for="(step, index) in executionSteps" :key="step.id" class="step-item">
              <div class="step-number" :class="{ completed: step.status === '已完成' }">
                {{ index + 1 }}
              </div>
              <div class="step-content">
                <div class="step-header">
                  <span class="step-title">{{ step.title }}</span>
                  <span :class="`step-status status-${getStepStatusClass(step.status)}`">
                    {{ step.status }}
                  </span>
                </div>
                <div class="step-description">{{ step.description }}</div>
                <div class="step-meta">
                  <span v-if="step.executor_name" class="executor">执行人: {{ step.executor_name }}</span>
                  <span v-if="step.estimated_time" class="time">预计: {{ step.estimated_time }}分钟</span>
                  <span v-if="step.actual_time" class="time">实际: {{ step.actual_time }}分钟</span>
                  <span v-if="step.completed_at" class="date">完成: {{ formatDate(step.completed_at) }}</span>
                </div>
              </div>
              <div class="step-actions">
                <button v-if="step.status === '进行中'" @click="completeStep(step)" class="btn-sm btn-success">完成</button>
                <button v-if="step.status === '待执行'" @click="startStep(step)" class="btn-sm btn-warning">开始</button>
                <button @click="editStep(step)" class="btn-sm btn-primary">编辑</button>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无执行步骤</p>
            <button @click="addStep" class="btn btn-primary">添加步骤</button>
          </div>
        </div>
      </div>

      <!-- 执行记录 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📜 执行记录</h2>
          <div class="card-actions">
            <button v-if="canAddRecord" @click="addRecord" class="btn-sm btn-primary">添加记录</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="executionRecords.length > 0" class="record-timeline">
            <div v-for="record in executionRecords" :key="record.id" class="timeline-item">
              <div class="timeline-dot" :class="`dot-${getRecordTypeClass(record.record_type)}`"></div>
              <div class="timeline-content">
                <div class="record-header">
                  <span class="record-type">{{ getRecordTypeName(record.record_type) }}</span>
                  <span class="record-date">{{ formatDate(record.created_at) }}</span>
                </div>
                <div class="record-details">
                  <p>{{ record.description }}</p>
                  <div v-if="record.images && record.images.length > 0" class="record-images">
                    <img
                      v-for="image in record.images"
                      :key="image.id"
                      :src="image.thumbnail_url"
                      :alt="image.name"
                      class="record-image"
                      @click="previewImage(image)"
                    >
                  </div>
                </div>
                <div class="record-user">
                  <span>记录人: {{ record.recorder_name }}</span>
                  <span v-if="record.time_spent">耗时: {{ record.time_spent }}分钟</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无执行记录</p>
          </div>
        </div>
      </div>

      <!-- 结果总结 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📊 结果总结</h2>
          <div class="card-actions">
            <button v-if="canEditSummary" @click="editSummary" class="btn-sm btn-primary">编辑</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="maintenance.summary" class="summary-content">
            <div class="summary-text">
              <p>{{ maintenance.summary }}</p>
            </div>
            <div class="summary-stats">
              <div class="stat-row">
                <label>维护结果:</label>
                <span :class="`result-tag result-${maintenance.result_status}`">
                  {{ maintenance.result_status || '进行中' }}
                </span>
              </div>
              <div class="stat-row">
                <label>实际耗时:</label>
                <span>{{ maintenance.actual_duration || '-' }}小时</span>
              </div>
              <div class="stat-row">
                <label>成本费用:</label>
                <span>{{ maintenance.cost ? '¥' + maintenance.cost.toLocaleString() : '-' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>维护完成后将显示结果总结</p>
            <button v-if="canEditSummary" @click="addSummary" class="btn btn-primary">添加总结</button>
          </div>
        </div>
      </div>

      <!-- 附件文件 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📎 附件文件</h2>
          <div class="card-actions">
            <button @click="uploadAttachment" class="btn-sm btn-primary">上传附件</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="attachments.length > 0" class="attachment-list">
            <div v-for="file in attachments" :key="file.id" class="attachment-item">
              <div class="file-icon">{{ getFileIcon(file.file_type) }}</div>
              <div class="file-info">
                <div class="file-name">{{ file.original_name }}</div>
                <div class="file-meta">
                  <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
                  <span class="file-date">{{ formatDate(file.created_at) }}</span>
                  <span class="file-uploader">{{ file.uploader_name }}</span>
                </div>
              </div>
              <div class="file-actions">
                <button @click="downloadFile(file)" class="btn-sm btn-info">下载</button>
                <button @click="previewFile(file)" class="btn-sm btn-secondary">预览</button>
                <button @click="deleteAttachment(file)" class="btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无附件文件</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="!loading" class="error-state">
      <div class="error-icon">❌</div>
      <p>运维记录加载失败</p>
      <button @click="refreshData" class="btn btn-primary">重新加载</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { maintenanceApi } from '@/api/maintenance'
import type { MaintenanceRecord } from '@/types/common'
import { getMaintenanceStatusClass, getPriorityClass, getStatusClass } from '@/types/common'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const maintenance = ref<MaintenanceRecord | null>(null)
const affectedAssets = ref<any[]>([])
const executionSteps = ref<any[]>([])
const executionRecords = ref<any[]>([])
const attachments = ref<any[]>([])

// 计算属性
const maintenanceId = computed(() => route.params.id ? Number(route.params.id) : null)

const canEdit = computed(() => {
  if (!maintenance.value) return false
  return ['计划中', '进行中'].includes(maintenance.value.status)
})

const canStart = computed(() => {
  if (!maintenance.value) return false
  return maintenance.value.status === '计划中'
})

const canComplete = computed(() => {
  if (!maintenance.value) return false
  return maintenance.value.status === '进行中' && maintenance.value.progress === 100
})

const canCancel = computed(() => {
  if (!maintenance.value) return false
  return ['计划中', '进行中'].includes(maintenance.value.status)
})

const canAddStep = computed(() => {
  if (!maintenance.value) return false
  return ['计划中', '进行中'].includes(maintenance.value.status)
})

const canAddRecord = computed(() => {
  if (!maintenance.value) return false
  return maintenance.value.status === '进行中'
})

const canEditSummary = computed(() => {
  if (!maintenance.value) return false
  return ['进行中', '已完成'].includes(maintenance.value.status)
})

const completedTasks = computed(() => 
  executionSteps.value.filter(step => step.status === '已完成').length
)

const totalTasks = computed(() => executionSteps.value.length)

const timeSpent = computed(() => {
  return executionRecords.value.reduce((total, record) => total + (record.time_spent || 0), 0) / 60
})

// 数据加载
const loadMaintenanceDetail = async () => {
  if (!maintenanceId.value) return
  
  loading.value = true
  try {
    // 加载维护记录基本信息
    const response = await maintenanceApi.getMaintenance(maintenanceId.value)
    if (response.success) {
      maintenance.value = response.data
    }
    
    // 并行加载关联数据
    await Promise.all([
      loadAffectedAssets(),
      loadExecutionSteps(),
      loadExecutionRecords(),
      loadAttachments()
    ])
    
  } catch (error) {
    console.error('加载运维记录详情失败:', error)
  } finally {
    loading.value = false
  }
}

const loadAffectedAssets = async () => {
  try {
    // 模拟数据
    affectedAssets.value = [
      {
        id: 1,
        name: '服务器-001',
        asset_code: 'SRV20240001',
        location: '机房A-机柜01',
        status: '在用'
      },
      {
        id: 2,
        name: '交换机-002',
        asset_code: 'SW20240002',
        location: '机房A-机柜02',
        status: '在用'
      }
    ]
  } catch (error) {
    console.error('加载涉及资产失败:', error)
  }
}

const loadExecutionSteps = async () => {
  try {
    // 模拟数据
    executionSteps.value = [
      {
        id: 1,
        title: '停止服务',
        description: '停止相关应用服务，确保数据安全',
        status: '已完成',
        executor_name: '张三',
        estimated_time: 30,
        actual_time: 25,
        completed_at: '2024-01-15 10:30:00'
      },
      {
        id: 2,
        title: '系统备份',
        description: '备份重要数据和配置文件',
        status: '已完成',
        executor_name: '李四',
        estimated_time: 60,
        actual_time: 55,
        completed_at: '2024-01-15 11:25:00'
      },
      {
        id: 3,
        title: '系统维护',
        description: '执行系统维护操作',
        status: '进行中',
        executor_name: '王五',
        estimated_time: 120,
        actual_time: null,
        completed_at: null
      }
    ]
  } catch (error) {
    console.error('加载执行步骤失败:', error)
  }
}

const loadExecutionRecords = async () => {
  try {
    // 模拟数据
    executionRecords.value = [
      {
        id: 1,
        record_type: 'start',
        description: '开始执行维护任务',
        recorder_name: '张三',
        created_at: '2024-01-15 10:00:00',
        time_spent: null,
        images: []
      },
      {
        id: 2,
        record_type: 'progress',
        description: '服务停止完成，开始备份数据',
        recorder_name: '张三',
        created_at: '2024-01-15 10:30:00',
        time_spent: 30,
        images: [
          {
            id: 1,
            name: '服务停止截图.png',
            thumbnail_url: '/api/files/thumbnail/1'
          }
        ]
      }
    ]
  } catch (error) {
    console.error('加载执行记录失败:', error)
  }
}

const loadAttachments = async () => {
  try {
    // 模拟数据
    attachments.value = [
      {
        id: 1,
        original_name: '维护计划.pdf',
        file_type: 'application/pdf',
        file_size: 2048576,
        file_url: '/api/files/download/1',
        uploader_name: '张三',
        created_at: '2024-01-15 09:00:00'
      }
    ]
  } catch (error) {
    console.error('加载附件失败:', error)
  }
}

// 工具函数
const formatDate = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileIcon = (fileType: string): string => {
  if (fileType.includes('pdf')) return '📄'
  if (fileType.includes('image')) return '🖼️'
  if (fileType.includes('word')) return '📝'
  if (fileType.includes('excel')) return '📊'
  return '📁'
}

const getStepStatusClass = (status: string): string => {
  const classes = {
    '待执行': 'info',
    '进行中': 'warning',
    '已完成': 'success',
    '已跳过': 'secondary'
  }
  return classes[status as keyof typeof classes] || 'info'
}

const getRecordTypeClass = (type: string): string => {
  const classes = {
    start: 'success',
    progress: 'primary',
    issue: 'warning',
    complete: 'success'
  }
  return classes[type as keyof typeof classes] || 'info'
}

const getRecordTypeName = (type: string): string => {
  const names = {
    start: '开始执行',
    progress: '进度更新',
    issue: '问题记录',
    complete: '完成'
  }
  return names[type as keyof typeof names] || type
}

// 事件处理
const goBack = () => {
  router.push('/app/maintenance')
}

const refreshData = () => {
  loadMaintenanceDetail()
}

const printMaintenance = () => {
  window.print()
}

const editMaintenance = () => {
  router.push(`/app/maintenance/edit/${maintenanceId.value}`)
}

const startMaintenance = () => {
  console.log('开始维护')
  // TODO: 实现开始维护
}

const completeMaintenance = () => {
  console.log('完成维护')
  // TODO: 实现完成维护
}

const cancelMaintenance = () => {
  console.log('取消维护')
  // TODO: 实现取消维护
}

const editBasicInfo = () => {
  console.log('编辑基本信息')
  // TODO: 实现编辑基本信息
}

const addAsset = () => {
  console.log('添加资产')
  // TODO: 实现添加资产
}

const viewAsset = (asset: any) => {
  router.push(`/app/assets/detail/${asset.id}`)
}

const removeAsset = (asset: any) => {
  console.log('移除资产', asset)
  // TODO: 实现移除资产
}

const addStep = () => {
  console.log('添加执行步骤')
  // TODO: 实现添加执行步骤
}

const startStep = (step: any) => {
  console.log('开始执行步骤', step)
  // TODO: 实现开始执行步骤
}

const completeStep = (step: any) => {
  console.log('完成执行步骤', step)
  // TODO: 实现完成执行步骤
}

const editStep = (step: any) => {
  console.log('编辑执行步骤', step)
  // TODO: 实现编辑执行步骤
}

const addRecord = () => {
  console.log('添加执行记录')
  // TODO: 实现添加执行记录
}

const editSummary = () => {
  console.log('编辑结果总结')
  // TODO: 实现编辑结果总结
}

const addSummary = () => {
  console.log('添加结果总结')
  // TODO: 实现添加结果总结
}

const uploadAttachment = () => {
  console.log('上传附件')
  // TODO: 实现上传附件
}

const downloadFile = (file: any) => {
  window.open(file.file_url, '_blank')
}

const previewFile = (file: any) => {
  console.log('预览文件', file)
  // TODO: 实现文件预览
}

const previewImage = (image: any) => {
  console.log('预览图片', image)
  // TODO: 实现图片预览
}

const deleteAttachment = async (file: any) => {
  if (confirm(`确认删除附件 "${file.original_name}" 吗？`)) {
    try {
      // 这里应该调用删除API
      const index = attachments.value.findIndex(f => f.id === file.id)
      if (index > -1) {
        attachments.value.splice(index, 1)
      }
      console.log('删除成功')
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

// 初始化
onMounted(() => {
  loadMaintenanceDetail()
})
</script>

<style scoped>
.maintenance-detail-container {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-info h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
}

.maintenance-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.maintenance-code {
  font-family: monospace;
  color: #409eff;
  font-weight: 600;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-spinner {
  font-size: 32px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.detail-content {
  display: grid;
  gap: 20px;
}

.info-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #e4e7ed;
  background: #f8f9fa;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-body {
  padding: 30px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.info-item span {
  color: #303133;
  font-size: 16px;
}

.status-tag, .priority-tag {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  width: fit-content;
}

.status-info { background: #e1f3ff; color: #409eff; }
.status-warning { background: #fdf6ec; color: #e6a23c; }
.status-success { background: #f0f9ff; color: #67c23a; }
.status-danger { background: #fef0f0; color: #f56c6c; }

.priority-low { background: #f4f4f5; color: #909399; }
.priority-medium { background: #e1f3ff; color: #409eff; }
.priority-high { background: #fdf6ec; color: #e6a23c; }
.priority-urgent { background: #fef0f0; color: #f56c6c; }

.progress-overview {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-bar {
  flex: 1;
  height: 12px;
  background: #f0f2f5;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #66b1ff);
  transition: width 0.3s;
}

.progress-text {
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
}

.description-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.description-content p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.asset-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.asset-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.asset-info {
  flex: 1;
}

.asset-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.asset-code {
  font-family: monospace;
  color: #409eff;
  font-size: 12px;
  margin-bottom: 2px;
}

.asset-location {
  color: #909399;
  font-size: 12px;
  margin-bottom: 4px;
}

.asset-status {
  margin-top: 4px;
}

.asset-actions {
  display: flex;
  gap: 8px;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e4e7ed;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.step-number.completed {
  background: #67c23a;
}

.step-content {
  flex: 1;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.step-title {
  font-weight: 500;
  color: #303133;
}

.step-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.step-description {
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.5;
}

.step-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.step-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-timeline {
  position: relative;
  padding-left: 30px;
}

.timeline-item {
  position: relative;
  padding-bottom: 24px;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: -22px;
  top: 20px;
  bottom: -8px;
  width: 2px;
  background: #e4e7ed;
}

.timeline-dot {
  position: absolute;
  left: -27px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #e4e7ed;
}

.dot-success { background: #67c23a; }
.dot-primary { background: #409eff; }
.dot-warning { background: #e6a23c; }

.timeline-content {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-type {
  font-weight: 500;
  color: #303133;
}

.record-date {
  font-size: 12px;
  color: #909399;
}

.record-details p {
  margin: 0 0 8px 0;
  color: #606266;
  line-height: 1.5;
}

.record-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.record-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid #e4e7ed;
}

.record-user {
  margin-top: 8px;
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.summary-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #67c23a;
}

.summary-text p {
  margin: 0 0 16px 0;
  color: #303133;
  line-height: 1.6;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-row {
  display: flex;
  gap: 12px;
}

.stat-row label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.result-tag {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.result-success { background: #f0f9ff; color: #67c23a; }
.result-warning { background: #fdf6ec; color: #e6a23c; }

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.file-icon {
  font-size: 24px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.file-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.no-data {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.no-data p {
  margin-bottom: 16px;
}

.error-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
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

.btn-warning {
  background: #e6a23c;
  color: white;
}

.btn-warning:hover {
  background: #ebb563;
}

.btn-success {
  background: #67c23a;
  color: white;
}

.btn-success:hover {
  background: #85ce61;
}

.btn-info {
  background: #909399;
  color: white;
}

.btn-info:hover {
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
  .maintenance-detail-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-left {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .progress-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .asset-item,
  .step-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .timeline-item {
    padding-left: 0;
  }
  
  .timeline-dot {
    left: -6px;
  }
  
  .attachment-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .progress-stats {
    grid-template-columns: 1fr;
  }
  
  .maintenance-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

/* 打印样式 */
@media print {
  .page-header .header-actions,
  .card-actions,
  .asset-actions,
  .step-actions,
  .file-actions {
    display: none;
  }
  
  .maintenance-detail-container {
    background: white;
    padding: 0;
  }
  
  .info-card {
    box-shadow: none;
    border: 1px solid #e4e7ed;
    margin-bottom: 20px;
  }
}
</style>