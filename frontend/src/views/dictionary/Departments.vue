<template>
  <div class="departments-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>组织机构管理</h1>
      <div class="header-actions">
        <button @click="refreshData" class="btn btn-secondary">🔄 刷新</button>
        <button @click="showCreateDialog" class="btn btn-primary">➕ 新增部门</button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>关键词</label>
          <input v-model="searchParams.keyword" placeholder="搜索部门名称或编码" />
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="searchParams.status">
            <option value="">全部状态</option>
            <option value="1">启用</option>
            <option value="0">禁用</option>
          </select>
        </div>
        <button @click="searchData" class="btn btn-primary">🔍 搜索</button>
        <button @click="resetSearch" class="btn btn-secondary">🔄 重置</button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <div v-if="loading" class="loading">
        <div class="loading-spinner">🔄</div>
        <p>加载中...</p>
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th width="60">#</th>
            <th width="150">部门编码</th>
            <th>部门名称</th>
            <th>描述</th>
            <th width="120">上级部门</th>
            <th width="80">排序</th>
            <th width="80">状态</th>
            <th width="150">创建时间</th>
            <th width="200">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in departmentsList" :key="item.id">
            <td class="row-number">{{ index + 1 }}</td>
            <td class="dept-code">{{ item.code }}</td>
            <td class="dept-name">
              <div class="name-content">
                <span class="name">{{ item.name }}</span>
                <span v-if="item.parent_id" class="parent-indicator">子级</span>
              </div>
            </td>
            <td class="description">{{ item.description || '-' }}</td>
            <td>{{ getParentName(item.parent_id) }}</td>
            <td>{{ item.sort_order }}</td>
            <td>
              <span :class="`status-tag ${item.is_active ? 'status-active' : 'status-inactive'}`">
                {{ item.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ formatDate(item.created_at) }}</td>
            <td class="actions">
              <button @click="showEditDialog(item)" class="btn-sm btn-primary">编辑</button>
              <button @click="toggleStatus(item)" :class="`btn-sm ${item.is_active ? 'btn-warning' : 'btn-success'}`">
                {{ item.is_active ? '禁用' : '启用' }}
              </button>
              <button @click="confirmDelete(item)" class="btn-sm btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!loading && departmentsList.length === 0" class="no-data">
        <p>暂无数据</p>
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <div v-if="showDialog" class="modal-overlay" @click="hideDialog">
      <div class="modal-dialog" @click.stop>
        <div class="modal-header">
          <h3>{{ dialogTitle }}</h3>
          <button @click="hideDialog" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveItem" class="form">
            <div class="form-group">
              <label class="required">部门名称</label>
              <input
                v-model="formData.name"
                type="text"
                class="form-control"
                placeholder="请输入部门名称"
                maxlength="100"
                :class="{ error: errors.name }"
                required
              >
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label class="required">部门编码</label>
              <input
                v-model="formData.code"
                type="text"
                class="form-control"
                placeholder="请输入部门编码"
                maxlength="50"
                :class="{ error: errors.code }"
                required
              >
              <span v-if="errors.code" class="error-text">{{ errors.code }}</span>
            </div>

            <div class="form-group">
              <label>描述</label>
              <textarea
                v-model="formData.description"
                class="form-control"
                placeholder="请输入描述"
                rows="3"
                maxlength="255"
              ></textarea>
            </div>

            <div class="form-group">
              <label>上级部门</label>
              <select v-model="formData.parent_id" class="form-control">
                <option value="">无（顶级部门）</option>
                <option v-for="item in parentOptions" :key="item.id" :value="item.id">
                  {{ item.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>排序</label>
              <input
                v-model.number="formData.sort_order"
                type="number"
                class="form-control"
                placeholder="排序值，数字越小越靠前"
                min="0"
              >
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="formData.is_active" type="checkbox">
                <span>启用状态</span>
              </label>
            </div>

            <div class="form-actions">
              <button type="button" @click="hideDialog" class="btn btn-secondary">取消</button>
              <button type="submit" :disabled="submitting" class="btn btn-primary">
                {{ submitting ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { dictionaryApi, type Department } from '@/api/dictionary'
import { formatDate } from '@/utils/date'

// 响应式数据
const loading = ref(false)
const departmentsList = ref<Department[]>([])
const showDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)

// 搜索参数
const searchParams = reactive({
  keyword: '',
  status: ''
})

// 表单数据
const formData = reactive({
  id: 0,
  name: '',
  code: '',
  description: '',
  parent_id: null as number | null,
  sort_order: 0,
  is_active: true
})

// 表单验证错误
const errors = reactive({
  name: '',
  code: ''
})

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑组织机构' : '新增组织机构')

const parentOptions = computed(() => {
  return departmentsList.value.filter(item => 
    item.id !== formData.id && // 排除自己
    !item.parent_id // 只显示顶级部门作为父级选项
  )
})

// 获取父级名称
const getParentName = (parentId: number | null | undefined) => {
  if (!parentId) return '-'
  const parent = departmentsList.value.find(item => item.id === parentId)
  return parent ? parent.name : '-'
}

// 数据加载
const loadData = async () => {
  loading.value = true
  try {
    console.log('🔄 开始加载组织机构数据...')
    const response = await dictionaryApi.getDepartments()
    console.log('📋 API响应:', response)
    
    if (response.success && response.data) {
      departmentsList.value = response.data
      console.log('✅ 数据加载成功，条数:', response.data.length)
    } else {
      console.error('❌ API响应失败:', response)
      departmentsList.value = []
    }
  } catch (error) {
    console.error('❌ 加载组织机构失败:', error)
    departmentsList.value = []
    // 显示用户友好的错误信息
    alert('加载数据失败，请检查网络连接或重新登录')
  } finally {
    loading.value = false
  }
}

// 搜索
const searchData = () => {
  // 这里可以根据搜索参数过滤数据
  let filteredList = [...departmentsList.value]
  
  if (searchParams.keyword) {
    const keyword = searchParams.keyword.toLowerCase()
    filteredList = filteredList.filter(item =>
      item.name.toLowerCase().includes(keyword) ||
      item.code.toLowerCase().includes(keyword)
    )
  }
  
  if (searchParams.status !== '') {
    const isActive = searchParams.status === '1'
    filteredList = filteredList.filter(item => item.is_active === isActive)
  }
  
  // 注意：这里简化处理，实际应该在后端实现搜索
}

// 重置搜索
const resetSearch = () => {
  searchParams.keyword = ''
  searchParams.status = ''
  loadData()
}

// 刷新数据
const refreshData = () => {
  loadData()
}

// 显示新增对话框
const showCreateDialog = () => {
  isEdit.value = false
  resetFormData()
  clearErrors()
  showDialog.value = true
}

// 显示编辑对话框
const showEditDialog = (item: Department) => {
  isEdit.value = true
  Object.assign(formData, {
    id: item.id,
    name: item.name,
    code: item.code,
    description: item.description || '',
    parent_id: item.parent_id,
    sort_order: item.sort_order,
    is_active: item.is_active
  })
  clearErrors()
  showDialog.value = true
}

// 隐藏对话框
const hideDialog = () => {
  showDialog.value = false
  resetFormData()
  clearErrors()
}

// 重置表单数据
const resetFormData = () => {
  Object.assign(formData, {
    id: 0,
    name: '',
    code: '',
    description: '',
    parent_id: null,
    sort_order: 0,
    is_active: true
  })
}

// 清除错误
const clearErrors = () => {
  errors.name = ''
  errors.code = ''
}

// 表单验证
const validateForm = () => {
  clearErrors()
  let isValid = true

  if (!formData.name.trim()) {
    errors.name = '请输入部门名称'
    isValid = false
  }

  if (!formData.code.trim()) {
    errors.code = '请输入部门编码'
    isValid = false
  }

  return isValid
}

// 保存数据
const saveItem = async () => {
  if (!validateForm()) return

  submitting.value = true
  try {
    const data = {
      name: formData.name.trim(),
      code: formData.code.trim(),
      description: formData.description.trim(),
      parent_id: formData.parent_id,
      sort_order: formData.sort_order,
      is_active: formData.is_active
    }

    if (isEdit.value) {
      await dictionaryApi.updateDepartment(formData.id, data)
    } else {
      await dictionaryApi.createDepartment(data)
    }

    hideDialog()
    await loadData()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    submitting.value = false
  }
}

// 切换状态
const toggleStatus = async (item: Department) => {
  try {
    await dictionaryApi.updateDepartment(item.id, {
      ...item,
      is_active: !item.is_active
    })
    await loadData()
  } catch (error) {
    console.error('切换状态失败:', error)
  }
}

// 确认删除
const confirmDelete = (item: Department) => {
  if (confirm(`确定要删除部门"${item.name}"吗？`)) {
    deleteItem(item)
  }
}

// 删除数据
const deleteItem = async (item: Department) => {
  try {
    await dictionaryApi.deleteDepartment(item.id)
    await loadData()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.departments-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e1e8ed;
}

.page-header h1 {
  margin: 0;
  color: #1a202c;
  font-size: 24px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-form {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.search-row {
  display: flex;
  gap: 15px;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
  min-width: 120px;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.row-number {
  text-align: center;
  color: #6b7280;
}

.dept-code {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #374151;
}

.name-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.parent-indicator {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
}

.status-inactive {
  background: #fee2e2;
  color: #991b1b;
}

.actions {
  display: flex;
  gap: 5px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.loading-spinner {
  font-size: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-dialog {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1a202c;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #374151;
}

.required::after {
  content: '*';
  color: #ef4444;
  margin-left: 2px;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-control.error {
  border-color: #ef4444;
}

.error-text {
  color: #ef4444;
  font-size: 12px;
  margin-top: 2px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}
</style>