<template>
  <div class="user-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>用户管理</h1>
      <div class="header-actions">
        <button @click="refreshUsers" class="btn btn-secondary">🔄 刷新</button>
        <button @click="createUser" class="btn btn-primary">👤 新增用户</button>
        <button @click="exportUserData" class="btn btn-info">📊 导出</button>
      </div>
    </div>

    <!-- 用户统计卡片 -->
    <div class="stats-cards">
      <div class="stats-card">
        <div class="stats-icon">👥</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.total }}</div>
          <div class="stats-label">总用户数</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">✅</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.active }}</div>
          <div class="stats-label">活跃用户</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">🔒</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.admins }}</div>
          <div class="stats-label">管理员</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">🕐</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.online }}</div>
          <div class="stats-label">在线</div>
        </div>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>用户名/姓名</label>
          <input v-model="searchParams.keyword" placeholder="搜索用户名或真实姓名" />
        </div>
        <div class="form-group">
          <label>角色</label>
          <select v-model="searchParams.role">
            <option value="">全部角色</option>
            <option value="admin">管理员</option>
            <option value="operator">运维员</option>
            <option value="viewer">查看员</option>
          </select>
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="searchParams.status">
            <option value="">全部状态</option>
            <option value="1">启用</option>
            <option value="0">禁用</option>
          </select>
        </div>
        <div class="form-group">
          <label>部门</label>
          <select v-model="searchParams.department">
            <option value="">全部部门</option>
            <option value="IT部">IT部</option>
            <option value="运维部">运维部</option>
            <option value="网络部">网络部</option>
            <option value="安全部">安全部</option>
          </select>
        </div>
        <div class="form-group">
          <button @click="searchUsers" class="btn btn-primary">🔍 搜索</button>
          <button @click="resetSearch" class="btn btn-secondary">🔄 重置</button>
        </div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="table-container">
      <div v-if="loading" class="loading">
        <div class="loading-spinner">🔄</div>
        <p>加载中...</p>
      </div>
      
      <table v-else class="user-table">
        <thead>
          <tr>
            <th>
              <input type="checkbox" @change="selectAll" :checked="selectedAll" />
            </th>
            <th width="60">序号</th>
            <th>头像</th>
            <th>用户名</th>
            <th>真实姓名</th>
            <th>邮箱</th>
            <th>手机号</th>
            <th>部门</th>
            <th>角色</th>
            <th>状态</th>
            <th>最后登录</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in userList" :key="user.id">
            <td>
              <input 
                type="checkbox" 
                :value="user.id" 
                v-model="selectedUsers"
                @change="updateSelection"
              />
            </td>
            <td class="row-number">{{ (pagination.page - 1) * pagination.pageSize + index + 1 }}</td>
            <td>
              <div class="user-avatar">
                <img v-if="user.avatar" :src="user.avatar" :alt="user.real_name" />
                <div v-else class="avatar-placeholder">
                  {{ user.real_name ? user.real_name.charAt(0) : user.username.charAt(0) }}
                </div>
              </div>
            </td>
            <td class="username">{{ user.username }}</td>
            <td class="real-name">{{ user.real_name || '-' }}</td>
            <td class="email">{{ user.email || '-' }}</td>
            <td class="phone">{{ user.phone || '-' }}</td>
            <td class="department">{{ user.department || '-' }}</td>
            <td>
              <div class="user-roles">
                <span 
                  v-for="role in user.roles" 
                  :key="role.id" 
                  :class="`role-tag role-${role.code}`"
                >
                  {{ role.name }}
                </span>
              </div>
            </td>
            <td>
              <span :class="`status-tag status-${user.status ? 'active' : 'inactive'}`">
                {{ user.status ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="last-login">
              <div v-if="user.last_login_time">
                <div class="login-time">{{ formatDate(user.last_login_time) }}</div>
                <div class="login-ip">{{ user.last_login_ip || '' }}</div>
              </div>
              <span v-else class="never-login">从未登录</span>
            </td>
            <td class="created-time">{{ formatDate(user.created_at) }}</td>
            <td class="actions">
              <button @click="viewUser(user)" class="btn-sm btn-info">查看</button>
              <button @click="editUser(user)" class="btn-sm btn-primary">编辑</button>
              <button @click="resetPassword(user)" class="btn-sm btn-warning">重置密码</button>
              <button 
                @click="toggleUserStatus(user)" 
                :class="`btn-sm ${user.status ? 'btn-danger' : 'btn-success'}`"
              >
                {{ user.status ? '禁用' : '启用' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 空状态 -->
      <div v-if="!loading && userList.length === 0" class="empty-state">
        <div class="empty-icon">👤</div>
        <p>暂无用户数据</p>
        <button @click="createUser" class="btn btn-primary">创建第一个用户</button>
      </div>
    </div>

    <!-- 批量操作栏 -->
    <div v-if="selectedUsers.length > 0" class="batch-actions">
      <div class="selected-info">
        已选择 {{ selectedUsers.length }} 个用户
      </div>
      <div class="actions">
        <button @click="batchEnable" class="btn btn-success">批量启用</button>
        <button @click="batchDisable" class="btn btn-warning">批量禁用</button>
        <button @click="batchAssignRole" class="btn btn-primary">批量分配角色</button>
        <button @click="batchDelete" class="btn btn-danger">批量删除</button>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userApi, type UserRole } from '@/api/user'
import { exportUsers } from '@/utils/export'
import type { UserInfo, UserSearchParams, PaginationInfo } from '@/types/common'

interface UserItem extends UserInfo {
  // 可以扩展额外属性
}

const router = useRouter()

// 状态管理
const loading = ref(false)
const userList = ref<UserItem[]>([])
const selectedUsers = ref<number[]>([])

const searchParams = reactive<UserSearchParams>({
  keyword: '',
  role: '',
  status: '',
  department: '',
  page: 1,
  pageSize: 20
})

const pagination = reactive<PaginationInfo>({
  total: 0,
  page: 1,
  pageSize: 20
})

const stats = reactive({
  total: 0,
  active: 0,
  admins: 0,
  online: 0
})

// 计算属性
const selectedAll = computed(() => {
  return userList.value.length > 0 && selectedUsers.value.length === userList.value.length
})

// 数据加载
const loadUsers = async () => {
  loading.value = true
  try {
    const response = await userApi.getUsers(searchParams)
    if (response.success) {
      userList.value = response.data.list
      Object.assign(pagination, response.data.pagination)
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
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

// 选择相关
const selectAll = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.checked) {
    selectedUsers.value = userList.value.map(user => user.id)
  } else {
    selectedUsers.value = []
  }
}

const updateSelection = () => {
  // 选择状态会自动更新
}

// 事件处理
const searchUsers = () => {
  searchParams.page = 1
  loadUsers()
}

const resetSearch = () => {
  Object.assign(searchParams, {
    keyword: '',
    role: '',
    status: '',
    department: '',
    page: 1,
    pageSize: 20
  })
  loadUsers()
}

const refreshUsers = () => loadUsers()

const changePage = (page: number) => {
  searchParams.page = page
  loadUsers()
}

// 改变每页条数
const changePageSize = () => {
  searchParams.pageSize = pagination.pageSize
  searchParams.page = 1  // 重置到第一页
  pagination.page = 1
  loadUsers()
}

const createUser = () => {
  router.push('/app/users/create')
}

const viewUser = (user: UserItem) => {
  router.push(`/app/users/detail/${user.id}`)
}

const editUser = (user: UserItem) => {
  router.push(`/app/users/edit/${user.id}`)
}

const resetPassword = async (user: UserItem) => {
  if (confirm(`确认重置用户 "${user.real_name || user.username}" 的密码吗？`)) {
    try {
      const response = await userApi.resetPassword(user.id)
      if (response.success) {
        alert('密码已重置为默认密码，请提醒用户及时修改')
      }
    } catch (error) {
      console.error('重置密码失败:', error)
      alert('重置密码失败，请稍后重试')
    }
  }
}

const toggleUserStatus = async (user: UserItem) => {
  const action = user.status ? '禁用' : '启用'
  if (confirm(`确认${action}用户 "${user.real_name || user.username}" 吗？`)) {
    try {
      const newStatus = user.status ? 0 : 1
      const response = await userApi.updateUser(user.id, { status: newStatus })
      if (response.success) {
        user.status = newStatus
        console.log(`${action}用户成功`)
      }
    } catch (error) {
      console.error(`${action}用户失败:`, error)
      alert(`${action}用户失败，请稍后重试`)
    }
  }
}

// 批量操作
const batchEnable = async () => {
  if (confirm(`确认启用选中的 ${selectedUsers.value.length} 个用户吗？`)) {
    try {
      const response = await userApi.batchEnable(selectedUsers.value)
      if (response.success) {
        console.log('批量启用成功')
        selectedUsers.value = []
        await loadUsers()
      }
    } catch (error) {
      console.error('批量启用失败:', error)
      alert('批量启用失败，请稍后重试')
    }
  }
}

const batchDisable = async () => {
  if (confirm(`确认禁用选中的 ${selectedUsers.value.length} 个用户吗？`)) {
    try {
      const response = await userApi.batchDisable(selectedUsers.value)
      if (response.success) {
        console.log('批量禁用成功')
        selectedUsers.value = []
        await loadUsers()
      }
    } catch (error) {
      console.error('批量禁用失败:', error)
      alert('批量禁用失败，请稍后重试')
    }
  }
}

const batchAssignRole = () => {
  console.log('批量分配角色')
  // TODO: 打开角色分配对话框
}

const batchDelete = async () => {
  if (confirm(`确认删除选中的 ${selectedUsers.value.length} 个用户吗？此操作不可恢复！`)) {
    try {
      const response = await userApi.batchDelete(selectedUsers.value)
      if (response.success) {
        console.log('批量删除成功')
        selectedUsers.value = []
        await loadUsers()
      }
    } catch (error) {
      console.error('批量删除失败:', error)
      alert('批量删除失败，请稍后重试')
    }
  }
}

const exportUserData = async () => {
  try {
    exportUsers(userList.value)
    console.log('导出用户数据成功')
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请稍后重试')
  }
}

// 初始化
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management-container {
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

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th {
  background: #f8f9fa;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
}

.user-table td {
  padding: 16px 12px;
  border-bottom: 1px solid #ebeef5;
  vertical-align: middle;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  color: #606266;
  font-weight: 500;
  font-size: 16px;
}

.username {
  font-weight: 500;
  color: #303133;
}

.user-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.role-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.role-admin { background: #fef0f0; color: #f56c6c; }
.role-operator { background: #e1f3ff; color: #409eff; }
.role-viewer { background: #f0f9ff; color: #67c23a; }

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-active { background: #f0f9ff; color: #67c23a; }
.status-inactive { background: #f4f4f5; color: #909399; }

.last-login .login-time {
  font-weight: 500;
  color: #303133;
}

.last-login .login-ip {
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}

.never-login {
  color: #c0c4cc;
  font-size: 12px;
}

.created-time {
  color: #606266;
  font-size: 13px;
}

.actions {
  white-space: nowrap;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 20px;
  z-index: 1000;
}

.selected-info {
  color: #606266;
  font-weight: 500;
}

.batch-actions .actions {
  display: flex;
  gap: 8px;
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
  justify-content: space-between;
  align-items: center;
  gap: 20px;
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

.page-info {
  color: #606266;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-management-container {
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
  
  .user-table {
    font-size: 12px;
  }
  
  .user-table th,
  .user-table td {
    padding: 8px 6px;
  }
  
  .batch-actions {
    position: relative;
    bottom: auto;
    left: auto;
    transform: none;
    flex-direction: column;
    gap: 12px;
  }
}

.row-number {
  text-align: center;
  font-weight: 500;
  color: #909399;
  font-size: 13px;
  width: 60px;
}
</style>