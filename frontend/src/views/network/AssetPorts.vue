<template>
  <div class="asset-ports">
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="back-btn">← 返回</button>
        <div class="device-info">
          <h1>{{ asset?.name }} - 端口管理</h1>
          <span class="device-category" v-if="asset?.category">{{ asset?.category }}</span>
        </div>
      </div>
    </div>

    <!-- 端口管理组件 -->
    <PortManager 
      v-if="assetId" 
      :asset-id="assetId"
      @port-created="handlePortCreated"
      @port-updated="handlePortUpdated"
      @port-deleted="handlePortDeleted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { assetApi, type Asset } from '@/api/asset'
import PortManager from '@/components/network/PortManager.vue'

const route = useRoute()
const router = useRouter()

// 数据
const asset = ref<Asset | null>(null)

// 计算属性
const assetId = computed(() => {
  const id = route.params.assetId
  return typeof id === 'string' ? parseInt(id) : 0
})

// 加载资产信息
const loadAsset = async () => {
  if (!assetId.value) return
  
  try {
    const response = await assetApi.getAsset(assetId.value)
    if (response.success) {
      asset.value = response.data
    }
  } catch (error) {
    console.error('加载资产信息失败:', error)
  }
}

// 返回
const goBack = () => {
  router.push('/app/network/ports')
}

// 事件处理
const handlePortCreated = () => {
  // PortManager组件会自动刷新
}

const handlePortUpdated = () => {
  // PortManager组件会自动刷新
}

const handlePortDeleted = () => {
  // PortManager组件会自动刷新
}

onMounted(() => {
  loadAsset()
})
</script>

<style scoped>
.asset-ports {
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

.back-btn {
  background: #f0f2f5;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: #606266;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #e6e8eb;
  color: #409eff;
}

.device-info h1 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 20px;
}

.device-category {
  color: #909399;
  font-size: 14px;
  font-weight: 400;
  opacity: 0.8;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary { background: #409eff; color: white; }
.btn-secondary { background: #909399; color: white; }
.btn-info { background: #17a2b8; color: white; }

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 700px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.modal-header h3 {
  margin: 0;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #909399;
}

.modal-body {
  padding: 24px;
}

.batch-options {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.option-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.preset-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.preset-btn {
  background: #f8f9fa;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.preset-btn:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.custom-batch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.custom-batch .btn {
  grid-column: 1 / -1;
  justify-self: start;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input,
.form-group select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
}

@media (max-width: 768px) {
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
  }
  
  .custom-batch {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 90%;
    margin: 20px;
  }
}
</style>