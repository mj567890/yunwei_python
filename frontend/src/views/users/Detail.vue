<template>
  <div class="user-detail-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="btn btn-secondary">
          ← 返回列表
        </button>
        <h1>用户详情</h1>
      </div>
      <div class="header-actions">
        <button @click="editUser" class="btn btn-primary">✏️ 编辑用户</button>
        <button @click="resetPassword" class="btn btn-warning">🔑 重置密码</button>
        <button 
          @click="toggleUserStatus" 
          :class="`btn ${userInfo.status ? 'btn-danger' : 'btn-success'}`"
        >
          {{ userInfo.status ? '🚫 禁用用户' : '✅ 启用用户' }}
        </button>
      </div>
    </div>

    <!-- 用户基本信息 -->
    <div class="user-info-section">
      <div class="info-header">
        <div class="user-avatar-large">
          <img v-if="userInfo.avatar" :src="userInfo.avatar" :alt="userInfo.real_name" />
          <div v-else class="avatar-placeholder-large">
            {{ userInfo.real_name ? userInfo.real_name.charAt(0) : userInfo.username.charAt(0) }}
          </div>
        </div>
        <div class="user-basic-info">
          <h2>{{ userInfo.real_name || userInfo.username }}</h2>
          <div class="user-meta">
            <span class="username">@{{ userInfo.username }}</span>
            <span :class="`status-badge status-${userInfo.status ? 'active' : 'inactive'}`">
              {{ userInfo.status ? '启用' : '禁用' }}
            </span>
          </div>
          <div class="user-roles">
            <span 
              v-for="role in userInfo.roles" 
              :key="role.id" 
              :class="`role-badge role-${role.code}`"
            >
              {{ role.name }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细信息卡片 -->
    <div class="details-grid">
      <!-- 基本信息 -->
      <div class="detail-card">
        <div class="card-header">
          <h3>👤 基本信息</h3>
        </div>
        <div class="card-content">
          <div class="info-item">
            <span class="label">用户ID:</span>
            <span class="value">{{ userInfo.id }}</span>
          </div>
          <div class="info-item">
            <span class="label">用户名:</span>
            <span class="value">{{ userInfo.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">真实姓名:</span>
            <span class="value">{{ userInfo.real_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">邮箱:</span>
            <span class="value">{{ userInfo.email || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">手机号:</span>
            <span class="value">{{ userInfo.phone || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">部门:</span>
            <span class="value">{{ userInfo.department || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">职位:</span>
            <span class="value">{{ userInfo.position || '-' }}</span>
          </div>
        </div>
      </div>

      <!-- 账户状态 -->
      <div class="detail-card">
        <div class="card-header">
          <h3>🔐 账户状态</h3>
        </div>
        <div class="card-content">
          <div class="info-item">
            <span class="label">账户状态:</span>
            <span :class="`value status-${userInfo.status ? 'active' : 'inactive'}`">
              {{ userInfo.status ? '启用' : '禁用' }}
            </span>
          </div>
          <div class="info-item">
            <span class="label">创建时间:</span>
            <span class="value">{{ formatDate(userInfo.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">最后更新:</span>
            <span class="value">{{ formatDate(userInfo.updated_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">最后登录:</span>
            <span class="value">{{ userInfo.last_login_time ? formatDate(userInfo.last_login_time) : '从未登录' }}</span>
          </div>
          <div class="info-item">
            <span class="label">登录IP:</span>
            <span class="value">{{ userInfo.last_login_ip || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">登录次数:</span>
            <span class="value">{{ userInfo.login_count || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- 权限信息 -->
      <div class="detail-card">
        <div class="card-header">
          <h3>🛡️ 权限信息</h3>
        </div>
        <div class="card-content">
          <div class="roles-section">
            <h4>分配角色</h4>
            <div class="roles-list">
              <div v-for="role in userInfo.roles" :key="role.id" class="role-item">
                <span :class="`role-badge role-${role.code}`">{{ role.name }}</span>
                <span class="role-desc">{{ role.description }}</span>
              </div>
            </div>
          </div>
          <div class="permissions-section">
            <h4>具体权限</h4>
            <div class="permissions-grid">
              <span 
                v-for="permission in userInfo.permissions" 
                :key="permission.id"
                class="permission-tag"
              >
                {{ permission.name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作历史 -->
      <div class="detail-card full-width">
        <div class="card-header">
          <h3>📋 最近操作历史</h3>
          <button @click="viewAllLogs" class="btn btn-sm btn-info">查看全部</button>
        </div>
        <div class="card-content">
          <div class="logs-list">
            <div v-for="log in userInfo.recent_logs" :key="log.id" class="log-item">
              <div class="log-icon">
                <span :class="`log-type log-${log.type}`">{{ getLogIcon(log.type) }}</span>
              </div>
              <div class="log-content">
                <div class="log-action">{{ log.action }}</div>
                <div class="log-meta">
                  <span class="log-time">{{ formatDate(log.created_at) }}</span>
                  <span class="log-ip">{{ log.ip_address }}</span>
                </div>
              </div>
              <div class="log-result">
                <span :class="`result-badge result-${log.result}`">
                  {{ log.result === 'success' ? '成功' : '失败' }}
                </span>
              </div>
            </div>
          </div>
          
          <div v-if="!userInfo.recent_logs || userInfo.recent_logs.length === 0" class="no-logs">
            <span class="empty-icon">📝</span>
            <p>暂无操作记录</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface UserRole {
  id: number
  name: string
  code: string
  description: string
}

interface UserPermission {
  id: number
  name: string
  code: string
}

interface UserLog {
  id: number
  action: string
  type: string
  result: string
  ip_address: string
  created_at: string
}

interface UserInfo {
  id: number
  username: string
  real_name: string
  email: string
  phone: string
  avatar: string
  department: string
  position: string
  status: number
  roles: UserRole[]
  permissions: UserPermission[]
  recent_logs: UserLog[]
  created_at: string
  updated_at: string
  last_login_time: string
  last_login_ip: string
  login_count: number
}

const route = useRoute()
const router = useRouter()

const userInfo = ref<UserInfo>({
  id: 1,
  username: 'admin',
  real_name: '系统管理员',
  email: 'admin@itops.com',
  phone: '13800138000',
  avatar: '',
  department: 'IT部',
  position: '系统管理员',
  status: 1,
  roles: [
    { id: 1, name: '系统管理员', code: 'admin', description: '拥有系统全部权限' }
  ],
  permissions: [
    { id: 1, name: '用户管理', code: 'user:manage' },
    { id: 2, name: '系统设置', code: 'system:config' },
    { id: 3, name: '数据导出', code: 'data:export' }
  ],
  recent_logs: [
    {
      id: 1,
      action: '登录系统',
      type: 'login',
      result: 'success',
      ip_address: '192.168.1.100',
      created_at: '2024-01-15 10:30:00'
    },
    {
      id: 2,
      action: '修改用户信息',
      type: 'update',
      result: 'success',
      ip_address: '192.168.1.100',
      created_at: '2024-01-15 09:15:00'
    },
    {
      id: 3,
      action: '导出资产数据',
      type: 'export',
      result: 'success',
      ip_address: '192.168.1.100',
      created_at: '2024-01-14 16:45:00'
    }
  ],
  created_at: '2024-01-01 09:00:00',
  updated_at: '2024-01-15 10:30:00',
  last_login_time: '2024-01-15 10:30:00',
  last_login_ip: '192.168.1.100',
  login_count: 156
})

// 数据加载
const loadUserDetail = async () => {
  const userId = route.params.id
  try {
    // 这里应该调用API获取用户详情
    console.log('加载用户详情:', userId)
  } catch (error) {
    console.error('加载用户详情失败:', error)
  }
}

// 工具函数
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getLogIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    'login': '🔑',
    'logout': '🚪',
    'create': '➕',
    'update': '✏️',
    'delete': '🗑️',
    'export': '📤',
    'import': '📥'
  }
  return iconMap[type] || '📝'
}

// 事件处理
const goBack = () => {
  router.go(-1)
}

const editUser = () => {
  router.push(`/app/users/edit/${userInfo.value.id}`)
}

const resetPassword = async () => {
  if (confirm(`确认重置用户 "${userInfo.value.real_name || userInfo.value.username}" 的密码吗？`)) {
    try {
      // 这里应该调用重置密码API
      console.log('重置密码')
      alert('密码已重置为默认密码，请提醒用户及时修改')
    } catch (error) {
      console.error('重置密码失败:', error)
      alert('重置密码失败，请重试')
    }
  }
}

const toggleUserStatus = async () => {
  const action = userInfo.value.status ? '禁用' : '启用'
  if (confirm(`确认${action}用户 "${userInfo.value.real_name || userInfo.value.username}" 吗？`)) {
    try {
      // 这里应该调用状态切换API
      userInfo.value.status = userInfo.value.status ? 0 : 1
      console.log(`${action}用户成功`)
    } catch (error) {
      console.error(`${action}用户失败:`, error)
    }
  }
}

const viewAllLogs = () => {
  router.push(`/app/users/${userInfo.value.id}/logs`)
}

// 初始化
onMounted(() => {
  loadUserDetail()
})
</script>

<style scoped>
.user-detail-container {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.user-info-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.user-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.user-avatar-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder-large {
  color: white;
  font-weight: 600;
  font-size: 28px;
}

.user-basic-info h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.username {
  font-size: 16px;
  opacity: 0.9;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background: rgba(103, 194, 58, 0.2);
  color: #67c23a;
  border: 1px solid rgba(103, 194, 58, 0.3);
}

.status-inactive {
  background: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
  border: 1px solid rgba(245, 108, 108, 0.3);
}

.user-roles {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.role-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.detail-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.detail-card.full-width {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #ebeef5;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.card-content {
  padding: 24px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #606266;
  font-weight: 500;
  min-width: 100px;
}

.info-item .value {
  color: #303133;
  text-align: right;
  font-family: monospace;
}

.value.status-active {
  color: #67c23a;
}

.value.status-inactive {
  color: #f56c6c;
}

.roles-section, .permissions-section {
  margin-bottom: 20px;
}

.roles-section h4, .permissions-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.roles-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.role-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-item .role-desc {
  color: #909399;
  font-size: 12px;
}

.permissions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.permission-tag {
  padding: 4px 8px;
  background: #e1f3ff;
  color: #409eff;
  border-radius: 4px;
  font-size: 12px;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.log-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: white;
}

.log-type {
  font-size: 16px;
}

.log-content {
  flex: 1;
}

.log-action {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.log-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.log-ip {
  font-family: monospace;
}

.result-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.result-success {
  background: #f0f9ff;
  color: #67c23a;
}

.result-failed {
  background: #fef0f0;
  color: #f56c6c;
}

.no-logs {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
  display: block;
}

.btn, .btn-sm {
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn {
  padding: 10px 16px;
  font-size: 14px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-primary { background: #409eff; color: white; }
.btn-primary:hover { background: #66b1ff; }

.btn-secondary { background: #909399; color: white; }
.btn-secondary:hover { background: #a6a9ad; }

.btn-info { background: #17a2b8; color: white; }
.btn-info:hover { background: #138496; }

.btn-warning { background: #e6a23c; color: white; }
.btn-warning:hover { background: #ebb563; }

.btn-success { background: #67c23a; color: white; }
.btn-success:hover { background: #85ce61; }

.btn-danger { background: #f56c6c; color: white; }
.btn-danger:hover { background: #f78989; }

/* 响应式设计 */
@media (max-width: 768px) {
  .user-detail-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-left {
    justify-content: center;
  }
  
  .header-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .info-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .info-item .value {
    text-align: left;
  }
}
</style>