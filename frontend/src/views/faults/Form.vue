<template>
  <div class="fault-form-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="btn btn-secondary">← 返回</button>
        <div class="title-info">
          <h1>{{ isEdit ? '编辑故障' : '新建故障' }}</h1>
          <div v-if="isEdit && form.fault_code" class="fault-code">{{ form.fault_code }}</div>
        </div>
      </div>
      <div class="header-actions">
        <button @click="saveDraft" :disabled="loading" class="btn btn-secondary">💾 保存草稿</button>
        <button @click="submitForm" :disabled="loading || !canSubmit" class="btn btn-primary">
          {{ isEdit ? '更新' : '提交' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner">🔄</div>
      <p>{{ isEdit ? '加载中...' : '提交中...' }}</p>
    </div>

    <div v-else class="form-content">
      <form @submit.prevent="submitForm" class="fault-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <div class="section-header">
            <h2>📋 基本信息</h2>
            <span class="required-note">* 为必填项</span>
          </div>
          <div class="section-body">
            <div class="form-grid">
              <div class="form-group">
                <label class="required">故障标题</label>
                <input
                  v-model="form.title"
                  type="text"
                  class="form-control"
                  placeholder="请输入故障标题"
                  maxlength="100"
                  :class="{ error: errors.title }"
                >
                <span v-if="errors.title" class="error-text">{{ errors.title }}</span>
              </div>

              <div class="form-group">
                <label class="required">故障类型</label>
                <select v-model="form.fault_type" class="form-control" :class="{ error: errors.fault_type }">
                  <option value="">请选择故障类型</option>
                  <option v-for="type in faultTypes" :key="type" :value="type">{{ type }}</option>
                </select>
                <span v-if="errors.fault_type" class="error-text">{{ errors.fault_type }}</span>
              </div>

              <div class="form-group">
                <label class="required">严重程度</label>
                <select v-model="form.severity" class="form-control" :class="{ error: errors.severity }">
                  <option value="">请选择严重程度</option>
                  <option value="低">低</option>
                  <option value="中">中</option>
                  <option value="高">高</option>
                  <option value="严重">严重</option>
                </select>
                <span v-if="errors.severity" class="error-text">{{ errors.severity }}</span>
              </div>

              <div class="form-group">
                <label class="required">优先级</label>
                <select v-model="form.priority" class="form-control" :class="{ error: errors.priority }">
                  <option value="">请选择优先级</option>
                  <option value="低">低</option>
                  <option value="中">中</option>
                  <option value="高">高</option>
                  <option value="紧急">紧急</option>
                </select>
                <span v-if="errors.priority" class="error-text">{{ errors.priority }}</span>
              </div>

              <div v-if="!isEdit" class="form-group">
                <label>报告人</label>
                <input
                  v-model="form.reporter_name"
                  type="text"
                  class="form-control"
                  placeholder="系统自动填充"
                  readonly
                >
              </div>

              <div v-if="isEdit" class="form-group">
                <label>指派给</label>
                <select v-model="form.assignee_id" class="form-control">
                  <option value="">未指派</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">{{ user.real_name }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- 故障描述 -->
        <div class="form-section">
          <div class="section-header">
            <h2>📝 故障描述</h2>
          </div>
          <div class="section-body">
            <div class="form-group">
              <label class="required">详细描述</label>
              <textarea
                v-model="form.description"
                class="form-control textarea"
                placeholder="请详细描述故障现象、发生时间、操作步骤等信息..."
                rows="6"
                maxlength="2000"
                :class="{ error: errors.description }"
              ></textarea>
              <div class="textarea-footer">
                <span v-if="errors.description" class="error-text">{{ errors.description }}</span>
                <span class="char-count">{{ form.description?.length || 0 }}/2000</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 影响资产 -->
        <div class="form-section">
          <div class="section-header">
            <h2>💻 影响资产</h2>
            <button type="button" @click="showAssetSelector = true" class="btn-sm btn-primary">
              + 添加资产
            </button>
          </div>
          <div class="section-body">
            <div v-if="selectedAssets.length > 0" class="selected-assets">
              <div v-for="asset in selectedAssets" :key="asset.id" class="asset-item">
                <div class="asset-info">
                  <div class="asset-name">{{ asset.name }}</div>
                  <div class="asset-code">{{ asset.asset_code }}</div>
                  <div class="asset-location">{{ asset.location }}</div>
                </div>
                <button type="button" @click="removeAsset(asset)" class="btn-sm btn-danger">移除</button>
              </div>
            </div>
            <div v-else class="no-assets">
              <p>暂未选择影响资产</p>
              <button type="button" @click="showAssetSelector = true" class="btn btn-primary">选择资产</button>
            </div>
          </div>
        </div>

        <!-- 附件上传 -->
        <div class="form-section">
          <div class="section-header">
            <h2>📎 附件文件</h2>
          </div>
          <div class="section-body">
            <div class="upload-area" :class="{ dragover: isDragging }" @dragover.prevent @drop.prevent="handleDrop">
              <input
                ref="fileInputRef"
                type="file"
                multiple
                accept="image/*,application/pdf,.doc,.docx,.xls,.xlsx"
                @change="handleFileSelect"
                style="display: none"
              >
              <div class="upload-content" @click="selectFiles">
                <div class="upload-icon">📁</div>
                <p>点击上传或拖拽文件到此处</p>
                <p class="upload-tip">支持 图片、PDF、Word、Excel 格式，单个文件最大 10MB</p>
              </div>
            </div>

            <div v-if="attachments.length > 0" class="attachment-list">
              <div v-for="file in attachments" :key="file.id || file.name" class="attachment-item">
                <div class="file-icon">{{ getFileIcon(file.type || file.file_type) }}</div>
                <div class="file-info">
                  <div class="file-name">{{ file.name || file.original_name }}</div>
                  <div class="file-meta">
                    <span class="file-size">{{ formatFileSize(file.size || file.file_size) }}</span>
                    <span v-if="file.upload_progress !== undefined" class="upload-progress">
                      {{ file.upload_progress }}%
                    </span>
                  </div>
                  <div v-if="file.upload_progress !== undefined && file.upload_progress < 100" class="progress-bar">
                    <div class="progress-fill" :style="{ width: file.upload_progress + '%' }"></div>
                  </div>
                </div>
                <button type="button" @click="removeAttachment(file)" class="btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- 资产选择器弹窗 -->
    <div v-if="showAssetSelector" class="modal-overlay" @click.self="closeAssetSelector">
      <div class="modal-content">
        <div class="modal-header">
          <h3>选择影响资产</h3>
          <button @click="closeAssetSelector" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="asset-search">
            <input
              v-model="assetSearchKeyword"
              type="text"
              class="form-control"
              placeholder="搜索资产名称或编码..."
              @input="searchAssets"
            >
          </div>
          <div class="asset-grid">
            <div
              v-for="asset in availableAssets"
              :key="asset.id"
              class="asset-card"
              :class="{ selected: isAssetSelected(asset) }"
              @click="toggleAssetSelection(asset)"
            >
              <div class="asset-name">{{ asset.name }}</div>
              <div class="asset-code">{{ asset.asset_code }}</div>
              <div class="asset-location">{{ asset.location }}</div>
              <div class="asset-status">
                <span :class="`status-tag status-${getStatusClass(asset.status)}`">
                  {{ asset.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeAssetSelector" class="btn btn-secondary">取消</button>
          <button @click="confirmAssetSelection" class="btn btn-primary">
            确认选择 ({{ selectedAssets.length }})
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { faultApi } from '@/api/fault'
import { assetApi } from '@/api/asset'
import type { Fault, Asset, PriorityType } from '@/types/common'
import { getStatusClass } from '@/types/common'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const showAssetSelector = ref(false)
const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement>()
const assetSearchKeyword = ref('')

// 表单数据
const form = reactive({
  fault_code: '' as string | undefined, // 故障编码，编辑时由后端提供
  title: '',
  fault_type: '',
  severity: '',
  priority: '',
  description: '',
  reporter_name: '',
  assignee_id: null as number | null
})

// 表单验证错误
const errors = reactive({
  title: '',
  fault_type: '',
  severity: '',
  priority: '',
  description: ''
})

// 其他数据
const faultTypes = ref<string[]>([])
const users = ref<any[]>([])
const selectedAssets = ref<Asset[]>([])
const availableAssets = ref<Asset[]>([])
const attachments = ref<any[]>([])

// 计算属性
const isEdit = computed(() => !!route.params.id)
const faultId = computed(() => route.params.id ? Number(route.params.id) : null)

const canSubmit = computed(() => {
  return form.title && form.fault_type && form.severity && form.priority && form.description
})

// 初始化
onMounted(async () => {
  await loadInitialData()
  if (isEdit.value && faultId.value) {
    await loadFaultData()
  } else {
    // 新建时设置默认报告人
    form.reporter_name = '当前用户' // 实际应从用户状态获取
  }
})

// 数据加载
const loadInitialData = async () => {
  try {
    // 只加载故障类型，用户数据用模拟数据
    const typesRes = await faultApi.getFaultTypes()
    
    if (typesRes.success) {
      faultTypes.value = typesRes.data
    }
    
    // 模拟用户数据
    users.value = [
      { id: 1, real_name: '张三' },
      { id: 2, real_name: '李四' },
      { id: 3, real_name: '王五' }
    ]
  } catch (error) {
    console.error('加载初始数据失败:', error)
  }
}

const loadFaultData = async () => {
  if (!faultId.value) return
  
  loading.value = true
  try {
    const response = await faultApi.getFault(faultId.value)
    if (response.success) {
      const fault = response.data
      form.fault_code = fault.fault_code // 加载故障编码
      form.title = fault.title
      form.fault_type = fault.fault_type
      form.severity = fault.severity
      form.priority = fault.priority
      form.description = fault.description || ''
      form.reporter_name = fault.reporter_name
      
      selectedAssets.value = fault.affected_assets.map(asset => ({
        id: asset.id,
        name: asset.name,
        asset_code: asset.asset_code || '',
        location: '',
        status: '在用'
      })) as Asset[]
    }
  } catch (error) {
    console.error('加载故障数据失败:', error)
  } finally {
    loading.value = false
  }
}

const searchAssets = async () => {
  try {
    const response = await assetApi.getAssets({
      keyword: assetSearchKeyword.value,
      page: 1,
      pageSize: 50
    })
    if (response.success) {
      availableAssets.value = response.data.list
    }
  } catch (error) {
    console.error('搜索资产失败:', error)
  }
}

// 表单验证
const validateForm = (): boolean => {
  // 清空之前的错误
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })

  let isValid = true

  if (!form.title.trim()) {
    errors.title = '请输入故障标题'
    isValid = false
  }

  if (!form.fault_type) {
    errors.fault_type = '请选择故障类型'
    isValid = false
  }

  if (!form.severity) {
    errors.severity = '请选择严重程度'
    isValid = false
  }

  if (!form.priority) {
    errors.priority = '请选择优先级'
    isValid = false
  }

  if (!form.description.trim()) {
    errors.description = '请输入故障描述'
    isValid = false
  }

  return isValid
}

// 事件处理
const goBack = () => {
  router.push('/app/faults')
}

const saveDraft = async () => {
  console.log('保存草稿')
  // TODO: 实现保存草稿功能
}

const submitForm = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true
  try {
    const submitData = {
      ...form,
      priority: form.priority as PriorityType, // 类型断言修复
      severity: form.severity as string,
      fault_type: form.fault_type as string,
      affected_assets: selectedAssets.value.map(asset => ({
        id: asset.id,
        name: asset.name,
        asset_code: asset.asset_code
      }))
    }

    let response
    if (isEdit.value && faultId.value) {
      response = await faultApi.updateFault(faultId.value, submitData)
    } else {
      response = await faultApi.createFault(submitData)
    }

    if (response.success) {
      // 上传附件
      if (attachments.value.length > 0) {
        await uploadAttachments(response.data.id)
      }
      
      console.log(isEdit.value ? '更新成功' : '创建成功')
      router.push('/app/faults')
    }
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}

// 资产选择
const isAssetSelected = (asset: Asset): boolean => {
  return selectedAssets.value.some(selected => selected.id === asset.id)
}

const toggleAssetSelection = (asset: Asset) => {
  const index = selectedAssets.value.findIndex(selected => selected.id === asset.id)
  if (index > -1) {
    selectedAssets.value.splice(index, 1)
  } else {
    selectedAssets.value.push(asset)
  }
}

const removeAsset = (asset: Asset) => {
  const index = selectedAssets.value.findIndex(selected => selected.id === asset.id)
  if (index > -1) {
    selectedAssets.value.splice(index, 1)
  }
}

const closeAssetSelector = () => {
  showAssetSelector.value = false
  assetSearchKeyword.value = ''
}

const confirmAssetSelection = () => {
  showAssetSelector.value = false
}

// 文件处理
const selectFiles = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    handleFiles(Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files) {
    handleFiles(Array.from(event.dataTransfer.files))
  }
}

const handleFiles = (files: File[]) => {
  for (const file of files) {
    if (file.size > 10 * 1024 * 1024) {
      alert(`文件 ${file.name} 超过 10MB 限制`)
      continue
    }
    
    const fileItem = {
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      upload_progress: 0,
      file: file
    }
    
    attachments.value.push(fileItem)
    
    // 模拟上传进度
    simulateUpload(fileItem)
  }
}

const simulateUpload = (fileItem: any) => {
  const interval = setInterval(() => {
    fileItem.upload_progress += 10
    if (fileItem.upload_progress >= 100) {
      clearInterval(interval)
    }
  }, 200)
}

const removeAttachment = (file: any) => {
  const index = attachments.value.findIndex(item => item.id === file.id)
  if (index > -1) {
    attachments.value.splice(index, 1)
  }
}

const uploadAttachments = async (faultId: number) => {
  for (const attachment of attachments.value) {
    if (attachment.file) {
      try {
        await faultApi.uploadFaultAttachment(faultId, attachment.file)
      } catch (error) {
        console.error(`上传附件 ${attachment.name} 失败:`, error)
      }
    }
  }
}

// 工具函数
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileIcon = (fileType: string): string => {
  if (fileType.includes('pdf')) return '📄'
  if (fileType.includes('image')) return '🖼️'
  if (fileType.includes('word')) return '📝'
  if (fileType.includes('excel')) return '📊'
  return '📁'
}

// 拖拽事件
const handleDragOver = () => {
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

// 初始加载资产数据
onMounted(() => {
  searchAssets()
})
</script>

<style scoped>
.fault-form-container {
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

.title-info h1 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 24px;
}

.fault-code {
  font-family: monospace;
  color: #409eff;
  font-weight: 600;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-spinner {
  font-size: 32px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.form-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.fault-form {
  padding: 0;
}

.form-section {
  border-bottom: 1px solid #e4e7ed;
}

.form-section:last-child {
  border-bottom: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #e4e7ed;
  background: #f8f9fa;
}

.section-header h2 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.required-note {
  color: #f56c6c;
  font-size: 12px;
}

.section-body {
  padding: 30px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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

.form-group label.required::after {
  content: ' *';
  color: #f56c6c;
}

.form-control {
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.form-control.error {
  border-color: #f56c6c;
}

.textarea {
  min-height: 120px;
  resize: vertical;
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.char-count {
  font-size: 12px;
  color: #909399;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
}

.selected-assets {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.asset-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.asset-info {
  flex: 1;
}

.asset-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.asset-code {
  font-family: monospace;
  color: #409eff;
  font-size: 12px;
  margin-bottom: 2px;
}

.asset-location {
  color: #909399;
  font-size: 12px;
}

.no-assets {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.no-assets p {
  margin-bottom: 16px;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  transition: border-color 0.2s;
  cursor: pointer;
}

.upload-area:hover,
.upload-area.dragover {
  border-color: #409eff;
  background: #f0f9ff;
}

.upload-content {
  pointer-events: none;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

.attachment-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.file-icon {
  font-size: 24px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.file-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.progress-bar {
  height: 4px;
  background: #f0f2f5;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 4px;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  transition: width 0.3s;
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
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #e4e7ed;
}

.modal-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #909399;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  flex: 1;
  padding: 20px 30px;
  overflow: auto;
}

.asset-search {
  margin-bottom: 20px;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.asset-card {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.asset-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.asset-card.selected {
  border-color: #409eff;
  background: #f0f9ff;
}

.asset-status {
  margin-top: 8px;
}

.status-tag {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-success { background: #f0f9ff; color: #67c23a; }
.status-info { background: #e1f3ff; color: #409eff; }
.status-warning { background: #fdf6ec; color: #e6a23c; }
.status-danger { background: #fef0f0; color: #f56c6c; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 30px;
  border-top: 1px solid #e4e7ed;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-secondary {
  background: #909399;
  color: white;
}

.btn-secondary:hover {
  background: #a6a9ad;
}

.btn-danger {
  background: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background: #f78989;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .fault-form-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-left {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .asset-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .asset-grid {
    grid-template-columns: 1fr;
  }
}
</style>