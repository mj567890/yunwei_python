<template>
  <div class="maintenance-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>运维记录管理</h1>
      <div class="header-actions">
        <button @click="refreshRecords" class="btn btn-secondary">🔄 刷新</button>
        <button @click="createRecord" class="btn btn-primary">➕ 新增记录</button>
        <button @click="exportRecords" class="btn btn-info">📊 导出</button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>关键词</label>
          <input v-model="searchParams.keyword" placeholder="搜索标题或内容" />
        </div>
        <div class="form-group">
          <label>记录类型</label>
          <select v-model="searchParams.record_type">
            <option value="">全部类型</option>
            <option value="日常巡检">日常巡检</option>
            <option value="设备维护">设备维护</option>
            <option value="故障处理">故障处理</option>
            <option value="系统升级">系统升级</option>
            <option value="其他">其他</option>
          </select>
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="searchParams.status">
            <option value="">全部状态</option>
            <option value="计划中">计划中</option>
            <option value="进行中">进行中</option>
            <option value="已完成">已完成</option>
            <option value="已取消">已取消</option>
          </select>
        </div>
        <div class="form-group">
          <label>时间范围</label>
          <input v-model="searchParams.date_start" type="date" />
          <span class="date-separator">至</span>
          <input v-model="searchParams.date_end" type="date" />
        </div>
        <div class="form-group">
          <button @click="searchRecords" class="btn btn-primary">🔍 搜索</button>
          <button @click="resetSearch" class="btn btn-secondary">🔄 重置</button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stats-card">
        <div class="stats-icon">📋</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.total }}</div>
          <div class="stats-label">总记录数</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">🔄</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.inProgress }}</div>
          <div class="stats-label">进行中</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">✅</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.completed }}</div>
          <div class="stats-label">已完成</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">⏱️</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.avgTime }}h</div>
          <div class="stats-label">平均耗时</div>
        </div>
      </div>
    </div>

    <!-- 记录列表 -->
    <div class="table-container">
      <div v-if="loading" class="loading">
        <div class="loading-spinner">🔄</div>
        <p>加载中...</p>
      </div>
      
      <table v-else class="maintenance-table">
        <thead>
          <tr>
            <th width="60">序号</th>
            <th>记录编号</th>
            <th>标题</th>
            <th>类型</th>
            <th>负责人</th>
            <th>开始时间</th>
            <th>状态</th>
            <th>优先级</th>
            <th>进度</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(record, index) in recordList" :key="record.id">
            <td class="row-number">{{ (pagination.page - 1) * pagination.pageSize + index + 1 }}</td>
            <td class="record-code">{{ record.record_code }}</td>
            <td class="record-title">
              <div class="title-content">
                <span class="title">{{ record.title }}</span>
                <div class="meta">
                  <span class="category">{{ record.category }}</span>
                  <span v-if="record.asset_count" class="asset-count">{{ record.asset_count }}个资产</span>
                </div>
              </div>
            </td>
            <td>
              <span class="type-tag">{{ record.record_type }}</span>
            </td>
            <td>
              <div class="user-info">
                <span class="name">{{ record.responsible_person }}</span>
                <span class="dept">{{ record.department }}</span>
              </div>
            </td>
            <td>{{ formatDate(record.start_time) }}</td>
            <td>
              <span :class="`status-tag status-${getStatusClass(record.status)}`">
                {{ record.status }}
              </span>
            </td>
            <td>
              <span :class="`priority-tag priority-${getPriorityClass(record.priority)}`">
                {{ record.priority }}
              </span>
            </td>
            <td>
              <div class="progress-container">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: record.progress + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ record.progress }}%</span>
              </div>
            </td>
            <td class="actions">
              <button @click="viewRecord(record)" class="btn-sm btn-info">查看</button>
              <button @click="editRecord(record)" class="btn-sm btn-primary">编辑</button>
              <button @click="updateProgress(record)" class="btn-sm btn-warning">进度</button>
              <button @click="deleteRecord(record)" class="btn-sm btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 空状态 -->
      <div v-if="!loading && recordList.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>暂无运维记录</p>
        <button @click="createRecord" class="btn btn-primary">创建第一个记录</button>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total > 0" class="pagination">
      <div class="pagination-left">
        <span class="page-size-label">每页显示</span>
        <select v-model="pagination.pageSize" @change="changePageSize" class="page-size-select">
          <option value="10">10条</option>
          <option value="20">20条</option>
          <option value="50">50条</option>
          <option value="100">100条</option>
        </select>
      </div>
      <div class="pagination-center">
        <button 
          @click="changePage(pagination.page - 1)" 
          :disabled="pagination.page <= 1"
          class="btn btn-secondary"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ pagination.page }} / {{ Math.ceil(pagination.total / pagination.pageSize) }} 页
          (共 {{ pagination.total }} 条)
        </span>
        <button 
          @click="changePage(pagination.page + 1)" 
          :disabled="pagination.page >= Math.ceil(pagination.total / pagination.pageSize)"
          class="btn btn-secondary"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { MaintenanceRecord, MaintenanceSearchParams, PaginationInfo } from '@/types/common'
import { getMaintenanceStatusClass, getPriorityClass as getCommonPriorityClass } from '@/types/common'

const router = useRouter()

// 状态管理
const loading = ref(false)
const recordList = ref<MaintenanceRecord[]>([])
const searchParams = reactive<MaintenanceSearchParams>({
  keyword: '',
  record_type: '',
  status: '',
  date_start: '',
  date_end: '',
  page: 1,
  pageSize: 20
})

const pagination = reactive<PaginationInfo>({
  total: 0,
  page: 1,
  pageSize: 20
})

const stats = reactive({
  total: 156,
  inProgress: 23,
  completed: 128,
  avgTime: 2.5
})

// 模拟数据
const mockData: MaintenanceRecord[] = [
  {
    id: 1,
    record_code: 'MNT20240001',
    title: '服务器机房日常巡检',
    record_type: '日常巡检',
    category: '硬件检查',
    responsible_person: '张三',
    department: 'IT部',
    start_time: '2024-01-15 09:00:00',
    status: '已完成',
    priority: '中',
    progress: 100,
    asset_count: 12,
    created_at: '2024-01-15 09:00:00'
  },
  {
    id: 2,
    record_code: 'MNT20240002',
    title: '核心交换机维护升级',
    record_type: '设备维护',
    category: '网络设备',
    responsible_person: '李四',
    department: '网络部',
    start_time: '2024-01-16 14:00:00',
    status: '进行中',
    priority: '高',
    progress: 65,
    asset_count: 3,
    created_at: '2024-01-16 14:00:00'
  },
  {
    id: 3,
    record_code: 'MNT20240003',
    title: '数据库服务器故障处理',
    record_type: '故障处理',
    category: '软件问题',
    responsible_person: '王五',
    department: 'DBA',
    start_time: '2024-01-17 10:30:00',
    status: '计划中',
    priority: '紧急',
    progress: 0,
    asset_count: 1,
    created_at: '2024-01-17 10:30:00'
  }
]

// 数据加载
const loadRecords = async () => {
  loading.value = true
  try {
    // 这里应该调用真实的API
    await new Promise(resolve => setTimeout(resolve, 500)) // 模拟请求延迟
    
    recordList.value = mockData
    pagination.total = mockData.length
    pagination.page = searchParams.page
  } catch (error) {
    console.error('加载运维记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 工具函数
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusClass = (status: string) => {
  return getMaintenanceStatusClass(status)
}

const getPriorityClass = (priority: string) => {
  return getCommonPriorityClass(priority)
}

// 事件处理
const searchRecords = () => {
  searchParams.page = 1
  loadRecords()
}

const resetSearch = () => {
  Object.assign(searchParams, {
    keyword: '',
    record_type: '',
    status: '',
    date_start: '',
    date_end: '',
    page: 1,
    pageSize: 20
  })
  loadRecords()
}

const refreshRecords = () => loadRecords()

const changePage = (page: number) => {
  searchParams.page = page
  loadRecords()
}

// 改变每页条数
const changePageSize = () => {
  searchParams.pageSize = pagination.pageSize
  searchParams.page = 1  // 重置到第一页
  pagination.page = 1
  loadRecords()
}

const createRecord = () => {
  router.push('/app/maintenance/create')
}

const viewRecord = (record: any) => {
  router.push(`/app/maintenance/detail/${record.id}`)
}

const editRecord = (record: any) => {
  router.push(`/app/maintenance/edit/${record.id}`)
}

const updateProgress = (record: any) => {
  console.log('更新进度:', record)
  // TODO: 打开进度更新对话框
}

const deleteRecord = async (record: any) => {
  if (confirm(`确认删除运维记录 "${record.title}" 吗？`)) {
    try {
      // 这里应该调用删除API
      await loadRecords()
      console.log('删除成功')
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

const exportRecords = () => {
  console.log('导出运维记录')
  // TODO: 实现导出功能
}

// 初始化
onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.maintenance-container {
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
  font-size: 24px;
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
  flex-wrap: wrap;
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
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #409eff;
}

.date-separator {
  margin: 0 8px;
  color: #909399;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stats-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  font-size: 32px;
  opacity: 0.8;
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.loading-spinner {
  font-size: 24px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.maintenance-table {
  width: 100%;
  border-collapse: collapse;
}

.maintenance-table th {
  background: #f8f9fa;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
}

.maintenance-table td {
  padding: 16px 12px;
  border-bottom: 1px solid #ebeef5;
  vertical-align: middle;
}

.record-code {
  font-family: monospace;
  color: #409eff;
  font-weight: 500;
}

.title-content .title {
  display: block;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.title-content .meta {
  font-size: 12px;
  color: #909399;
}

.title-content .category {
  margin-right: 8px;
}

.asset-count {
  color: #67c23a;
}

.type-tag {
  background: #e1f3ff;
  color: #409eff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.user-info .name {
  display: block;
  font-weight: 500;
  color: #303133;
}

.user-info .dept {
  font-size: 12px;
  color: #909399;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-info { background: #e1f3ff; color: #409eff; }
.status-warning { background: #fdf6ec; color: #e6a23c; }
.status-success { background: #f0f9ff; color: #67c23a; }
.status-danger { background: #fef0f0; color: #f56c6c; }

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

.progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
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
  background: #409eff;
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 32px;
}

.actions {
  white-space: nowrap;
}

.btn, .btn-sm {
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

.btn {
  padding: 10px 16px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  margin-right: 6px;
}

.btn-primary { background: #409eff; color: white; }
.btn-primary:hover { background: #66b1ff; }

.btn-secondary { background: #909399; color: white; }
.btn-secondary:hover { background: #a6a9ad; }

.btn-info { background: #909399; color: white; }
.btn-info:hover { background: #a6a9ad; }

.btn-warning { background: #e6a23c; color: white; }
.btn-warning:hover { background: #ebb563; }

.btn-danger { background: #f56c6c; color: white; }
.btn-danger:hover { background: #f78989; }

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-info {
  color: #606266;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .maintenance-container {
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
  
  .search-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .maintenance-table {
    font-size: 12px;
  }
  
  .maintenance-table th,
  .maintenance-table td {
    padding: 8px 6px;
  }
}

.row-number {
  text-align: center;
  font-weight: 500;
  color: #909399;
  font-size: 13px;
  width: 60px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size-label {
  color: #606266;
  font-size: 14px;
}

.page-size-select {
  padding: 4px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.pagination-center {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>