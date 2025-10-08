<template>
  <div class="fault-detail-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="btn btn-secondary">← 返回</button>
        <div class="title-info">
          <h1>{{ fault?.title || '故障详情' }}</h1>
          <div class="fault-meta">
            <span class="fault-code">{{ fault?.fault_code }}</span>
            <span :class="`status-tag status-${getFaultStatusClass(fault?.status || '')}`">
              {{ fault?.status }}
            </span>
            <span :class="`priority-tag priority-${getPriorityClass(fault?.priority || '')}`">
              {{ fault?.priority }}
            </span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button @click="refreshData" :disabled="loading" class="btn btn-secondary">🔄 刷新</button>
        <button @click="printFault" class="btn btn-secondary">🖨️ 打印</button>
        <button v-if="canEdit" @click="editFault" class="btn btn-primary">✏️ 编辑</button>
        <button v-if="canProcess" @click="processFault" class="btn btn-warning">🔧 处理</button>
        <button v-if="canClose" @click="closeFault" class="btn btn-success">✅ 关闭</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner">🔄</div>
      <p>加载中...</p>
    </div>

    <div v-else-if="fault" class="detail-content">
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
              <label>故障编码</label>
              <span class="fault-code">{{ fault.fault_code }}</span>
            </div>
            <div class="info-item">
              <label>故障标题</label>
              <span>{{ fault.title }}</span>
            </div>
            <div class="info-item">
              <label>故障类型</label>
              <span>{{ fault.fault_type }}</span>
            </div>
            <div class="info-item">
              <label>严重程度</label>
              <span>{{ fault.severity }}</span>
            </div>
            <div class="info-item">
              <label>优先级</label>
              <span :class="`priority-tag priority-${getPriorityClass(fault.priority)}`">
                {{ fault.priority }}
              </span>
            </div>
            <div class="info-item">
              <label>当前状态</label>
              <span :class="`status-tag status-${getFaultStatusClass(fault.status)}`">
                {{ fault.status }}
              </span>
            </div>
            <div class="info-item">
              <label>报告人</label>
              <span>{{ fault.reporter_name }}</span>
            </div>
            <div class="info-item">
              <label>报告时间</label>
              <span>{{ formatDate(fault.report_time) }}</span>
            </div>
            <div class="info-item">
              <label>指派人</label>
              <span>{{ fault.assignee_name || '未指派' }}</span>
            </div>
            <div class="info-item">
              <label>指派时间</label>
              <span>{{ fault.assign_time ? formatDate(fault.assign_time) : '-' }}</span>
            </div>
            <div class="info-item">
              <label>响应时间</label>
              <span>{{ fault.response_time ? formatDate(fault.response_time) : '-' }}</span>
            </div>
            <div class="info-item">
              <label>SLA违约</label>
              <span :class="fault.sla_breach ? 'text-danger' : 'text-success'">
                {{ fault.sla_breach ? '是' : '否' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 故障描述 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📝 故障描述</h2>
        </div>
        <div class="card-body">
          <div class="description-content">
            <p>{{ fault.description || '暂无描述' }}</p>
          </div>
        </div>
      </div>

      <!-- 影响资产 -->
      <div class="info-card">
        <div class="card-header">
          <h2>💻 影响资产</h2>
          <div class="card-actions">
            <button @click="addAffectedAsset" class="btn-sm btn-primary">添加资产</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="fault.affected_assets && fault.affected_assets.length > 0" class="asset-list">
            <div v-for="asset in fault.affected_assets" :key="asset.id" class="asset-item">
              <div class="asset-info">
                <div class="asset-name">{{ asset.name }}</div>
                <div class="asset-code">{{ asset.asset_code }}</div>
              </div>
              <div class="asset-actions">
                <button @click="viewAsset(asset)" class="btn-sm btn-info">查看</button>
                <button @click="removeAffectedAsset(asset)" class="btn-sm btn-danger">移除</button>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无影响资产</p>
          </div>
        </div>
      </div>

      <!-- 处理进度 -->
      <div class="info-card">
        <div class="card-header">
          <h2>⏱️ 处理进度</h2>
          <div class="card-actions">
            <button v-if="canAddProgress" @click="addProgress" class="btn-sm btn-primary">添加进度</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="progressRecords.length > 0" class="progress-timeline">
            <div v-for="record in progressRecords" :key="record.id" class="timeline-item">
              <div class="timeline-dot" :class="`dot-${getProgressTypeClass(record.action_type)}`"></div>
              <div class="timeline-content">
                <div class="progress-header">
                  <span class="progress-action">{{ getProgressActionName(record.action_type) }}</span>
                  <span class="progress-date">{{ formatDate(record.created_at) }}</span>
                </div>
                <div class="progress-details">
                  <p>{{ record.description }}</p>
                  <div v-if="record.time_spent" class="time-spent">
                    耗时: {{ record.time_spent }}分钟
                  </div>
                </div>
                <div class="progress-user">
                  <span>操作人: {{ record.operator_name }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无处理记录</p>
          </div>
        </div>
      </div>

      <!-- 解决方案 -->
      <div class="info-card">
        <div class="card-header">
          <h2>💡 解决方案</h2>
          <div class="card-actions">
            <button v-if="canEditSolution" @click="editSolution" class="btn-sm btn-primary">编辑方案</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="fault.solution" class="solution-content">
            <div class="solution-text">
              <p>{{ fault.solution }}</p>
            </div>
            <div v-if="fault.solution_time" class="solution-meta">
              <span>解决时间: {{ formatDate(fault.solution_time) }}</span>
              <span>解决人: {{ fault.solver_name }}</span>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无解决方案</p>
            <button v-if="canEditSolution" @click="addSolution" class="btn btn-primary">添加方案</button>
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

      <!-- 操作日志 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📜 操作日志</h2>
        </div>
        <div class="card-body">
          <div v-if="operationLogs.length > 0" class="log-timeline">
            <div v-for="log in operationLogs" :key="log.id" class="timeline-item">
              <div class="timeline-dot" :class="`dot-${getLogTypeClass(log.operation_type)}`"></div>
              <div class="timeline-content">
                <div class="log-header">
                  <span class="log-action">{{ getLogActionName(log.operation_type) }}</span>
                  <span class="log-date">{{ formatDate(log.created_at) }}</span>
                </div>
                <div class="log-details">
                  <p>{{ log.description }}</p>
                </div>
                <div class="log-user">
                  <span>操作人: {{ log.operator_name }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无操作记录</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="!loading" class="error-state">
      <div class="error-icon">❌</div>
      <p>故障信息加载失败</p>
      <button @click="refreshData" class="btn btn-primary">重新加载</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { faultApi } from '@/api/fault'
import type { Fault } from '@/types/common'
import { getFaultStatusClass, getPriorityClass } from '@/types/common'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const fault = ref<Fault | null>(null)
const progressRecords = ref<any[]>([])
const attachments = ref<any[]>([])
const operationLogs = ref<any[]>([])

// 计算属性
const faultId = computed(() => route.params.id ? Number(route.params.id) : null)

const canEdit = computed(() => {
  if (!fault.value) return false
  return ['新建', '处理中'].includes(fault.value.status)
})

const canProcess = computed(() => {
  if (!fault.value) return false
  return fault.value.status === '新建'
})

const canClose = computed(() => {
  if (!fault.value) return false
  return fault.value.status === '已解决'
})

const canAddProgress = computed(() => {
  if (!fault.value) return false
  return ['新建', '处理中'].includes(fault.value.status)
})

const canEditSolution = computed(() => {
  if (!fault.value) return false
  return ['处理中', '已解决'].includes(fault.value.status)
})

// 数据加载
const loadFaultDetail = async () => {
  if (!faultId.value) return
  
  loading.value = true
  try {
    // 加载故障基本信息
    const response = await faultApi.getFault(faultId.value)
    if (response.success) {
      fault.value = response.data
    }
    
    // 并行加载关联数据
    await Promise.all([
      loadProgressRecords(),
      loadAttachments(),
      loadOperationLogs()
    ])
    
  } catch (error) {
    console.error('加载故障详情失败:', error)
  } finally {
    loading.value = false
  }
}

const loadProgressRecords = async () => {
  try {
    // 模拟数据
    progressRecords.value = [
      {
        id: 1,
        action_type: 'create',
        description: '故障已创建，等待处理',
        operator_name: '张三',
        created_at: '2024-01-15 09:30:00',
        time_spent: null
      },
      {
        id: 2,
        action_type: 'assign',
        description: '故障已指派给李四',
        operator_name: '张三',
        created_at: '2024-01-15 10:00:00',
        time_spent: null
      },
      {
        id: 3,
        action_type: 'progress',
        description: '开始排查问题，初步判断为硬件故障',
        operator_name: '李四',
        created_at: '2024-01-15 10:30:00',
        time_spent: 30
      }
    ]
  } catch (error) {
    console.error('加载处理记录失败:', error)
  }
}

const loadAttachments = async () => {
  try {
    // 模拟数据
    attachments.value = [
      {
        id: 1,
        original_name: '故障截图.png',
        file_type: 'image/png',
        file_size: 1024576,
        file_url: '/api/files/download/1',
        uploader_name: '张三',
        created_at: '2024-01-15 09:30:00'
      }
    ]
  } catch (error) {
    console.error('加载附件失败:', error)
  }
}

const loadOperationLogs = async () => {
  try {
    // 模拟数据
    operationLogs.value = [
      {
        id: 1,
        operation_type: 'create',
        description: '创建故障记录',
        operator_name: '张三',
        created_at: '2024-01-15 09:30:00'
      },
      {
        id: 2,
        operation_type: 'assign',
        description: '指派给李四处理',
        operator_name: '张三',
        created_at: '2024-01-15 10:00:00'
      }
    ]
  } catch (error) {
    console.error('加载操作日志失败:', error)
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

const getProgressTypeClass = (type: string): string => {
  const classes = {
    create: 'info',
    assign: 'warning',
    progress: 'primary',
    resolve: 'success',
    close: 'secondary'
  }
  return classes[type as keyof typeof classes] || 'info'
}

const getProgressActionName = (type: string): string => {
  const names = {
    create: '创建',
    assign: '指派',
    progress: '处理',
    resolve: '解决',
    close: '关闭'
  }
  return names[type as keyof typeof names] || type
}

const getLogTypeClass = (type: string): string => {
  return getProgressTypeClass(type)
}

const getLogActionName = (type: string): string => {
  return getProgressActionName(type)
}

// 事件处理
const goBack = () => {
  router.push('/app/faults')
}

const refreshData = () => {
  loadFaultDetail()
}

const printFault = () => {
  window.print()
}

const editFault = () => {
  router.push(`/app/faults/edit/${faultId.value}`)
}

const processFault = () => {
  console.log('开始处理故障')
  // TODO: 实现处理故障
}

const closeFault = () => {
  console.log('关闭故障')
  // TODO: 实现关闭故障
}

const editBasicInfo = () => {
  console.log('编辑基本信息')
  // TODO: 实现编辑基本信息
}

const addAffectedAsset = () => {
  console.log('添加影响资产')
  // TODO: 实现添加影响资产
}

const viewAsset = (asset: any) => {
  router.push(`/app/assets/detail/${asset.id}`)
}

const removeAffectedAsset = (asset: any) => {
  console.log('移除影响资产', asset)
  // TODO: 实现移除影响资产
}

const addProgress = () => {
  console.log('添加进度')
  // TODO: 实现添加进度
}

const editSolution = () => {
  console.log('编辑解决方案')
  // TODO: 实现编辑解决方案
}

const addSolution = () => {
  console.log('添加解决方案')
  // TODO: 实现添加解决方案
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
  loadFaultDetail()
})
</script>

<style scoped>
.fault-detail-container {
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

.fault-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.fault-code {
  font-family: monospace;
  color: #409eff;
  font-weight: 600;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
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

.status-tag {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  width: fit-content;
}

.status-info { background: #e1f3ff; color: #409eff; }
.status-warning { background: #fdf6ec; color: #e6a23c; }
.status-success { background: #f0f9ff; color: #67c23a; }
.status-secondary { background: #f4f4f5; color: #909399; }

.priority-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.priority-low { background: #f4f4f5; color: #909399; }
.priority-medium { background: #e1f3ff; color: #409eff; }
.priority-high { background: #fdf6ec; color: #e6a23c; }
.priority-urgent { background: #fef0f0; color: #f56c6c; }

.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }

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
}

.asset-actions {
  display: flex;
  gap: 8px;
}

.progress-timeline,
.log-timeline {
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

.dot-info { background: #409eff; }
.dot-warning { background: #e6a23c; }
.dot-primary { background: #409eff; }
.dot-success { background: #67c23a; }
.dot-secondary { background: #909399; }

.timeline-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.progress-header,
.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-action,
.log-action {
  font-weight: 500;
  color: #303133;
}

.progress-date,
.log-date {
  font-size: 12px;
  color: #909399;
}

.progress-details p,
.log-details p {
  margin: 0 0 8px 0;
  color: #606266;
}

.time-spent {
  font-size: 12px;
  color: #909399;
  background: #e1f3ff;
  padding: 2px 6px;
  border-radius: 3px;
  display: inline-block;
}

.progress-user,
.log-user {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.solution-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #67c23a;
}

.solution-text p {
  margin: 0 0 12px 0;
  color: #303133;
  line-height: 1.6;
}

.solution-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

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
  .fault-detail-container {
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
    flex-wrap: wrap;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .asset-item {
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

/* 打印样式 */
@media print {
  .page-header .header-actions,
  .card-actions,
  .asset-actions,
  .file-actions {
    display: none;
  }
  
  .fault-detail-container {
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