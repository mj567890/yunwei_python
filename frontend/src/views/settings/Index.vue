<template>
  <div class="settings-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>系统设置</h1>
      <div class="header-actions">
        <button @click="saveAllSettings" class="btn btn-primary">💾 保存设置</button>
        <button @click="resetToDefault" class="btn btn-secondary">🔄 恢复默认</button>
      </div>
    </div>

    <!-- 设置导航 -->
    <div class="settings-nav">
      <div class="nav-tabs">
        <div 
          v-for="tab in tabs" 
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="['nav-tab', { active: activeTab === tab.key }]"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-name">{{ tab.name }}</span>
        </div>
      </div>
    </div>

    <!-- 设置内容 -->
    <div class="settings-content">
      <!-- 基本设置 -->
      <div v-if="activeTab === 'basic'" class="setting-section">
        <div class="section-header">
          <h2>⚙️ 基本设置</h2>
          <p>系统基本配置信息</p>
        </div>
        
        <div class="setting-form">
          <div class="form-group">
            <label>系统名称</label>
            <input v-model="settings.basic.systemName" placeholder="请输入系统名称" />
            <small>显示在页面标题和登录页面的系统名称</small>
          </div>
          
          <div class="form-group">
            <label>系统版本</label>
            <input v-model="settings.basic.version" placeholder="请输入版本号" />
            <small>当前系统版本号</small>
          </div>
          
          <div class="form-group">
            <label>公司名称</label>
            <input v-model="settings.basic.companyName" placeholder="请输入公司名称" />
          </div>
          
          <div class="form-group">
            <label>系统描述</label>
            <textarea v-model="settings.basic.description" rows="3" placeholder="请输入系统描述"></textarea>
          </div>
          
          <div class="form-group">
            <label>时区设置</label>
            <select v-model="settings.basic.timezone">
              <option value="Asia/Shanghai">Asia/Shanghai (北京时间)</option>
              <option value="UTC">UTC (协调世界时)</option>
              <option value="America/New_York">America/New_York (纽约时间)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>语言设置</label>
            <select v-model="settings.basic.language">
              <option value="zh-CN">简体中文</option>
              <option value="en-US">English</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 安全设置 -->
      <div v-if="activeTab === 'security'" class="setting-section">
        <div class="section-header">
          <h2>🔒 安全设置</h2>
          <p>系统安全相关配置</p>
        </div>
        
        <div class="setting-form">
          <div class="form-group">
            <label>登录超时时间（分钟）</label>
            <input v-model.number="settings.security.sessionTimeout" type="number" min="5" max="1440" />
            <small>用户无操作自动登出时间</small>
          </div>
          
          <div class="form-group">
            <label>密码最小长度</label>
            <input v-model.number="settings.security.passwordMinLength" type="number" min="6" max="20" />
          </div>
          
          <div class="form-group checkbox-group">
            <label>
              <input v-model="settings.security.requireComplexPassword" type="checkbox" />
              <span>要求复杂密码（包含大小写字母、数字和特殊字符）</span>
            </label>
          </div>
          
          <div class="form-group">
            <label>最大登录失败次数</label>
            <input v-model.number="settings.security.maxLoginAttempts" type="number" min="3" max="10" />
            <small>达到次数后将锁定账户</small>
          </div>
          
          <div class="form-group">
            <label>账户锁定时间（分钟）</label>
            <input v-model.number="settings.security.lockoutDuration" type="number" min="5" max="1440" />
          </div>
          
          <div class="form-group checkbox-group">
            <label>
              <input v-model="settings.security.enableApiRateLimit" type="checkbox" />
              <span>启用API频率限制</span>
            </label>
          </div>
          
          <div class="form-group checkbox-group">
            <label>
              <input v-model="settings.security.enableAuditLog" type="checkbox" />
              <span>启用操作审计日志</span>
            </label>
          </div>
        </div>
      </div>

      <!-- 邮件设置 -->
      <div v-if="activeTab === 'email'" class="setting-section">
        <div class="section-header">
          <h2>📧 邮件设置</h2>
          <p>系统邮件发送配置</p>
        </div>
        
        <div class="setting-form">
          <div class="form-group checkbox-group">
            <label>
              <input v-model="settings.email.enabled" type="checkbox" />
              <span>启用邮件功能</span>
            </label>
          </div>
          
          <div v-if="settings.email.enabled">
            <div class="form-group">
              <label>SMTP服务器</label>
              <input v-model="settings.email.smtpHost" placeholder="smtp.example.com" />
            </div>
            
            <div class="form-group">
              <label>SMTP端口</label>
              <input v-model.number="settings.email.smtpPort" type="number" placeholder="587" />
            </div>
            
            <div class="form-group">
              <label>发送邮箱</label>
              <input v-model="settings.email.fromEmail" type="email" placeholder="noreply@example.com" />
            </div>
            
            <div class="form-group">
              <label>邮箱密码</label>
              <input v-model="settings.email.password" type="password" placeholder="请输入邮箱密码" />
            </div>
            
            <div class="form-group checkbox-group">
              <label>
                <input v-model="settings.email.useTLS" type="checkbox" />
                <span>使用TLS加密</span>
              </label>
            </div>
            
            <div class="form-group">
              <button @click="testEmail" class="btn btn-info">📧 发送测试邮件</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 备份设置 -->
      <div v-if="activeTab === 'backup'" class="setting-section">
        <div class="section-header">
          <h2>💾 备份设置</h2>
          <p>数据备份相关配置</p>
        </div>
        
        <div class="setting-form">
          <div class="form-group checkbox-group">
            <label>
              <input v-model="settings.backup.autoBackup" type="checkbox" />
              <span>启用自动备份</span>
            </label>
          </div>
          
          <div v-if="settings.backup.autoBackup">
            <div class="form-group">
              <label>备份频率</label>
              <select v-model="settings.backup.frequency">
                <option value="daily">每日</option>
                <option value="weekly">每周</option>
                <option value="monthly">每月</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>备份时间</label>
              <input v-model="settings.backup.backupTime" type="time" />
            </div>
            
            <div class="form-group">
              <label>保留备份数量</label>
              <input v-model.number="settings.backup.keepCount" type="number" min="1" max="30" />
              <small>超过数量的旧备份将被自动删除</small>
            </div>
          </div>
          
          <div class="backup-actions">
            <button @click="createBackup" class="btn btn-primary">💾 立即备份</button>
            <button @click="restoreBackup" class="btn btn-warning">🔄 恢复备份</button>
            <button @click="downloadBackup" class="btn btn-info">📥 下载备份</button>
          </div>
          
          <div class="backup-list">
            <h3>备份历史</h3>
            <div class="backup-item" v-for="backup in backupList" :key="backup.id">
              <div class="backup-info">
                <div class="backup-name">{{ backup.name }}</div>
                <div class="backup-meta">
                  <span class="backup-size">{{ backup.size }}</span>
                  <span class="backup-date">{{ backup.date }}</span>
                </div>
              </div>
              <div class="backup-actions">
                <button @click="downloadBackupFile(backup)" class="btn-sm btn-info">下载</button>
                <button @click="deleteBackup(backup)" class="btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统信息 -->
      <div v-if="activeTab === 'system'" class="setting-section">
        <div class="section-header">
          <h2>ℹ️ 系统信息</h2>
          <p>当前系统运行状态信息</p>
        </div>
        
        <div class="system-info">
          <div class="info-cards">
            <div class="info-card">
              <div class="card-header">
                <span class="card-icon">🖥️</span>
                <span class="card-title">系统版本</span>
              </div>
              <div class="card-content">
                <div class="info-item">
                  <span class="label">应用版本:</span>
                  <span class="value">{{ systemInfo.appVersion }}</span>
                </div>
                <div class="info-item">
                  <span class="label">构建时间:</span>
                  <span class="value">{{ systemInfo.buildTime }}</span>
                </div>
              </div>
            </div>
            
            <div class="info-card">
              <div class="card-header">
                <span class="card-icon">⚡</span>
                <span class="card-title">运行状态</span>
              </div>
              <div class="card-content">
                <div class="info-item">
                  <span class="label">运行时间:</span>
                  <span class="value">{{ systemInfo.uptime }}</span>
                </div>
                <div class="info-item">
                  <span class="label">当前用户:</span>
                  <span class="value">{{ systemInfo.currentUsers }}</span>
                </div>
              </div>
            </div>
            
            <div class="info-card">
              <div class="card-header">
                <span class="card-icon">💾</span>
                <span class="card-title">存储信息</span>
              </div>
              <div class="card-content">
                <div class="info-item">
                  <span class="label">数据库大小:</span>
                  <span class="value">{{ systemInfo.dbSize }}</span>
                </div>
                <div class="info-item">
                  <span class="label">文件存储:</span>
                  <span class="value">{{ systemInfo.fileSize }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// 标签页配置
const activeTab = ref('basic')
const tabs = [
  { key: 'basic', name: '基本设置', icon: '⚙️' },
  { key: 'security', name: '安全设置', icon: '🔒' },
  { key: 'email', name: '邮件设置', icon: '📧' },
  { key: 'backup', name: '备份设置', icon: '💾' },
  { key: 'system', name: '系统信息', icon: 'ℹ️' }
]

// 设置数据
const settings = reactive({
  basic: {
    systemName: 'IT运维综合管理系统',
    version: '1.0.0',
    companyName: '示例公司',
    description: '企业级IT运维管理平台',
    timezone: 'Asia/Shanghai',
    language: 'zh-CN'
  },
  security: {
    sessionTimeout: 30,
    passwordMinLength: 6,
    requireComplexPassword: true,
    maxLoginAttempts: 5,
    lockoutDuration: 30,
    enableApiRateLimit: true,
    enableAuditLog: true
  },
  email: {
    enabled: false,
    smtpHost: '',
    smtpPort: 587,
    fromEmail: '',
    password: '',
    useTLS: true
  },
  backup: {
    autoBackup: true,
    frequency: 'daily',
    backupTime: '02:00',
    keepCount: 7
  }
})

// 系统信息
const systemInfo = reactive({
  appVersion: '1.0.0',
  buildTime: '2024-01-15 14:30:00',
  uptime: '15天 6小时 32分钟',
  currentUsers: 8,
  dbSize: '156.7 MB',
  fileSize: '2.3 GB'
})

// 备份列表
const backupList = ref([
  {
    id: 1,
    name: 'backup_20240115_020000.sql',
    size: '145.2 MB',
    date: '2024-01-15 02:00:00'
  },
  {
    id: 2,
    name: 'backup_20240114_020000.sql',
    size: '144.8 MB',
    date: '2024-01-14 02:00:00'
  },
  {
    id: 3,
    name: 'backup_20240113_020000.sql',
    size: '143.9 MB',
    date: '2024-01-13 02:00:00'
  }
])

// 事件处理
const saveAllSettings = async () => {
  try {
    // 这里应该调用保存设置的API
    console.log('保存设置:', settings)
    alert('设置保存成功！')
  } catch (error) {
    console.error('保存设置失败:', error)
    alert('保存设置失败，请重试')
  }
}

const resetToDefault = () => {
  if (confirm('确认恢复所有设置为默认值吗？')) {
    // 恢复默认设置
    console.log('恢复默认设置')
    alert('设置已恢复为默认值')
  }
}

const testEmail = async () => {
  try {
    // 这里应该调用发送测试邮件的API
    console.log('发送测试邮件')
    alert('测试邮件发送成功！请查收邮箱')
  } catch (error) {
    console.error('发送测试邮件失败:', error)
    alert('测试邮件发送失败，请检查邮件配置')
  }
}

const createBackup = async () => {
  try {
    // 这里应该调用创建备份的API
    console.log('创建备份')
    alert('备份创建成功！')
  } catch (error) {
    console.error('创建备份失败:', error)
    alert('备份创建失败，请重试')
  }
}

const restoreBackup = () => {
  if (confirm('确认要恢复备份吗？这将覆盖当前数据！')) {
    console.log('恢复备份')
    alert('备份恢复功能暂未实现')
  }
}

const downloadBackup = () => {
  console.log('下载最新备份')
  alert('下载功能暂未实现')
}

const downloadBackupFile = (backup: any) => {
  console.log('下载备份文件:', backup.name)
  alert(`下载 ${backup.name}`)
}

const deleteBackup = (backup: any) => {
  if (confirm(`确认删除备份文件 "${backup.name}" 吗？`)) {
    const index = backupList.value.findIndex(item => item.id === backup.id)
    if (index > -1) {
      backupList.value.splice(index, 1)
      console.log('删除备份成功')
    }
  }
}
</script>

<style scoped>
.settings-container {
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

.settings-nav {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
}

.nav-tabs {
  display: flex;
  border-bottom: 1px solid #ebeef5;
}

.nav-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.2s;
  color: #606266;
  border-bottom: 3px solid transparent;
}

.nav-tab:hover {
  background: #f5f7fa;
  color: #303133;
}

.nav-tab.active {
  color: #409eff;
  border-bottom-color: #409eff;
  background: rgba(64, 158, 255, 0.05);
}

.tab-icon {
  font-size: 18px;
}

.tab-name {
  font-weight: 500;
}

.settings-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.setting-section {
  max-width: 800px;
}

.section-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.section-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
}

.section-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.setting-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #409eff;
}

.form-group small {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin: 0;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.backup-actions {
  display: flex;
  gap: 12px;
  margin: 24px 0;
}

.backup-list {
  border-top: 1px solid #ebeef5;
  padding-top: 24px;
}

.backup-list h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.backup-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.backup-info .backup-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.backup-info .backup-meta {
  font-size: 12px;
  color: #909399;
}

.backup-meta span {
  margin-right: 16px;
}

.backup-actions {
  display: flex;
  gap: 8px;
  margin: 0;
}

.system-info {
  width: 100%;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-card {
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: #409eff;
  color: white;
}

.card-icon {
  font-size: 20px;
}

.card-title {
  font-weight: 500;
  font-size: 16px;
}

.card-content {
  padding: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #606266;
  font-size: 14px;
}

.info-item .value {
  font-weight: 500;
  color: #303133;
  font-family: monospace;
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
}

.btn-primary { background: #409eff; color: white; }
.btn-primary:hover { background: #66b1ff; }

.btn-secondary { background: #909399; color: white; }
.btn-secondary:hover { background: #a6a9ad; }

.btn-info { background: #17a2b8; color: white; }
.btn-info:hover { background: #138496; }

.btn-warning { background: #e6a23c; color: white; }
.btn-warning:hover { background: #ebb563; }

.btn-danger { background: #f56c6c; color: white; }
.btn-danger:hover { background: #f78989; }

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
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
  
  .nav-tabs {
    flex-direction: column;
  }
  
  .nav-tab {
    justify-content: flex-start;
    border-bottom: 1px solid #ebeef5;
    border-right: none;
  }
  
  .nav-tab.active {
    border-bottom-color: #ebeef5;
    border-left: 3px solid #409eff;
  }
  
  .settings-content {
    padding: 20px;
  }
  
  .info-cards {
    grid-template-columns: 1fr;
  }
  
  .backup-item {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .backup-actions {
    justify-content: center;
  }
}
</style>