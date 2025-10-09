<template>
  <div class="maintenance-form-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <button @click="goBack" class="btn btn-secondary">← 返回</button>
        <div class="title-info">
          <h1>{{ isEdit ? '编辑运维记录' : '新建运维记录' }}</h1>
          <div v-if="isEdit && form.record_code" class="record-code">{{ form.record_code }}</div>
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
      <form @submit.prevent="submitForm" class="maintenance-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <div class="section-header">
            <h2>📋 基本信息</h2>
            <span class="required-note">* 为必填项</span>
          </div>
          <div class="section-body">
            <div class="form-grid">
              <div class="form-group">
                <label class="required">维护标题</label>
                <input
                  v-model="form.title"
                  type="text"
                  class="form-control"
                  placeholder="请输入维护标题"
                  maxlength="100"
                  :class="{ error: errors.title }"
                >
                <span v-if="errors.title" class="error-text">{{ errors.title }}</span>
              </div>

              <div class="form-group">
                <label class="required">记录类型</label>
                <HierarchicalSelect
                  v-model="form.record_type"
                  :items="recordTypesData"
                  :loading="loadingTypes"
                  :hasError="!!errors.record_type"
                  placeholder="请选择记录类型"
                />
                <span v-if="errors.record_type" class="error-text">{{ errors.record_type }}</span>
              </div>

              <div class="form-group">
                <label class="required">维护类别</label>
                <HierarchicalSelect
                  v-model="form.category"
                  :items="categoriesData"
                  :loading="loadingCategories"
                  :hasError="!!errors.category"
                  placeholder="请选择维护类别"
                />
                <span v-if="errors.category" class="error-text">{{ errors.category }}</span>
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

              <div class="form-group">
                <label class="required">责任人</label>
                <select v-model="form.responsible_person_id" class="form-control" :class="{ error: errors.responsible_person_id }">
                  <option value="">请选择责任人</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">{{ user.real_name }}</option>
                </select>
                <span v-if="errors.responsible_person_id" class="error-text">{{ errors.responsible_person_id }}</span>
              </div>

              <div class="form-group">
                <label class="required">所属部门</label>
                <HierarchicalSelect
                  v-model="form.department"
                  :items="departmentsData"
                  :loading="loadingDepartments"
                  :hasError="!!errors.department"
                  placeholder="请选择部门"
                />
                <span v-if="errors.department" class="error-text">{{ errors.department }}</span>
              </div>

              <div class="form-group">
                <label class="required">开始时间</label>
                <input
                  v-model="form.start_time"
                  type="datetime-local"
                  class="form-control"
                  :class="{ error: errors.start_time }"
                >
                <span v-if="errors.start_time" class="error-text">{{ errors.start_time }}</span>
              </div>

              <div class="form-group">
                <label>计划完成时间</label>
                <input
                  v-model="form.planned_end_time"
                  type="datetime-local"
                  class="form-control"
                >
              </div>

              <div class="form-group">
                <label>预计耗时(小时)</label>
                <input
                  v-model.number="form.estimated_duration"
                  type="number"
                  class="form-control"
                  placeholder="请输入预计耗时"
                  min="0"
                  step="0.5"
                >
              </div>

              <div class="form-group">
                <label>预算成本(元)</label>
                <input
                  v-model.number="form.estimated_cost"
                  type="number"
                  class="form-control"
                  placeholder="请输入预算成本"
                  min="0"
                  step="0.01"
                >
              </div>
            </div>
          </div>
        </div>

        <!-- 维护描述 -->
        <div class="form-section">
          <div class="section-header">
            <h2>📝 维护描述</h2>
          </div>
          <div class="section-body">
            <div class="form-group">
              <label class="required">详细描述</label>
              <textarea
                v-model="form.description"
                class="form-control textarea"
                placeholder="请详细描述维护内容、目标、预期效果等信息..."
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

        <!-- 涉及资产 -->
        <div class="form-section">
          <div class="section-header">
            <h2>💻 涉及资产</h2>
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
                  <div class="asset-status">
                    <span :class="`status-tag status-${getStatusClass(asset.status)}`">
                      {{ asset.status }}
                    </span>
                  </div>
                </div>
                <button type="button" @click="removeAsset(asset)" class="btn-sm btn-danger">移除</button>
              </div>
            </div>
            <div v-else class="no-assets">
              <p>暂未选择涉及资产</p>
              <button type="button" @click="showAssetSelector = true" class="btn btn-primary">选择资产</button>
            </div>
          </div>
        </div>

        <!-- 执行步骤 -->
        <div class="form-section">
          <div class="section-header">
            <h2>📋 执行步骤</h2>
            <button type="button" @click="addExecutionStep" class="btn-sm btn-primary">
              + 添加步骤
            </button>
          </div>
          <div class="section-body">
            <div v-if="executionSteps.length > 0" class="steps-list">
              <div v-for="(step, index) in executionSteps" :key="step.id" class="step-item">
                <div class="step-number">{{ index + 1 }}</div>
                <div class="step-content">
                  <div class="form-group">
                    <label class="required">步骤标题</label>
                    <input
                      v-model="step.title"
                      type="text"
                      class="form-control"
                      placeholder="请输入步骤标题"
                      maxlength="50"
                    >
                  </div>
                  <div class="form-group">
                    <label>步骤描述</label>
                    <textarea
                      v-model="step.description"
                      class="form-control"
                      placeholder="请描述具体执行内容..."
                      rows="3"
                      maxlength="500"
                    ></textarea>
                  </div>
                  <div class="step-meta">
                    <div class="form-group">
                      <label>执行人</label>
                      <select v-model="step.executor_id" class="form-control">
                        <option value="">请选择执行人</option>
                        <option v-for="user in users" :key="user.id" :value="user.id">{{ user.real_name }}</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>预计时间(分钟)</label>
                      <input
                        v-model.number="step.estimated_time"
                        type="number"
                        class="form-control"
                        placeholder="预计时间"
                        min="0"
                      >
                    </div>
                  </div>
                </div>
                <div class="step-actions">
                  <button type="button" @click="moveStepUp(index)" :disabled="index === 0" class="btn-sm btn-secondary">↑</button>
                  <button type="button" @click="moveStepDown(index)" :disabled="index === executionSteps.length - 1" class="btn-sm btn-secondary">↓</button>
                  <button type="button" @click="removeExecutionStep(index)" class="btn-sm btn-danger">删除</button>
                </div>
              </div>
            </div>
            <div v-else class="no-steps">
              <p>暂无执行步骤</p>
              <button type="button" @click="addExecutionStep" class="btn btn-primary">添加步骤</button>
            </div>
          </div>
        </div>

        <!-- 风险评估 -->
        <div class="form-section">
          <div class="section-header">
            <h2>⚠️ 风险评估</h2>
          </div>
          <div class="section-body">
            <div class="form-group">
              <label>风险级别</label>
              <select v-model="form.risk_level" class="form-control">
                <option value="">请选择风险级别</option>
                <option value="低">低</option>
                <option value="中">中</option>
                <option value="高">高</option>
              </select>
            </div>
            <div class="form-group">
              <label>潜在风险</label>
              <textarea
                v-model="form.potential_risks"
                class="form-control"
                placeholder="请描述维护过程中可能遇到的风险..."
                rows="4"
                maxlength="1000"
              ></textarea>
            </div>
            <div class="form-group">
              <label>应对措施</label>
              <textarea
                v-model="form.risk_mitigation"
                class="form-control"
                placeholder="请描述风险应对和预防措施..."
                rows="4"
                maxlength="1000"
              ></textarea>
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
          <h3>选择涉及资产</h3>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { dictionaryApi } from '@/api/dictionary'
import { maintenanceApi } from '@/api/maintenance'
import { assetApi } from '@/api/asset'
import type { MaintenanceRecord, Asset, PriorityType } from '@/types/common'
import { getStatusClass } from '@/types/common'
import HierarchicalSelect from '@/components/form/HierarchicalSelect.vue'

// 数据字典项接口
interface DictItem {
  id: number
  name: string
  code: string
  description?: string
  parent_id?: number | null
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

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
  record_code: '', // 运维记录编码
  title: '',
  record_type: '',
  category: '',
  priority: '' as PriorityType | '',
  responsible_person_id: null as number | null,
  department: '',
  start_time: '',
  planned_end_time: '',
  description: '',
  estimated_duration: null as number | null,
  estimated_cost: null as number | null,
  risk_level: '',
  potential_risks: '',
  risk_mitigation: ''
})

// 表单验证错误
const errors = reactive({
  title: '',
  record_type: '',
  category: '',
  priority: '',
  responsible_person_id: '',
  department: '',
  start_time: '',
  description: ''
})

// 其他数据
const recordTypes = ref<string[]>([])
const categories = ref<string[]>([])
const departments = ref<string[]>([])
const users = ref<any[]>([])
const selectedAssets = ref<Asset[]>([])
const availableAssets = ref<Asset[]>([])
const executionSteps = ref<any[]>([])
const attachments = ref<any[]>([])

// 层级数据字典数据
const recordTypesData = ref<DictItem[]>([])
const categoriesData = ref<DictItem[]>([])
const departmentsData = ref<DictItem[]>([])

// 加载状态
const loadingTypes = ref(false)
const loadingCategories = ref(false)
const loadingDepartments = ref(false)

// 计算属性
const isEdit = computed(() => !!route.params.id)
const maintenanceId = computed(() => route.params.id ? Number(route.params.id) : null)

const canSubmit = computed(() => {
  return form.title && form.record_type && form.category && form.priority && 
         form.responsible_person_id && form.department && form.start_time && form.description
})

// 初始化
onMounted(async () => {
  await loadInitialData()
  if (isEdit.value && maintenanceId.value) {
    await loadMaintenanceData()
  } else {
    // 新建时设置默认开始时间
    const now = new Date()
    form.start_time = now.toISOString().slice(0, 16)
  }
})

// 数据加载
const loadInitialData = async () => {
  try {
    // 加载层级数据
    loadingTypes.value = true
    loadingCategories.value = true
    loadingDepartments.value = true
    
    const [
      typesRes, 
      categoriesRes, 
      departmentsRes,
      typesDataRes,
      categoriesDataRes,
      departmentsDataRes
    ] = await Promise.all([
      dictionaryApi.getTypesForForm(),
      dictionaryApi.getCategoriesForForm(),
      dictionaryApi.getDepartmentsForForm(),
      dictionaryApi.getMaintenanceTypes(),
      dictionaryApi.getMaintenanceCategories(),
      dictionaryApi.getDepartments()
    ])
    
    // 简化数据（备用）
    if (typesRes.success) {
      recordTypes.value = typesRes.data
    }
    
    if (categoriesRes.success) {
      categories.value = categoriesRes.data
    }
    
    if (departmentsRes.success) {
      departments.value = departmentsRes.data
    }
    
    // 层级数据
    if (typesDataRes.success) {
      recordTypesData.value = typesDataRes.data
      loadingTypes.value = false
    }
    
    if (categoriesDataRes.success) {
      categoriesData.value = categoriesDataRes.data
      loadingCategories.value = false
    }
    
    if (departmentsDataRes.success) {
      departmentsData.value = departmentsDataRes.data
      loadingDepartments.value = false
    }
    
    // 模拟用户数据
    users.value = [
      { id: 1, real_name: '张三' },
      { id: 2, real_name: '李四' },
      { id: 3, real_name: '王五' },
      { id: 4, real_name: '赵六' }
    ]
  } catch (error) {
    console.error('加载初始数据失败:', error)
    
    // 停止加载状态
    loadingTypes.value = false
    loadingCategories.value = false
    loadingDepartments.value = false
    
    // 备用默认数据（如果 API 失败）
    if (recordTypes.value.length === 0) {
      recordTypes.value = ['例行维护', '紧急处理', '升级改造', '故障修复', '巡检']
    }
    if (categories.value.length === 0) {
      categories.value = ['硬件维护', '软件维护', '网络设备', '系统巡检', '故障修复']
    }
    if (departments.value.length === 0) {
      departments.value = ['IT部门', '运维部门', '技术部门', '网络部门']
    }
    users.value = [
      { id: 1, real_name: '张三' },
      { id: 2, real_name: '李四' },
      { id: 3, real_name: '王五' },
      { id: 4, real_name: '赵六' }
    ]
  }
}

const loadMaintenanceData = async () => {
  if (!maintenanceId.value) return
  
  loading.value = true
  try {
    const response = await maintenanceApi.getMaintenance(maintenanceId.value)
    if (response.success) {
      const maintenance = response.data
      form.record_code = maintenance.record_code || ''
      form.title = maintenance.title
      form.record_type = maintenance.record_type
      form.category = maintenance.category
      form.priority = maintenance.priority as PriorityType | ''
      form.department = maintenance.department
      form.start_time = maintenance.start_time
      form.planned_end_time = maintenance.planned_end_time || ''
      form.description = maintenance.description || ''
      form.estimated_duration = maintenance.estimated_duration || null
      form.estimated_cost = maintenance.estimated_cost || null
      form.risk_level = maintenance.risk_level || ''
      form.potential_risks = maintenance.potential_risks || ''
      form.risk_mitigation = maintenance.risk_mitigation || ''
      
      // 加载关联数据
      await Promise.all([
        loadAffectedAssets(),
        loadExecutionSteps()
      ])
    }
  } catch (error) {
    console.error('加载运维记录数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadAffectedAssets = async () => {
  try {
    if (!maintenanceId.value) return
    const response = await maintenanceApi.getAffectedAssets(maintenanceId.value)
    if (response.success) {
      selectedAssets.value = response.data
    }
  } catch (error) {
    console.error('加载涉及资产失败:', error)
  }
}

const loadExecutionSteps = async () => {
  try {
    if (!maintenanceId.value) return
    const response = await maintenanceApi.getExecutionSteps(maintenanceId.value)
    if (response.success) {
      executionSteps.value = response.data
    }
  } catch (error) {
    console.error('加载执行步骤失败:', error)
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
    errors.title = '请输入维护标题'
    isValid = false
  }

  if (!form.record_type) {
    errors.record_type = '请选择记录类型'
    isValid = false
  }

  if (!form.category) {
    errors.category = '请选择维护类别'
    isValid = false
  }

  if (!form.priority) {
    errors.priority = '请选择优先级'
    isValid = false
  }

  if (!form.responsible_person_id) {
    errors.responsible_person_id = '请选择责任人'
    isValid = false
  }

  if (!form.department) {
    errors.department = '请选择所属部门'
    isValid = false
  }

  if (!form.start_time) {
    errors.start_time = '请选择开始时间'
    isValid = false
  }

  if (!form.description.trim()) {
    errors.description = '请输入维护描述'
    isValid = false
  }

  return isValid
}

// 事件处理
const goBack = () => {
  router.push('/app/maintenance')
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
      priority: form.priority || undefined, // 将空字符串转为undefined
      affected_assets: selectedAssets.value.map(asset => ({
        id: asset.id,
        name: asset.name,
        asset_code: asset.asset_code
      })),
      execution_steps: executionSteps.value
    } as any // 使用any类型跳过类型检查，因为API可能支持额外字段

    let response
    if (isEdit.value && maintenanceId.value) {
      response = await maintenanceApi.updateMaintenance(maintenanceId.value, submitData)
    } else {
      response = await maintenanceApi.createMaintenance(submitData)
    }

    if (response.success) {
      // 上传附件
      if (attachments.value.length > 0) {
        await uploadAttachments(response.data.id)
      }
      
      console.log(isEdit.value ? '更新成功' : '创建成功')
      router.push('/app/maintenance')
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

// 执行步骤管理
const addExecutionStep = () => {
  executionSteps.value.push({
    id: Date.now(),
    title: '',
    description: '',
    executor_id: null,
    estimated_time: null
  })
}

const removeExecutionStep = (index: number) => {
  executionSteps.value.splice(index, 1)
}

const moveStepUp = (index: number) => {
  if (index > 0) {
    const temp = executionSteps.value[index]
    executionSteps.value[index] = executionSteps.value[index - 1]
    executionSteps.value[index - 1] = temp
  }
}

const moveStepDown = (index: number) => {
  if (index < executionSteps.value.length - 1) {
    const temp = executionSteps.value[index]
    executionSteps.value[index] = executionSteps.value[index + 1]
    executionSteps.value[index + 1] = temp
  }
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

const uploadAttachments = async (maintenanceId: number) => {
  for (const attachment of attachments.value) {
    if (attachment.file) {
      try {
        await maintenanceApi.uploadAttachment(maintenanceId, attachment.file)
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

// 初始加载资产数据
onMounted(() => {
  searchAssets()
})
</script>

<style scoped>
.maintenance-form-container {
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

.record-code {
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

.maintenance-form {
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
  margin-bottom: 4px;
}

.asset-status {
  margin-top: 4px;
}

.no-assets, .no-steps {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.no-assets p, .no-steps p {
  margin-bottom: 16px;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  display: grid;
  gap: 16px;
}

.step-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.step-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 30px;
  border-top: 1px solid #e4e7ed;
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

.btn-secondary:hover:not(:disabled) {
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
  .maintenance-form-container {
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
  
  .step-meta {
    grid-template-columns: 1fr;
  }
  
  .asset-item,
  .step-item {
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