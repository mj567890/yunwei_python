<template>
  <div class="fault-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>故障管理</h1>
      <div class="header-actions">
        <button @click="refreshFaults" class="btn btn-secondary">🔄 刷新</button>
        <button @click="createFault" class="btn btn-primary">🚨 新增故障</button>
        <button @click="exportFaults" class="btn btn-info">📊 导出</button>
      </div>
    </div>

    <!-- 故障统计卡片 -->
    <div class="stats-cards">
      <div class="stats-card urgent">
        <div class="stats-icon">🚨</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.urgent }}</div>
          <div class="stats-label">紧急故障</div>
        </div>
      </div>
      <div class="stats-card high">
        <div class="stats-icon">⚠️</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.high }}</div>
          <div class="stats-label">高优先级</div>
        </div>
      </div>
      <div class="stats-card pending">
        <div class="stats-icon">⏳</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.pending }}</div>
          <div class="stats-label">待处理</div>
        </div>
      </div>
      <div class="stats-card resolved">
        <div class="stats-icon">✅</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.resolved }}</div>
          <div class="stats-label">已解决</div>
        </div>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>故障编号/标题</label>
          <input v-model="searchParams.keyword" placeholder="搜索故障编号或标题" />
        </div>
        <div class="form-group">
          <label>故障类型</label>
          <select v-model="searchParams.fault_type">
            <option value="">全部类型</option>
            <option value="硬件故障">硬件故障</option>
            <option value="软件故障">软件故障</option>
            <option value="网络故障">网络故障</option>
            <option value="系统故障">系统故障</option>
            <option value="其他">其他</option>
          </select>
        </div>
        <div class="form-group">
          <label>优先级</label>
          <select v-model="searchParams.priority">
            <option value="">全部优先级</option>
            <option value="紧急">紧急</option>
            <option value="高">高</option>
            <option value="中">中</option>
            <option value="低">低</option>
          </select>
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="searchParams.status">
            <option value="">全部状态</option>
            <option value="新建">新建</option>
            <option value="处理中">处理中</option>
            <option value="已解决">已解决</option>
            <option value="已关闭">已关闭</option>
          </select>
        </div>
        <div class="form-group">
          <button @click="searchFaults" class="btn btn-primary">🔍 搜索</button>
          <button @click="resetSearch" class="btn btn-secondary">🔄 重置</button>
        </div>
      </div>
    </div>

    <!-- 故障列表 -->
    <div class="table-container">
      <div v-if="loading" class="loading">
        <div class="loading-spinner">🔄</div>
        <p>加载中...</p>
      </div>
      
      <table v-else class="fault-table">
        <thead>
          <tr>
            <th width="60">序号</th>
            <th>故障编号</th>
            <th>标题</th>
            <th>类型</th>
            <th>影响资产</th>
            <th>优先级</th>
            <th>状态</th>
            <th>报告人</th>
            <th>处理人</th>
            <th>创建时间</th>
            <th>响应时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(fault, index) in faultList" :key="fault.id" :class="{ 'row-urgent': fault.priority === '紧急' }">
            <td class="row-number">{{ (pagination.page - 1) * pagination.pageSize + index + 1 }}</td>
            <td class="fault-code">{{ fault.fault_code }}</td>
            <td class="fault-title">
              <div class="title-content">
                <span class="title">{{ fault.title }}</span>
                <div class="meta">
                  <span class="severity">{{ fault.severity }}</span>
                  <span v-if="fault.sla_breach" class="sla-warning">⏰ SLA超时</span>
                </div>
              </div>
            </td>
            <td>
              <span class="type-tag">{{ fault.fault_type }}</span>
            </td>
            <td class="affected-assets">
              <div v-if="fault.affected_assets && fault.affected_assets.length > 0">
                <div v-for="asset in fault.affected_assets.slice(0, 2)" :key="asset.id" class="asset-item">
                  <span class="asset-name">{{ asset.name }}</span>
                </div>
                <span v-if="fault.affected_assets.length > 2" class="more-assets">
                  +{{ fault.affected_assets.length - 2 }}个
                </span>
              </div>
              <span v-else class="no-assets">无关联资产</span>
            </td>
            <td>
              <span :class="`priority-tag priority-${getPriorityClass(fault.priority)}`">
                {{ fault.priority }}
              </span>
            </td>
            <td>
              <span :class="`status-tag status-${getStatusClass(fault.status)}`">
                {{ fault.status }}
              </span>
            </td>
            <td>
              <div class="user-info">
                <span class="name">{{ fault.reporter_name }}</span>
                <span class="time">{{ formatTime(fault.report_time) }}</span>
              </div>
            </td>
            <td>
              <div class="user-info" v-if="fault.assignee_name">
                <span class="name">{{ fault.assignee_name }}</span>
                <span class="time">{{ fault.assign_time ? formatTime(fault.assign_time) : '' }}</span>
              </div>
              <span v-else class="unassigned">未分配</span>
            </td>
            <td>{{ formatDate(fault.created_at) }}</td>
            <td>
              <span v-if="fault.response_time" :class="getResponseTimeClass(fault.response_time, fault.priority)">
                {{ fault.response_time }}
              </span>
              <span v-else class="no-response">未响应</span>
            </td>
            <td class="actions">
              <button @click="viewFault(fault)" class="btn-sm btn-info">查看</button>
              <button @click="editFault(fault)" class="btn-sm btn-primary">编辑</button>
              <button @click="assignFault(fault)" class="btn-sm btn-warning">分配</button>
              <button @click="closeFault(fault)" class="btn-sm btn-success">关闭</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 空状态 -->
      <div v-if="!loading && faultList.length === 0" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>暂无故障记录</p>
        <button @click="createFault" class="btn btn-primary">报告第一个故障</button>
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
import type { Fault, FaultSearchParams, PaginationInfo } from '@/types/common'
import { getFaultStatusClass, getPriorityClass as getCommonPriorityClass } from '@/types/common'

// 定义故障数据类型
interface FaultItem extends Fault {
  // 可以扩展额外的属性
}

const router = useRouter()

// 状态管理
const loading = ref(false)
const faultList = ref<FaultItem[]>([])
const searchParams = reactive<FaultSearchParams>({
  keyword: '',
  fault_type: '',
  priority: '',
  status: '',
  page: 1,
  pageSize: 20
})

const pagination = reactive<PaginationInfo>({
  total: 0,
  page: 1,
  pageSize: 20
})

const stats = reactive({
  urgent: 5,
  high: 12,
  pending: 23,
  resolved: 156
})

// 模拟数据
const mockFaults: FaultItem[] = [
  {
    id: 1,
    fault_code: 'FLT20240001',
    title: '数据库服务器连接超时',
    fault_type: '系统故障',
    severity: '高',
    priority: '紧急',
    status: '处理中',
    reporter_name: '张三',
    report_time: '2024-01-15 09:30:00',
    assignee_name: '李四',
    assign_time: '2024-01-15 09:45:00',
    created_at: '2024-01-15 09:30:00',
    response_time: '15分钟',
    sla_breach: false,
    affected_assets: [
      { id: 1, name: 'DB-Server-01' },
      { id: 2, name: 'DB-Server-02' }
    ]
  },
  {
    id: 2,
    fault_code: 'FLT20240002',
    title: '网络交换机端口故障',
    fault_type: '硬件故障',
    severity: '中',
    priority: '高',
    status: '新建',
    reporter_name: '王五',
    report_time: '2024-01-15 14:20:00',
    assignee_name: null,
    assign_time: null,
    created_at: '2024-01-15 14:20:00',
    response_time: null,
    sla_breach: false,
    affected_assets: [
      { id: 3, name: 'SW-Core-01' }
    ]
  },
  {
    id: 3,
    fault_code: 'FLT20240003',
    title: '邮件系统无法发送邮件',
    fault_type: '软件故障',
    severity: '中',
    priority: '中',
    status: '已解决',
    reporter_name: '赵六',
    report_time: '2024-01-14 16:10:00',
    assignee_name: '孙七',
    assign_time: '2024-01-14 16:25:00',
    created_at: '2024-01-14 16:10:00',
    response_time: '15分钟',
    sla_breach: false,
    affected_assets: []
  }
]

// 数据加载
const loadFaults = async () => {
  loading.value = true
  try {
    // 这里应该调用真实的API
    await new Promise(resolve => setTimeout(resolve, 500))
    
    faultList.value = mockFaults
    pagination.total = mockFaults.length
    pagination.page = searchParams.page
  } catch (error) {
    console.error('加载故障列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 工具函数
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusClass = (status: string) => {
  return getFaultStatusClass(status)
}

const getPriorityClass = (priority: string) => {
  return getCommonPriorityClass(priority)
}

const getResponseTimeClass = (responseTime: string, priority: string) => {
  if (!responseTime) return ''
  
  // 根据优先级判断响应时间是否合理
  const minutes = parseInt(responseTime)
  if (priority === '紧急' && minutes > 30) return 'response-slow'
  if (priority === '高' && minutes > 60) return 'response-slow'
  if (priority === '中' && minutes > 120) return 'response-slow'
  
  return 'response-good'
}

// 事件处理
const searchFaults = () => {
  searchParams.page = 1
  loadFaults()
}

const resetSearch = () => {
  Object.assign(searchParams, {
    keyword: '',
    fault_type: '',
    priority: '',
    status: '',
    page: 1,
    pageSize: 20
  })
  loadFaults()
}

const refreshFaults = () => loadFaults()

const changePage = (page: number) => {
  searchParams.page = page
  loadFaults()
}

// 改变每页条数
const changePageSize = () => {
  searchParams.pageSize = pagination.pageSize
  searchParams.page = 1  // 重置到第一页
  pagination.page = 1
  loadFaults()
}

const createFault = () => {
  router.push('/app/faults/create')
}

const viewFault = (fault: any) => {
  router.push(`/app/faults/detail/${fault.id}`)
}

const editFault = (fault: any) => {
  router.push(`/app/faults/edit/${fault.id}`)
}

const assignFault = (fault: any) => {
  console.log('分配故障:', fault)
  // TODO: 打开分配对话框
}

const closeFault = async (fault: any) => {
  if (confirm(`确认关闭故障 "${fault.title}" 吗？`)) {
    try {
      // 这里应该调用关闭API
      console.log('关闭故障成功')
      await loadFaults()
    } catch (error) {
      console.error('关闭故障失败:', error)
    }
  }
}

const exportFaults = () => {
  console.log('导出故障数据')
  // TODO: 实现导出功能
}

// 初始化
onMounted(() => {
  loadFaults()
})
</script>

<style scoped>
.fault-management-container {
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
  position: relative;
  overflow: hidden;
}

.stats-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.stats-card.urgent::before { background: #f56c6c; }
.stats-card.high::before { background: #e6a23c; }
.stats-card.pending::before { background: #409eff; }
.stats-card.resolved::before { background: #67c23a; }

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

.fault-table {
  width: 100%;
  border-collapse: collapse;
}

.fault-table th {
  background: #f8f9fa;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
}

.fault-table td {
  padding: 16px 12px;
  border-bottom: 1px solid #ebeef5;
  vertical-align: middle;
}

.row-urgent {
  background: rgba(245, 108, 108, 0.02);
  border-left: 4px solid #f56c6c;
}

.fault-code {
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

.severity {
  margin-right: 8px;
}

.sla-warning {
  color: #f56c6c;
  font-weight: 500;
}

.type-tag {
  background: #e1f3ff;
  color: #409eff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.affected-assets {
  max-width: 120px;
}

.asset-item {
  font-size: 12px;
  color: #606266;
  margin-bottom: 2px;
}

.asset-name {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.more-assets {
  font-size: 11px;
  color: #909399;
}

.no-assets {
  font-size: 12px;
  color: #c0c4cc;
}

.priority-tag, .status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.priority-low { background: #f4f4f5; color: #909399; }
.priority-medium { background: #e1f3ff; color: #409eff; }
.priority-high { background: #fdf6ec; color: #e6a23c; }
.priority-urgent { background: #fef0f0; color: #f56c6c; }

.status-info { background: #e1f3ff; color: #409eff; }
.status-warning { background: #fdf6ec; color: #e6a23c; }
.status-success { background: #f0f9ff; color: #67c23a; }
.status-secondary { background: #f4f4f5; color: #909399; }

.user-info .name {
  display: block;
  font-weight: 500;
  color: #303133;
  font-size: 13px;
}

.user-info .time {
  font-size: 11px;
  color: #909399;
}

.unassigned {
  color: #c0c4cc;
  font-size: 12px;
}

.response-good { color: #67c23a; }
.response-slow { color: #f56c6c; }
.no-response { color: #c0c4cc; font-size: 12px; }

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

.btn-success { background: #67c23a; color: white; }
.btn-success:hover { background: #85ce61; }

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
  justify-content: space-between;
  align-items: center;
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
  .fault-management-container {
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
  
  .fault-table {
    font-size: 12px;
  }
  
  .fault-table th,
  .fault-table td {
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