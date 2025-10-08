<template>
  <div class="profile-page">
    <div class="page-header">
      <div class="header-content">
        <h2>个人中心</h2>
        <div class="header-actions">
          <el-button @click="goBack">返回</el-button>
          <el-button type="primary" @click="saveProfile" :loading="saving">
            保存修改
          </el-button>
        </div>
      </div>
    </div>

    <div class="page-content">
      <el-row :gutter="24">
        <el-col :span="6">
          <!-- 个人信息卡片 -->
          <el-card class="profile-card">
            <div class="avatar-section">
              <div class="avatar-container">
                <img 
                  :src="profile.avatar || defaultAvatar" 
                  :alt="profile.real_name"
                  class="user-avatar"
                />
                <div class="avatar-overlay" @click="changeAvatar">
                  <span class="change-text">更换头像</span>
                </div>
              </div>
              <div class="user-basic-info">
                <h3>{{ profile.real_name || profile.username }}</h3>
                <p class="username">@{{ profile.username }}</p>
                <div class="user-roles">
                  <el-tag 
                    v-for="role in profile.roles" 
                    :key="role.id" 
                    :type="getRoleType(role.code)"
                    size="small"
                  >
                    {{ role.name }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <div class="stats-section">
              <div class="stat-item">
                <div class="stat-value">{{ profile.login_count || 0 }}</div>
                <div class="stat-label">登录次数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ getDaysJoined() }}</div>
                <div class="stat-label">加入天数</div>
              </div>
            </div>
          </el-card>

          <!-- 快速操作 -->
          <el-card title="快速操作" class="quick-actions-card">
            <div class="action-list">
              <div class="action-item" @click="changePassword">
                <span class="action-icon">🔑</span>
                <span class="action-text">修改密码</span>
                <span class="action-arrow">›</span>
              </div>
              <div class="action-item" @click="viewActivityLog">
                <span class="action-icon">📋</span>
                <span class="action-text">操作记录</span>
                <span class="action-arrow">›</span>
              </div>
              <div class="action-item" @click="downloadData">
                <span class="action-icon">📥</span>
                <span class="action-text">导出数据</span>
                <span class="action-arrow">›</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="18">
          <el-tabs v-model="activeTab" class="profile-tabs">
            <!-- 基本信息 -->
            <el-tab-pane label="基本信息" name="basic">
              <el-form 
                ref="formRef" 
                :model="profile" 
                :rules="rules" 
                label-width="120px"
                class="profile-form"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="真实姓名" prop="real_name">
                      <el-input v-model="profile.real_name" placeholder="请输入真实姓名" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="用户名" prop="username">
                      <el-input v-model="profile.username" disabled />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="邮箱地址" prop="email">
                      <el-input v-model="profile.email" type="email" placeholder="请输入邮箱地址" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="手机号码" prop="phone">
                      <el-input v-model="profile.phone" placeholder="请输入手机号码" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="部门">
                      <el-input v-model="profile.department" placeholder="请输入部门" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="职位">
                      <el-input v-model="profile.position" placeholder="请输入职位" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item label="个人简介">
                  <el-input 
                    v-model="profile.bio" 
                    type="textarea" 
                    :rows="4"
                    placeholder="简单介绍一下自己..."
                  />
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 安全设置 -->
            <el-tab-pane label="安全设置" name="security">
              <div class="security-settings">
                <div class="setting-group">
                  <h4>密码安全</h4>
                  <div class="setting-item">
                    <div class="setting-content">
                      <div class="setting-title">登录密码</div>
                      <div class="setting-desc">定期更新密码以保护账户安全</div>
                    </div>
                    <el-button @click="changePassword">修改密码</el-button>
                  </div>
                </div>

                <div class="setting-group">
                  <h4>登录安全</h4>
                  <div class="setting-item">
                    <div class="setting-content">
                      <div class="setting-title">双因素认证</div>
                      <div class="setting-desc">启用后需要手机验证码才能登录</div>
                    </div>
                    <el-switch 
                      v-model="securitySettings.twoFactorAuth" 
                      @change="toggleTwoFactor"
                    />
                  </div>
                  
                  <div class="setting-item">
                    <div class="setting-content">
                      <div class="setting-title">IP访问限制</div>
                      <div class="setting-desc">限制只能从指定IP地址登录</div>
                    </div>
                    <el-switch 
                      v-model="securitySettings.ipRestriction" 
                      @change="toggleIpRestriction"
                    />
                  </div>
                </div>

                <div class="setting-group">
                  <h4>设备管理</h4>
                  <div class="device-list">
                    <div v-for="device in loginDevices" :key="device.id" class="device-item">
                      <div class="device-info">
                        <div class="device-name">{{ device.device_name }}</div>
                        <div class="device-meta">
                          <span>{{ device.ip_address }}</span>
                          <span>{{ formatDate(device.last_login) }}</span>
                        </div>
                      </div>
                      <div class="device-actions">
                        <el-tag v-if="device.is_current" type="success" size="small">当前设备</el-tag>
                        <el-button v-else size="small" type="danger" @click="logoutDevice(device.id)">
                          下线
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- 偏好设置 -->
            <el-tab-pane label="偏好设置" name="preferences">
              <div class="preferences-settings">
                <div class="setting-group">
                  <h4>界面设置</h4>
                  <div class="setting-item">
                    <div class="setting-content">
                      <div class="setting-title">主题模式</div>
                      <div class="setting-desc">选择界面显示主题</div>
                    </div>
                    <el-select v-model="preferences.theme" style="width: 120px">
                      <el-option label="浅色" value="light" />
                      <el-option label="深色" value="dark" />
                      <el-option label="自动" value="auto" />
                    </el-select>
                  </div>
                  
                  <div class="setting-item">
                    <div class="setting-content">
                      <div class="setting-title">语言设置</div>
                      <div class="setting-desc">界面显示语言</div>
                    </div>
                    <el-select v-model="preferences.language" style="width: 120px">
                      <el-option label="中文" value="zh-CN" />
                      <el-option label="English" value="en-US" />
                    </el-select>
                  </div>
                </div>

                <div class="setting-group">
                  <h4>通知设置</h4>
                  <div class="setting-item">
                    <div class="setting-content">
                      <div class="setting-title">邮件通知</div>
                      <div class="setting-desc">接收系统邮件通知</div>
                    </div>
                    <el-switch v-model="preferences.emailNotification" />
                  </div>
                  
                  <div class="setting-item">
                    <div class="setting-content">
                      <div class="setting-title">浏览器通知</div>
                      <div class="setting-desc">显示浏览器推送通知</div>
                    </div>
                    <el-switch v-model="preferences.browserNotification" />
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- 操作记录 -->
            <el-tab-pane label="操作记录" name="activity">
              <div class="activity-log">
                <div class="activity-filters">
                  <el-row :gutter="20">
                    <el-col :span="6">
                      <el-select v-model="logFilter.type" placeholder="操作类型">
                        <el-option label="全部" value="" />
                        <el-option label="登录" value="login" />
                        <el-option label="修改" value="update" />
                        <el-option label="删除" value="delete" />
                      </el-select>
                    </el-col>
                    <el-col :span="8">
                      <el-date-picker
                        v-model="logFilter.dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                      />
                    </el-col>
                    <el-col :span="4">
                      <el-button type="primary" @click="searchLogs">查询</el-button>
                    </el-col>
                  </el-row>
                </div>
                
                <div class="log-list">
                  <div v-for="log in activityLogs" :key="log.id" class="log-item">
                    <div class="log-icon">
                      <span :class="`log-type-${log.type}`">{{ getLogIcon(log.type) }}</span>
                    </div>
                    <div class="log-content">
                      <div class="log-action">{{ log.action }}</div>
                      <div class="log-meta">
                        <span class="log-time">{{ formatDate(log.created_at) }}</span>
                        <span class="log-ip">IP: {{ log.ip_address }}</span>
                        <span class="log-result" :class="`result-${log.result}`">
                          {{ log.result === 'success' ? '成功' : '失败' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input 
            v-model="passwordForm.currentPassword" 
            type="password" 
            show-password
            placeholder="请输入当前密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input 
            v-model="passwordForm.newPassword" 
            type="password" 
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="passwordForm.confirmPassword" 
            type="password" 
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPasswordChange" :loading="changingPassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()

const activeTab = ref('basic')
const saving = ref(false)
const changingPassword = ref(false)
const passwordDialogVisible = ref(false)

const formRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const defaultAvatar = '/default-avatar.jpg'

const profile = ref({
  id: 1,
  username: 'admin',
  real_name: '系统管理员',
  email: 'admin@itops.com',
  phone: '13800138000',
  department: 'IT部门',
  position: '系统管理员',
  avatar: '',
  bio: '负责系统运维和管理工作',
  roles: [
    { id: 1, name: '系统管理员', code: 'admin' }
  ],
  login_count: 156,
  created_at: '2024-01-01 09:00:00'
})

const securitySettings = ref({
  twoFactorAuth: false,
  ipRestriction: false
})

const preferences = ref({
  theme: 'light',
  language: 'zh-CN',
  emailNotification: true,
  browserNotification: false
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const logFilter = ref({
  type: '',
  dateRange: null as any
})

const loginDevices = ref([
  {
    id: 1,
    device_name: 'Chrome on Windows',
    ip_address: '192.168.1.100',
    last_login: '2024-01-15 14:30:00',
    is_current: true
  },
  {
    id: 2,
    device_name: 'Safari on macOS',
    ip_address: '192.168.1.105',
    last_login: '2024-01-14 09:15:00',
    is_current: false
  }
])

const activityLogs = ref([
  {
    id: 1,
    action: '登录系统',
    type: 'login',
    result: 'success',
    ip_address: '192.168.1.100',
    created_at: '2024-01-15 14:30:00'
  },
  {
    id: 2,
    action: '修改个人信息',
    type: 'update',
    result: 'success',
    ip_address: '192.168.1.100',
    created_at: '2024-01-15 13:20:00'
  }
])

const rules: FormRules = {
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const getDaysJoined = () => {
  const joinDate = new Date(profile.value.created_at)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - joinDate.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

const getRoleType = (code: string) => {
  const typeMap: Record<string, string> = {
    'admin': 'danger',
    'manager': 'warning',
    'user': 'info'
  }
  return typeMap[code] || 'info'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const getLogIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    'login': '🔑',
    'logout': '🚪',
    'update': '✏️',
    'delete': '🗑️'
  }
  return iconMap[type] || '📝'
}

const saveProfile = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('个人信息保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const changeAvatar = () => {
  ElMessage.info('头像上传功能开发中...')
}

const changePassword = () => {
  passwordDialogVisible.value = true
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
}

const submitPasswordChange = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (error) {
    console.error('密码修改失败:', error)
    ElMessage.error('密码修改失败，请重试')
  } finally {
    changingPassword.value = false
  }
}

const viewActivityLog = () => {
  activeTab.value = 'activity'
}

const downloadData = () => {
  ElMessage.info('数据导出功能开发中...')
}

const toggleTwoFactor = (value: boolean) => {
  ElMessage.info(`双因素认证已${value ? '启用' : '禁用'}`)
}

const toggleIpRestriction = (value: boolean) => {
  ElMessage.info(`IP访问限制已${value ? '启用' : '禁用'}`)
}

const logoutDevice = async (deviceId: number) => {
  try {
    await ElMessageBox.confirm('确定要下线此设备吗？', '确认操作', {
      type: 'warning'
    })
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    loginDevices.value = loginDevices.value.filter(device => device.id !== deviceId)
    ElMessage.success('设备已下线')
  } catch {
    // 用户取消
  }
}

const searchLogs = () => {
  ElMessage.info('查询操作记录...')
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.profile-page {
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

.header-content h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.page-content {
  padding: 24px;
}

.profile-card {
  margin-bottom: 24px;
}

.avatar-section {
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 20px;
}

.avatar-container {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f0f0f0;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  cursor: pointer;
  transition: opacity 0.3s;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.change-text {
  color: white;
  font-size: 12px;
}

.user-basic-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #303133;
}

.username {
  color: #909399;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.user-roles {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.stats-section {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.quick-actions-card {
  margin-bottom: 24px;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.action-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  cursor: pointer;
  transition: background 0.3s;
}

.action-item:hover {
  background: #e9ecef;
}

.action-icon {
  width: 20px;
  text-align: center;
  margin-right: 12px;
}

.action-text {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.action-arrow {
  color: #c0c4cc;
}

.profile-tabs {
  background: white;
  border-radius: 8px;
  padding: 24px;
}

.profile-form {
  margin-top: 20px;
}

.security-settings,
.preferences-settings {
  margin-top: 20px;
}

.setting-group {
  margin-bottom: 32px;
}

.setting-group h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f8f9fa;
}

.setting-content {
  flex: 1;
}

.setting-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 12px;
  color: #909399;
}

.device-list {
  margin-top: 16px;
}

.device-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.device-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.device-meta {
  font-size: 12px;
  color: #909399;
}

.device-meta span {
  margin-right: 12px;
}

.activity-log {
  margin-top: 20px;
}

.activity-filters {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.log-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.log-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: white;
  margin-right: 12px;
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
  font-size: 12px;
  color: #909399;
}

.log-meta span {
  margin-right: 12px;
}

.result-success {
  color: #67c23a;
}

.result-error {
  color: #f56c6c;
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
  
  .header-actions {
    margin-top: 12px;
    width: 100%;
  }
  
  .profile-tabs {
    padding: 16px;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>