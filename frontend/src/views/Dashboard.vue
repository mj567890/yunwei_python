<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>IT运维综合管理系统 - 仪表盘</h1>
      <div class="user-info">
        <button @click="fetchStatistics" class="refresh-btn">🔄 刷新数据</button>
        <span>欢迎, {{ userInfo?.real_name || userInfo?.username || '用户' }}</span>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stats-card">
        <div class="stats-icon">📦</div>
        <div class="stats-content">
          <div class="stats-number">{{ loading ? '-' : dashboardData.assetStats.total }}</div>
          <div class="stats-label">总资产数</div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-icon">🌐</div>
        <div class="stats-content">
          <div class="stats-number">{{ loading ? '-' : dashboardData.deviceStats.total }}</div>
          <div class="stats-label">网络设备</div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-icon">🔧</div>
        <div class="stats-content">
          <div class="stats-number">{{ loading ? '-' : dashboardData.maintenanceStats.total }}</div>
          <div class="stats-label">运维记录</div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="stats-icon">⚠️</div>
        <div class="stats-content">
          <div class="stats-number">{{ loading ? '-' : dashboardData.faultStats.total }}</div>
          <div class="stats-label">故障记录</div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2>快速操作</h2>
      <div class="action-grid">
        <div class="action-card" @click="navigateTo('/app/assets/create')">
          <div class="action-icon">➕</div>
          <div class="action-title">新增资产</div>
        </div>
        
        <div class="action-card" @click="navigateTo('/app/network/devices/create')">
          <div class="action-icon">🖥️</div>
          <div class="action-title">新增设备</div>
        </div>
        
        <div class="action-card" @click="navigateTo('/app/maintenance/create')">
          <div class="action-icon">📋</div>
          <div class="action-title">新增运维</div>
        </div>
        
        <div class="action-card" @click="navigateTo('/app/faults/create')">
          <div class="action-icon">🚨</div>
          <div class="action-title">报告故障</div>
        </div>
        
        <div class="action-card" @click="navigateTo('/app/assets')">
          <div class="action-icon">📦</div>
          <div class="action-title">资产管理</div>
        </div>
        
        <div class="action-card" @click="navigateTo('/app/network/devices')">
          <div class="action-icon">🌐</div>
          <div class="action-title">设备列表</div>
        </div>
        
        <div class="action-card" @click="navigateTo('/app/maintenance')">
          <div class="action-icon">🔧</div>
          <div class="action-title">运维记录</div>
        </div>
        
        <div class="action-card" @click="navigateTo('/app/faults')">
          <div class="action-icon">⚠️</div>
          <div class="action-title">故障管理</div>
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activities">
      <h2>最近活动</h2>
      <div class="activity-list">
        <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
          <div class="activity-icon">{{ activity.icon }}</div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-time">{{ activity.time }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { request } from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()

const userInfo = ref(userStore.userInfo)
const loading = ref(true)

// 真实的仪表盘数据
const dashboardData = ref({
  assetStats: { total: 0 },
  deviceStats: { total: 0 },
  maintenanceStats: { total: 0 },
  faultStats: { total: 0 }
})

// 获取统计数据
const fetchStatistics = async () => {
  try {
    loading.value = true
    
    // 强制清理缓存，添加时间戳参数
    const timestamp = new Date().getTime()
    const apiUrl = `/api/statistics/overview?t=${timestamp}`
    
    console.log('🚀 正在调用API:', apiUrl)
    console.log('🚀 当前baseURL配置:', (request as any).baseURL || '空字符串（使用Vite代理）')
    console.log('🚀 实际请求URL:', `${(request as any).baseURL || ''}${apiUrl}`)
    
    const response = await request.get(apiUrl)
    console.log('📊 API响应:', response)
    
    if (response.success && response.data) {
      const apiData = response.data
      console.log('📊 解析的数据:', apiData)
      
      const newDashboardData = {
        assetStats: { total: apiData.total_assets || 0 },
        deviceStats: { total: apiData.device_count || 0 },
        maintenanceStats: { total: apiData.maintenance_count || 0 },
        faultStats: { total: apiData.fault_count || 0 }
      }
      
      console.log('📊 即将设置的仪表盘数据:', newDashboardData)
      
      // 强制更新数据
      dashboardData.value = newDashboardData
      
      console.log('🎉 仪表盘数据更新完成:', dashboardData.value)
      
      // 强制重渲染
      await nextTick()
      
    } else {
      console.error('❌ API响应没有success或data字段:', response)
    }
  } catch (error) {
    console.error('❌ 获取统计数据失败:', error)
    console.error('❌ 错误详情:', (error as Error).stack || error)
    
    // 设置默认值
    dashboardData.value = {
      assetStats: { total: 0 },
      deviceStats: { total: 0 },
      maintenanceStats: { total: 0 },
      faultStats: { total: 0 }
    }
  } finally {
    loading.value = false
    console.log('🏁 加载状态结束')
  }
}
const recentActivities = [
  {
    id: 1,
    icon: '📦',
    title: '新增服务器资产 - Dell R740',
    time: '2024-01-15 14:30'
  },
  {
    id: 2,
    icon: '🔧',
    title: '完成机房设备巡检',
    time: '2024-01-15 10:15'
  },
  {
    id: 3,
    icon: '⚠️',
    title: '网络设备故障已修复',
    time: '2024-01-14 16:45'
  },
  {
    id: 4,
    icon: '📊',
    title: '生成月度运维报告',
    time: '2024-01-14 09:00'
  }
]

// 导航函数
const navigateTo = (path: string) => {
  console.log('导航到:', path)
  router.push(path)
}

// 退出登录
const handleLogout = async () => {
  try {
    await userStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}

// 初始化用户状态和获取数据
onMounted(async () => {
  userInfo.value = userStore.userInfo
  await fetchStatistics()
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 20px 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.dashboard-header h1 {
  font-size: 24px;
  color: #303133;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info span {
  color: #606266;
  font-size: 14px;
}

.logout-btn {
  padding: 8px 16px;
  background: #f56565;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: #e53e3e;
}

.refresh-btn {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
  margin-right: 10px;
}

.refresh-btn:hover {
  background: #337ecc;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stats-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stats-icon {
  font-size: 48px;
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  opacity: 0.9;
}

.quick-actions {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.quick-actions h2 {
  margin: 0 0 20px 0;
  color: #303133;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
}

.action-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.action-card:hover {
  background: #e3f2fd;
  border-color: #409eff;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.action-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.recent-activities {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.recent-activities h2 {
  margin: 0 0 20px 0;
  color: #303133;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.activity-icon {
  font-size: 24px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 5px;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 15px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>