<template>
  <div class="asset-detail-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="btn btn-secondary">← 返回</button>
        <div class="title-info">
          <h1>{{ asset?.name || '资产详情' }}</h1>
          <div class="asset-meta">
            <span class="asset-code">{{ asset?.asset_code }}</span>
            <span :class="`status-tag status-${getStatusClass(asset?.status || '')}`">
              {{ asset?.status }}
            </span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button @click="refreshData" :disabled="loading" class="btn btn-secondary">🔄 刷新</button>
        <button @click="printAsset" class="btn btn-secondary">🖨️ 打印</button>
        <button @click="editAsset" class="btn btn-primary">✏️ 编辑</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner">🔄</div>
      <p>加载中...</p>
    </div>

    <div v-else-if="asset" class="detail-content">
      <!-- 基本信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📋 基本信息</h2>
          <div class="card-actions">
            <button @click="editBasicInfo" class="btn-sm btn-primary">编辑</button>
          </div>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label>资产名称</label>
              <span>{{ asset.name }}</span>
            </div>
            <div class="info-item">
              <label>资产编码</label>
              <span class="asset-code">{{ asset.asset_code }}</span>
            </div>
            <div class="info-item">
              <label>资产类别</label>
              <span>{{ asset.category }}</span>
            </div>
            <div class="info-item">
              <label>品牌型号</label>
              <span>{{ asset.brand }} {{ asset.model }}</span>
            </div>
            <div class="info-item">
              <label>序列号</label>
              <span>{{ asset.serial_number || '-' }}</span>
            </div>
            <div class="info-item">
              <label>当前状态</label>
              <span :class="`status-tag status-${getStatusClass(asset.status)}`">
                {{ asset.status }}
              </span>
            </div>
            <div class="info-item">
              <label>责任人</label>
              <span>{{ asset.manager || '-' }}</span>
            </div>
            <div class="info-item">
              <label>所在位置</label>
              <span>{{ asset.location || '-' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 采购信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <h2>💰 采购信息</h2>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label>采购日期</label>
              <span>{{ asset.purchase_date || '-' }}</span>
            </div>
            <div class="info-item">
              <label>采购价格</label>
              <span v-if="asset.price">¥{{ asset.price.toLocaleString() }}</span>
              <span v-else>-</span>
            </div>
            <div class="info-item">
              <label>保修开始</label>
              <span>{{ asset.warranty_start_date || '-' }}</span>
            </div>
            <div class="info-item">
              <label>保修到期</label>
              <span>{{ asset.warranty_date || '-' }}</span>
            </div>
            <div class="info-item">
              <label>保修状态</label>
              <span v-if="asset.warranty_status" :class="`warranty-tag warranty-${getWarrantyClass(asset.warranty_status)}`">
                {{ asset.warranty_status }}
              </span>
              <span v-else>-</span>
            </div>
            <div class="info-item">
              <label>剩余保修</label>
              <span v-if="asset.warranty_days_left !== undefined">
                {{ asset.warranty_days_left }}天
              </span>
              <span v-else>-</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 技术规格卡片 -->
      <div class="info-card">
        <div class="card-header">
          <h2>⚙️ 技术规格</h2>
          <div class="card-actions">
            <button @click="editSpecs" class="btn-sm btn-primary">编辑</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="asset.specifications && asset.specifications.length > 0" class="specs-list">
            <div v-for="spec in asset.specifications" :key="spec.name" class="spec-item">
              <label>{{ spec.name }}</label>
              <span>{{ spec.value }}</span>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无技术规格信息</p>
            <button @click="addSpecs" class="btn btn-primary">添加规格</button>
          </div>
        </div>
      </div>

      <!-- 端口管理卡片（仅网络设备显示） -->
      <div v-if="isNetworkDevice" class="info-card">
        <div class="card-header">
          <h2>🔌 端口管理</h2>
          <div class="card-actions">
            <button @click="refreshPorts" :disabled="loadingPorts" class="btn-sm btn-secondary">🔄 刷新</button>
          </div>
        </div>
        <div class="card-body">
          <PortManager 
            v-if="asset" 
            :asset="asset" 
            @port-updated="onPortUpdated"
          />
        </div>
      </div>

      <!-- 使用记录卡片 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📊 使用统计</h2>
        </div>
        <div class="card-body">
          <div class="usage-stats">
            <div class="stat-item">
              <div class="stat-value">{{ asset.usage_days || 0 }}</div>
              <div class="stat-label">使用天数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ maintenanceCount }}</div>
              <div class="stat-label">维护次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ faultCount }}</div>
              <div class="stat-label">故障次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ transferCount }}</div>
              <div class="stat-label">转移次数</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 关联故障 -->
      <div class="info-card">
        <div class="card-header">
          <h2>🚨 关联故障</h2>
          <div class="card-actions">
            <button @click="createFault" class="btn-sm btn-primary">报告故障</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="relatedFaults.length > 0" class="fault-list">
            <div v-for="fault in relatedFaults" :key="fault.id" class="fault-item">
              <div class="fault-info">
                <div class="fault-title">
                  <span class="fault-code">{{ fault.fault_code }}</span>
                  <span class="fault-name">{{ fault.title }}</span>
                </div>
                <div class="fault-meta">
                  <span class="fault-type">{{ fault.fault_type }}</span>
                  <span :class="`priority-tag priority-${getPriorityClass(fault.priority)}`">
                    {{ fault.priority }}
                  </span>
                  <span :class="`status-tag status-${getFaultStatusClass(fault.status)}`">
                    {{ fault.status }}
                  </span>
                  <span class="fault-date">{{ formatDate(fault.created_at) }}</span>
                </div>
              </div>
              <div class="fault-actions">
                <button @click="viewFault(fault)" class="btn-sm btn-info">查看</button>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无关联故障</p>
          </div>
        </div>
      </div>

      <!-- 维护记录 -->
      <div class="info-card">
        <div class="card-header">
          <h2>🔧 维护记录</h2>
          <div class="card-actions">
            <button @click="createMaintenance" class="btn-sm btn-primary">创建维护</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="maintenanceRecords.length > 0" class="maintenance-list">
            <div v-for="record in maintenanceRecords" :key="record.id" class="maintenance-item">
              <div class="maintenance-info">
                <div class="maintenance-title">
                  <span class="maintenance-code">{{ record.record_code }}</span>
                  <span class="maintenance-name">{{ record.title }}</span>
                </div>
                <div class="maintenance-meta">
                  <span class="maintenance-type">{{ record.record_type }}</span>
                  <span :class="`status-tag status-${getMaintenanceStatusClass(record.status)}`">
                    {{ record.status }}
                  </span>
                  <span class="maintenance-date">{{ formatDate(record.start_time) }}</span>
                </div>
              </div>
              <div class="maintenance-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: record.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ record.progress }}%</span>
              </div>
              <div class="maintenance-actions">
                <button @click="viewMaintenance(record)" class="btn-sm btn-info">查看</button>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无维护记录</p>
          </div>
        </div>
      </div>

      <!-- 变更历史 -->
      <div class="info-card">
        <div class="card-header">
          <h2>📜 变更历史</h2>
        </div>
        <div class="card-body">
          <div v-if="changeHistory.length > 0" class="history-timeline">
            <div v-for="change in changeHistory" :key="change.id" class="timeline-item">
              <div class="timeline-dot" :class="`dot-${getChangeTypeClass(change.change_type)}`"></div>
              <div class="timeline-content">
                <div class="change-header">
                  <span class="change-type">{{ getChangeTypeName(change.change_type) }}</span>
                  <span class="change-date">{{ formatDate(change.created_at) }}</span>
                </div>
                <div class="change-details">
                  <p>{{ change.description }}</p>
                  <div v-if="change.changes && change.changes.length > 0" class="change-fields">
                    <div v-for="field in change.changes" :key="field.field" class="field-change">
                      <strong>{{ field.field_name }}:</strong>
                      <span class="old-value">{{ field.old_value || '无' }}</span>
                      →
                      <span class="new-value">{{ field.new_value || '无' }}</span>
                    </div>
                  </div>
                </div>
                <div class="change-user">
                  <span>操作人: {{ change.operator_name }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>暂无变更记录</p>
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
                </div>
              </div>
              <div class="file-actions">
                <button @click="downloadFile(file)" class="btn-sm btn-info">下载</button>
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
      <p>资产信息加载失败</p>
      <button @click="refreshData" class="btn btn-primary">重新加载</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { assetApi } from '@/api/asset'
import type { Asset, AssetSpecification } from '@/types/common'
import { getStatusClass, getWarrantyStatusClass, getFaultStatusClass, getPriorityClass, getMaintenanceStatusClass } from '@/types/common'
import PortManager from '@/components/assets/PortManager.vue'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const loadingPorts = ref(false)
const asset = ref<Asset | null>(null)
const relatedFaults = ref<any[]>([])
const maintenanceRecords = ref<any[]>([])
const changeHistory = ref<any[]>([])
const attachments = ref<any[]>([])

// 计算属性
const assetId = computed(() => route.params.id ? Number(route.params.id) : null)

const maintenanceCount = computed(() => maintenanceRecords.value.length)
const faultCount = computed(() => relatedFaults.value.length)
const transferCount = computed(() => 
  changeHistory.value.filter(h => h.change_type === 'transfer').length
)

// 判断是否为网络设备
const isNetworkDevice = computed(() => {
  if (!asset.value) return false
  // 根据资产类别判断是否为网络设备
  const networkCategories = ['交换机', '路由器', '防火墙', '服务器', '工作站', '台式机', '笔记本', '网络设备']
  return networkCategories.includes(asset.value.category || '')
})

// 数据加载
const loadAssetDetail = async () => {
  if (!assetId.value) return
  
  loading.value = true
  try {
    // 加载资产基本信息
    const response = await assetApi.getAsset(assetId.value)
    if (response.success) {
      asset.value = response.data
    }
    
    // 并行加载关联数据
    await Promise.all([
      loadRelatedFaults(),
      loadMaintenanceRecords(),
      loadChangeHistory(),
      loadAttachments()
    ])
    
  } catch (error) {
    console.error('加载资产详情失败:', error)
  } finally {
    loading.value = false
  }
}

const loadRelatedFaults = async () => {
  try {
    // 模拟数据
    relatedFaults.value = [
      {
        id: 1,
        fault_code: 'FLT20240001',
        title: '设备无法正常启动',
        fault_type: '硬件故障',
        priority: '高',
        status: '已解决',
        created_at: '2024-01-15 09:30:00'
      }
    ]
  } catch (error) {
    console.error('加载关联故障失败:', error)
  }
}

const loadMaintenanceRecords = async () => {
  try {
    // 模拟数据
    maintenanceRecords.value = [
      {
        id: 1,
        record_code: 'MNT20240001',
        title: '定期保养维护',
        record_type: '预防性维护',
        status: '已完成',
        progress: 100,
        start_time: '2024-01-10 14:00:00'
      }
    ]
  } catch (error) {
    console.error('加载维护记录失败:', error)
  }
}

const loadChangeHistory = async () => {
  try {
    // 模拟数据
    changeHistory.value = [
      {
        id: 1,
        change_type: 'create',
        description: '创建资产记录',
        operator_name: '张三',
        created_at: '2024-01-01 10:00:00',
        changes: []
      },
      {
        id: 2,
        change_type: 'update',
        description: '更新资产信息',
        operator_name: '李四',
        created_at: '2024-01-05 14:30:00',
        changes: [
          {
            field: 'location',
            field_name: '位置',
            old_value: '机房A-机柜01',
            new_value: '机房A-机柜02'
          }
        ]
      }
    ]
  } catch (error) {
    console.error('加载变更历史失败:', error)
  }
}

const loadAttachments = async () => {
  try {
    // 模拟数据
    attachments.value = [
      {
        id: 1,
        original_name: '设备说明书.pdf',
        file_type: 'application/pdf',
        file_size: 2048576,
        file_url: '/api/files/download/1',
        created_at: '2024-01-01 10:00:00'
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

const getChangeTypeClass = (type: string): string => {
  const classes = {
    create: 'success',
    update: 'info',
    transfer: 'warning',
    delete: 'danger'
  }
  return classes[type as keyof typeof classes] || 'info'
}

const getChangeTypeName = (type: string): string => {
  const names = {
    create: '创建',
    update: '更新',
    transfer: '转移',
    delete: '删除'
  }
  return names[type as keyof typeof names] || type
}

const getWarrantyClass = (status: string): string => {
  return getWarrantyStatusClass(status)
}

// 事件处理
const goBack = () => {
  router.push('/app/assets')
}

const refreshData = () => {
  loadAssetDetail()
}

const printAsset = () => {
  window.print()
}

const editAsset = () => {
  router.push(`/app/assets/edit/${assetId.value}`)
}

const editBasicInfo = () => {
  console.log('编辑基本信息')
  // TODO: 实现编辑基本信息
}

const editSpecs = () => {
  console.log('编辑技术规格')
  // TODO: 实现编辑技术规格
}

const addSpecs = () => {
  console.log('添加技术规格')
  // TODO: 实现添加技术规格
}

const createFault = () => {
  router.push(`/app/faults/create?asset_id=${assetId.value}`)
}

const viewFault = (fault: any) => {
  router.push(`/app/faults/detail/${fault.id}`)
}

const createMaintenance = () => {
  router.push(`/app/maintenance/create?asset_id=${assetId.value}`)
}

const viewMaintenance = (record: any) => {
  router.push(`/app/maintenance/detail/${record.id}`)
}

const uploadAttachment = () => {
  console.log('上传附件')
  // TODO: 实现上传附件
}

const downloadFile = (file: any) => {
  window.open(file.file_url, '_blank')
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

// 端口管理相关方法
const refreshPorts = () => {
  console.log('刷新端口信息')
  // 端口组件内部会处理刷新逻辑
}

const onPortUpdated = () => {
  console.log('端口信息已更新')
  // 可以在这里执行其他逻辑，比如刷新资产信息
}

// 初始化
onMounted(() => {
  loadAssetDetail()
})
</script>

<style scoped>
.asset-detail-container {
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

.asset-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.asset-code {
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

.status-success { background: #f0f9ff; color: #67c23a; }
.status-info { background: #e1f3ff; color: #409eff; }
.status-warning { background: #fdf6ec; color: #e6a23c; }
.status-danger { background: #fef0f0; color: #f56c6c; }

.warranty-tag {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  width: fit-content;
}

.warranty-success { background: #f0f9ff; color: #67c23a; }
.warranty-warning { background: #fdf6ec; color: #e6a23c; }
.warranty-danger { background: #fef0f0; color: #f56c6c; }

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

.specs-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.spec-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.spec-item label {
  font-weight: 500;
  color: #606266;
  font-size: 12px;
}

.spec-item span {
  color: #303133;
  font-size: 14px;
}

.usage-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
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

.fault-list,
.maintenance-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.fault-item,
.maintenance-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.fault-info,
.maintenance-info {
  flex: 1;
}

.fault-title,
.maintenance-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.fault-code,
.maintenance-code {
  font-family: monospace;
  color: #409eff;
  font-weight: 600;
  font-size: 12px;
}

.fault-name,
.maintenance-name {
  font-weight: 500;
  color: #303133;
}

.fault-meta,
.maintenance-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.fault-type,
.maintenance-type {
  background: #e1f3ff;
  color: #409eff;
  padding: 2px 6px;
  border-radius: 3px;
}

.maintenance-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px;
  min-width: 120px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #f0f2f5;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #67c23a;
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
}

.fault-actions,
.maintenance-actions {
  display: flex;
  gap: 8px;
}

.history-timeline {
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
.dot-info { background: #409eff; }
.dot-warning { background: #e6a23c; }
.dot-danger { background: #f56c6c; }

.timeline-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.change-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.change-type {
  font-weight: 500;
  color: #303133;
}

.change-date {
  font-size: 12px;
  color: #909399;
}

.change-details p {
  margin: 0 0 8px 0;
  color: #606266;
}

.change-fields {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-change {
  font-size: 12px;
  color: #606266;
}

.old-value {
  color: #f56c6c;
  text-decoration: line-through;
}

.new-value {
  color: #67c23a;
  font-weight: 500;
}

.change-user {
  margin-top: 8px;
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
  .asset-detail-container {
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
  
  .usage-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .fault-item,
  .maintenance-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .maintenance-progress {
    margin: 0;
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
  .usage-stats {
    grid-template-columns: 1fr;
  }
  
  .asset-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

/* 打印样式 */
@media print {
  .page-header .header-actions,
  .card-actions,
  .fault-actions,
  .maintenance-actions,
  .file-actions {
    display: none;
  }
  
  .asset-detail-container {
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