<template>
  <div class="category-management">
    <div class="page-header">
      <h1>类别管理</h1>
      <div class="header-actions">
        <button @click="showCreateDialog = true" class="btn btn-primary">
          ➕ 新增类别
        </button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>类别名称</label>
          <input v-model="searchParams.name" placeholder="请输入类别名称" @keyup.enter="loadCategories" />
        </div>
        <div class="form-group">
          <label>类别类型</label>
          <select v-model="searchParams.type" @change="loadCategories">
            <option value="">全部</option>
            <option value="network">网络设备</option>
            <option value="general">一般设备</option>
          </select>
        </div>
        <div class="form-group button-group">
          <button @click="loadCategories" class="btn btn-primary">🔍 搜索</button>
          <button @click="resetSearch" class="btn btn-info">🔄 重置</button>
        </div>
      </div>
    </div>

    <!-- 类别表格 -->
    <div class="table-container">
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>数据加载中...</p>
      </div>
      
      <table v-else class="category-table">
        <thead>
          <tr>
            <th width="60">序号</th>
            <th width="120">类别编码</th>
            <th width="150">类别名称</th>
            <th width="200">描述</th>
            <th width="80">排序</th>
            <th width="100">网络设备</th>
            <th width="100">拓扑显示</th>
            <th width="100">终端设备</th>
            <th width="80">默认端口</th>
            <th width="60">图标</th>
            <th width="80">颜色</th>
            <th width="160">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(category, index) in categories" :key="category.id">
            <td class="row-number">{{ index + 1 }}</td>
            <td>{{ category.code }}</td>
            <td>{{ category.name }}</td>
            <td>{{ category.description || '-' }}</td>
            <td>{{ category.sort_order }}</td>
            <td>
              <span :class="`status-tag ${category.is_network_device ? 'status-success' : 'status-info'}`">
                {{ category.is_network_device ? '是' : '否' }}
              </span>
            </td>
            <td>
              <span :class="`status-tag ${category.can_topology ? 'status-success' : 'status-info'}`">
                {{ category.can_topology ? '是' : '否' }}
              </span>
            </td>
            <td>
              <span :class="`status-tag ${category.is_terminal ? 'status-success' : 'status-info'}`">
                {{ category.is_terminal ? '是' : '否' }}
              </span>
            </td>
            <td>{{ category.default_port_count || 0 }}</td>
            <td class="icon-cell">{{ category.device_icon }}</td>
            <td>
              <div class="color-indicator" :style="`background-color: ${category.device_color}`"></div>
            </td>
            <td class="actions">
              <button @click="editCategory(category)" class="btn-sm btn-primary">编辑</button>
              <button @click="deleteCategory(category)" class="btn-sm btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 空状态 -->
      <div v-if="!loading && categories.length === 0" class="empty-state">
        <div class="empty-icon">📂</div>
        <p>暂无类别数据</p>
        <button @click="showCreateDialog = true" class="btn btn-primary">添加第一个类别</button>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <div v-if="showCreateDialog || showEditDialog" class="modal-overlay" @click="closeDialogs">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑类别' : '新增类别' }}</h3>
          <button @click="closeDialogs" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveCategory">
            <div class="form-row">
              <div class="form-group">
                <label>类别名称 <span class="required">*</span></label>
                <input v-model="formData.name" required placeholder="请输入类别名称" />
              </div>
              <div class="form-group">
                <label>类别编码 <span class="required">*</span></label>
                <input v-model="formData.code" required placeholder="请输入类别编码" :disabled="isEditing" />
              </div>
            </div>
            
            <div class="form-group">
              <label>描述</label>
              <textarea v-model="formData.description" placeholder="请输入类别描述" rows="3"></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>排序权重</label>
                <input v-model.number="formData.sort_order" type="number" min="0" placeholder="0" />
              </div>
              <div class="form-group">
                <label>默认端口数</label>
                <input v-model.number="formData.default_port_count" type="number" min="0" placeholder="0" />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>设备图标</label>
                <input v-model="formData.device_icon" placeholder="📦" />
              </div>
              <div class="form-group">
                <label>设备颜色</label>
                <input v-model="formData.device_color" type="color" />
              </div>
            </div>
            
            <div class="form-section">
              <h4>设备特性</h4>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input v-model="formData.is_network_device" type="checkbox" />
                  <span>网络设备</span>
                  <small>在网络设备列表中显示</small>
                </label>
                <label class="checkbox-item">
                  <input v-model="formData.can_topology" type="checkbox" />
                  <span>拓扑显示</span>
                  <small>可在网络拓扑图中显示</small>
                </label>
                <label class="checkbox-item">
                  <input v-model="formData.is_terminal" type="checkbox" />
                  <span>终端设备</span>
                  <small>终端设备（如PC、笔记本等）</small>
                </label>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button @click="closeDialogs" class="btn btn-secondary">取消</button>
          <button @click="saveCategory" :disabled="saving" class="btn btn-primary">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { request } from '@/utils/request'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const categories = ref<any[]>([])
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const isEditing = ref(false)
const currentCategory = ref<any>(null)

// 搜索参数
const searchParams = reactive({
  name: '',
  type: ''
})

// 表单数据
const formData = reactive({
  name: '',
  code: '',
  description: '',
  sort_order: 0,
  is_network_device: false,
  can_topology: false,
  is_terminal: false,
  default_port_count: 0,
  device_icon: '📦',
  device_color: '#606266'
})

// 加载类别列表
const loadCategories = async () => {
  loading.value = true
  try {
    const params: any = {}
    
    if (searchParams.type === 'network') {
      params.network_only = 'true'
    }
    
    const response = await request.get('/api/categories', params)  // 使用完整API路径
    
    if (response.success) {
      let data = response.data
      
      // 如果有名称搜索，前端过滤
      if (searchParams.name) {
        data = data.filter((item: any) => 
          item.name.toLowerCase().includes(searchParams.name.toLowerCase())
        )
      }
      
      // 如果是一般设备过滤
      if (searchParams.type === 'general') {
        data = data.filter((item: any) => !item.is_network_device)
      }
      
      categories.value = data
    }
  } catch (error) {
    console.error('加载类别列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchParams.name = ''
  searchParams.type = ''
  loadCategories()
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    code: '',
    description: '',
    sort_order: 0,
    is_network_device: false,
    can_topology: false,
    is_terminal: false,
    default_port_count: 0,
    device_icon: '📦',
    device_color: '#606266'
  })
}

// 编辑类别
const editCategory = (category: any) => {
  currentCategory.value = category
  isEditing.value = true
  Object.assign(formData, {
    name: category.name,
    code: category.code,
    description: category.description || '',
    sort_order: category.sort_order || 0,
    is_network_device: category.is_network_device,
    can_topology: category.can_topology,
    is_terminal: category.is_terminal,
    default_port_count: category.default_port_count || 0,
    device_icon: category.device_icon || '📦',
    device_color: category.device_color || '#606266'
  })
  showEditDialog.value = true
}

// 删除类别
const deleteCategory = async (category: any) => {
  if (!confirm(`确认删除类别 "${category.name}" 吗？`)) {
    return
  }
  
  try {
    const response = await request.delete(`/api/categories/${category.id}`)  // 使用完整API路径
    if (response.success) {
      await loadCategories()
      console.log('删除成功')
    }
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 保存类别
const saveCategory = async () => {
  if (!formData.name || !formData.code) {
    alert('请填写类别名称和编码')
    return
  }
  
  saving.value = true
  try {
    let response
    if (isEditing.value) {
      response = await request.put(`/api/categories/${currentCategory.value.id}`, formData)  // 使用完整API路径
    } else {
      response = await request.post('/api/categories', formData)  // 使用完整API路径
    }
    
    if (response.success) {
      closeDialogs()
      await loadCategories()
      console.log(`${isEditing.value ? '更新' : '创建'}成功`)
    }
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const closeDialogs = () => {
  showCreateDialog.value = false
  showEditDialog.value = false
  isEditing.value = false
  currentCategory.value = null
  resetForm()
}

// 初始化
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.category-management {
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

.page-header h1 {
  margin: 0;
  color: #303133;
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
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
}

.button-group {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.category-table {
  width: 100%;
  border-collapse: collapse;
}

.category-table th,
.category-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.category-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.category-table tbody tr:hover {
  background: #f8f9fa;
}

.row-number {
  text-align: center;
  color: #909399;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-success {
  background: #f0f9ff;
  color: #67c23a;
}

.status-info {
  background: #f4f4f5;
  color: #909399;
}

.icon-cell {
  text-align: center;
  font-size: 18px;
}

.color-indicator {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-danger {
  background: #f56c6c;
  color: white;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

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
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
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

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
}

.required {
  color: #f56c6c;
}

.form-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.form-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
}

.checkbox-item input {
  margin-top: 2px;
}

.checkbox-item span {
  font-weight: 500;
  color: #303133;
}

.checkbox-item small {
  display: block;
  color: #909399;
  font-size: 12px;
  margin-top: 2px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #ebeef5;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #f4f4f5;
  color: #606266;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>