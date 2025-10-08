<template>
  <div class="asset-index-page">
    <div class="page-header">
      <div class="header-content">
        <h2>资产管理</h2>
        <div class="header-actions">
          <el-button type="primary" @click="createAsset" icon="Plus">
            新增资产
          </el-button>
          <el-button @click="exportAssets" icon="Download">
            导出资产
          </el-button>
        </div>
      </div>
    </div>

    <div class="page-content">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-content">
            <div class="stat-value">{{ totalAssets }}</div>
            <div class="stat-label">总资产数</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ activeAssets }}</div>
            <div class="stat-label">在用资产</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🔧</div>
          <div class="stat-content">
            <div class="stat-value">{{ maintenanceAssets }}</div>
            <div class="stat-label">维护中</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">❌</div>
          <div class="stat-content">
            <div class="stat-value">{{ retiredAssets }}</div>
            <div class="stat-label">已报废</div>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="quick-actions">
        <h3>快速操作</h3>
        <div class="action-grid">
          <div class="action-card" @click="goToAssetList">
            <div class="action-icon">📋</div>
            <div class="action-title">资产列表</div>
            <div class="action-desc">查看和管理所有资产</div>
          </div>
          
          <div class="action-card" @click="createAsset">
            <div class="action-icon">➕</div>
            <div class="action-title">新增资产</div>
            <div class="action-desc">添加新的资产记录</div>
          </div>
          
          <div class="action-card" @click="assetSearch">
            <div class="action-icon">🔍</div>
            <div class="action-title">资产查询</div>
            <div class="action-desc">按条件搜索资产</div>
          </div>
          
          <div class="action-card" @click="assetReport">
            <div class="action-icon">📊</div>
            <div class="action-title">资产报表</div>
            <div class="action-desc">生成资产统计报表</div>
          </div>
        </div>
      </div>

      <!-- 最近操作 -->
      <div class="recent-activities">
        <h3>最近操作</h3>
        <div class="activity-list">
          <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon">{{ activity.icon }}</div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-desc">{{ activity.description }}</div>
              <div class="activity-time">{{ formatDate(activity.created_at) }}</div>
            </div>
            <div class="activity-action">
              <el-button size="small" text @click="viewActivity(activity.id)">
                查看详情
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const totalAssets = ref(0)
const activeAssets = ref(0)
const maintenanceAssets = ref(0)
const retiredAssets = ref(0)

const recentActivities = ref([
  {
    id: 1,
    icon: '➕',
    title: '新增服务器',
    description: '张三 新增了 Dell PowerEdge R740 服务器',
    created_at: '2024-01-15 14:30:00'
  },
  {
    id: 2,
    icon: '🔧',
    title: '资产维护',
    description: '李四 对 HP ProLiant DL380 进行维护',
    created_at: '2024-01-15 13:15:00'
  },
  {
    id: 3,
    icon: '📦',
    title: '资产入库',
    description: '王五 将 10台笔记本电脑 入库',
    created_at: '2024-01-15 11:20:00'
  }
])

const loadStats = async () => {
  try {
    // 模拟API调用
    totalAssets.value = 1250
    activeAssets.value = 1080
    maintenanceAssets.value = 85
    retiredAssets.value = 85
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const createAsset = () => {
  router.push('/app/assets/create')
}

const goToAssetList = () => {
  router.push('/app/assets/list')
}

const exportAssets = () => {
  ElMessage.info('正在导出资产数据...')
  // 模拟导出
  setTimeout(() => {
    ElMessage.success('资产数据导出完成')
  }, 2000)
}

const assetSearch = () => {
  router.push('/app/assets/list?tab=search')
}

const assetReport = () => {
  ElMessage.info('资产报表功能开发中...')
}

const viewActivity = (id: number) => {
  ElMessage.info('查看活动详情功能开发中...')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.asset-index-page {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #f0f2f5;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.quick-actions h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-card {
  padding: 20px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.action-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.action-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.action-desc {
  font-size: 12px;
  color: #909399;
}

.recent-activities {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.recent-activities h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.activity-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #f0f2f5;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.activity-desc {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: #909399;
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
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-item {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
}
</style>