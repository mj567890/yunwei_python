<template>
  <div class="file-form-page">
    <div class="page-header">
      <div class="header-content">
        <h2>{{ isEdit ? '编辑文件' : '上传文件' }}</h2>
        <div class="header-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" @click="saveFile" :loading="saving">
            {{ isEdit ? '更新' : '上传' }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="page-content">
      <el-row :gutter="24">
        <el-col :span="16">
          <el-form 
            ref="formRef" 
            :model="form" 
            :rules="rules" 
            label-width="120px"
            class="file-form"
          >
            <!-- 文件上传区域 -->
            <el-card title="文件上传" class="upload-section" v-if="!isEdit">
              <el-upload
                ref="uploadRef"
                class="upload-dragger"
                drag
                :action="uploadUrl"
                :multiple="allowMultiple"
                :before-upload="beforeUpload"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :on-progress="handleUploadProgress"
                :file-list="fileList"
                :auto-upload="false"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持格式：{{ allowedFormats.join(', ') }}<br>
                    最大文件大小：{{ maxFileSize }}MB
                  </div>
                </template>
              </el-upload>
              
              <!-- 上传进度 -->
              <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
                <el-progress :percentage="uploadProgress" :show-text="true" />
                <p>正在上传...{{ uploadProgress }}%</p>
              </div>
            </el-card>

            <!-- 文件信息 -->
            <el-card title="文件信息" class="form-section">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="文件名称" prop="name">
                    <el-input 
                      v-model="form.name" 
                      placeholder="请输入文件名称"
                      :disabled="!isEdit && !form.name"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="文件分类" prop="category">
                    <el-select 
                      v-model="form.category" 
                      placeholder="请选择文件分类"
                      style="width: 100%"
                    >
                      <el-option 
                        v-for="category in categories" 
                        :key="category.value" 
                        :label="category.label" 
                        :value="category.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="存储目录" prop="directory">
                    <el-cascader
                      v-model="form.directory"
                      :options="directoryTree"
                      :props="cascaderProps"
                      placeholder="请选择存储目录"
                      style="width: 100%"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="访问权限" prop="permission">
                    <el-select 
                      v-model="form.permission" 
                      placeholder="请选择访问权限"
                      style="width: 100%"
                    >
                      <el-option label="私有" value="private" />
                      <el-option label="部门可见" value="department" />
                      <el-option label="公司可见" value="company" />
                      <el-option label="公开" value="public" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="文件描述" prop="description">
                <el-input 
                  v-model="form.description" 
                  type="textarea" 
                  :rows="4"
                  placeholder="请输入文件描述信息..."
                />
              </el-form-item>

              <el-form-item label="文件标签">
                <el-tag
                  v-for="tag in form.tags"
                  :key="tag"
                  closable
                  :disable-transitions="false"
                  @close="removeTag(tag)"
                  class="tag-item"
                >
                  {{ tag }}
                </el-tag>
                <el-input
                  v-if="inputVisible"
                  ref="InputRef"
                  v-model="inputValue"
                  class="tag-input"
                  size="small"
                  @keyup.enter="handleInputConfirm"
                  @blur="handleInputConfirm"
                />
                <el-button v-else class="button-new-tag" size="small" @click="showInput">
                  + 添加标签
                </el-button>
              </el-form-item>
            </el-card>

            <!-- 高级设置 -->
            <el-card title="高级设置" class="form-section">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="版本控制">
                    <el-switch 
                      v-model="form.version_control"
                      active-text="启用版本控制"
                      inactive-text="禁用版本控制"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="自动备份">
                    <el-switch 
                      v-model="form.auto_backup"
                      active-text="启用自动备份"
                      inactive-text="禁用自动备份"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="过期时间">
                    <el-date-picker
                      v-model="form.expire_at"
                      type="datetime"
                      placeholder="选择过期时间"
                      style="width: 100%"
                      :disabled-date="disabledDate"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="下载限制">
                    <el-input-number
                      v-model="form.download_limit"
                      :min="0"
                      :max="9999"
                      placeholder="最大下载次数"
                      style="width: 100%"
                    />
                    <div class="form-help">0表示无限制</div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="加密保护">
                <el-switch 
                  v-model="form.encrypt"
                  active-text="启用加密"
                  inactive-text="不加密"
                />
                <el-input
                  v-if="form.encrypt"
                  v-model="form.encrypt_password"
                  type="password"
                  placeholder="请设置访问密码"
                  style="margin-top: 8px"
                  show-password
                />
              </el-form-item>
            </el-card>

            <!-- 通知设置 -->
            <el-card title="通知设置" class="form-section">
              <el-form-item label="通知用户">
                <el-select
                  v-model="form.notify_users"
                  multiple
                  placeholder="选择要通知的用户"
                  style="width: 100%"
                >
                  <el-option
                    v-for="user in availableUsers"
                    :key="user.id"
                    :label="user.name"
                    :value="user.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="通知方式">
                <el-checkbox-group v-model="form.notify_methods">
                  <el-checkbox label="email">邮件通知</el-checkbox>
                  <el-checkbox label="system">系统通知</el-checkbox>
                  <el-checkbox label="sms">短信通知</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item label="通知消息">
                <el-input
                  v-model="form.notify_message"
                  type="textarea"
                  :rows="3"
                  placeholder="自定义通知消息..."
                />
              </el-form-item>
            </el-card>
          </el-form>
        </el-col>

        <el-col :span="8">
          <!-- 上传预览 -->
          <el-card title="文件预览" class="preview-card" v-if="previewUrl">
            <div class="file-preview">
              <img 
                v-if="isImageFile" 
                :src="previewUrl" 
                :alt="form.name"
                class="preview-image"
              />
              <div v-else class="file-icon-preview">
                <span class="file-icon">{{ getFileIcon(getFileExtension(form.name)) }}</span>
                <p class="file-name">{{ form.name }}</p>
              </div>
            </div>
          </el-card>

          <!-- 上传提示 -->
          <el-card title="上传说明" class="tips-card">
            <div class="tips-content">
              <h4>📋 上传须知</h4>
              <ul class="tips-list">
                <li>文件大小不超过 {{ maxFileSize }}MB</li>
                <li>支持格式：{{ allowedFormats.join(', ') }}</li>
                <li>文件名不能包含特殊字符</li>
                <li>启用版本控制后可保留历史版本</li>
                <li>加密文件需要密码才能访问</li>
              </ul>
              
              <h4>🔒 权限说明</h4>
              <ul class="tips-list">
                <li><strong>私有：</strong>仅上传者可见</li>
                <li><strong>部门可见：</strong>同部门成员可见</li>
                <li><strong>公司可见：</strong>公司所有成员可见</li>
                <li><strong>公开：</strong>所有人都可访问</li>
              </ul>
            </div>
          </el-card>

          <!-- 存储统计 -->
          <el-card title="存储统计" class="stats-card">
            <div class="storage-stats">
              <div class="stat-item">
                <div class="stat-label">已用空间</div>
                <div class="stat-value">{{ formatFileSize(storageUsed) }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">总空间</div>
                <div class="stat-value">{{ formatFileSize(storageTotal) }}</div>
              </div>
              <div class="storage-progress">
                <el-progress 
                  :percentage="storagePercentage" 
                  :status="storagePercentage > 90 ? 'exception' : undefined"
                />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadProps, UploadUserFile } from 'element-plus'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const uploadRef = ref()
const InputRef = ref()

const isEdit = computed(() => !!route.params.id)
const fileId = computed(() => route.params.id as string)

const saving = ref(false)
const uploadProgress = ref(0)
const inputVisible = ref(false)
const inputValue = ref('')
const fileList = ref<UploadUserFile[]>([])

const allowMultiple = ref(false)
const maxFileSize = ref(100) // MB
const allowedFormats = ref(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'jpg', 'png', 'gif', 'zip', 'rar'])
const uploadUrl = ref('/api/files/upload')

const storageUsed = ref(8589934592) // 8GB
const storageTotal = ref(21474836480) // 20GB

const form = ref({
  name: '',
  category: '',
  directory: [],
  permission: 'private',
  description: '',
  tags: [] as string[],
  version_control: true,
  auto_backup: false,
  expire_at: null as Date | null,
  download_limit: 0,
  encrypt: false,
  encrypt_password: '',
  notify_users: [] as number[],
  notify_methods: ['system'] as string[],
  notify_message: ''
})

const categories = ref([
  { label: '文档资料', value: 'document' },
  { label: '图片媒体', value: 'media' },
  { label: '压缩包', value: 'archive' },
  { label: '系统文件', value: 'system' },
  { label: '其他', value: 'other' }
])

const directoryTree = ref([
  {
    value: 'root',
    label: '根目录',
    children: [
      {
        value: 'documents',
        label: '文档',
        children: [
          { value: 'contracts', label: '合同' },
          { value: 'reports', label: '报告' }
        ]
      },
      {
        value: 'media',
        label: '媒体文件',
        children: [
          { value: 'images', label: '图片' },
          { value: 'videos', label: '视频' }
        ]
      },
      { value: 'backup', label: '备份文件' }
    ]
  }
])

const availableUsers = ref([
  { id: 1, name: '张三' },
  { id: 2, name: '李四' },
  { id: 3, name: '王五' }
])

const cascaderProps = {
  expandTrigger: 'hover' as const,
  value: 'value',
  label: 'label',
  children: 'children'
}

const previewUrl = computed(() => {
  if (fileList.value.length > 0) {
    return fileList.value[0].url
  }
  return ''
})

const isImageFile = computed(() => {
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
  const ext = getFileExtension(form.value.name)
  return imageExts.includes(ext.toLowerCase())
})

const storagePercentage = computed(() => {
  return Math.round((storageUsed.value / storageTotal.value) * 100)
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入文件名称', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择文件分类', trigger: 'change' }
  ],
  permission: [
    { required: true, message: '请选择访问权限', trigger: 'change' }
  ]
}

const getFileExtension = (filename: string) => {
  return filename.split('.').pop() || ''
}

const getFileIcon = (ext: string) => {
  const iconMap: Record<string, string> = {
    'pdf': '📄',
    'doc': '📝',
    'docx': '📝',
    'xls': '📊',
    'xlsx': '📊',
    'ppt': '📈',
    'pptx': '📈',
    'txt': '📃',
    'zip': '🗜️',
    'rar': '🗜️',
    'jpg': '🖼️',
    'jpeg': '🖼️',
    'png': '🖼️',
    'gif': '🖼️'
  }
  return iconMap[ext.toLowerCase()] || '📁'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now()
}

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isAllowedFormat = allowedFormats.value.some(format => 
    file.name.toLowerCase().endsWith('.' + format.toLowerCase())
  )
  const isLtMaxSize = file.size / 1024 / 1024 < maxFileSize.value

  if (!isAllowedFormat) {
    ElMessage.error(`只能上传 ${allowedFormats.value.join(', ')} 格式的文件!`)
    return false
  }
  if (!isLtMaxSize) {
    ElMessage.error(`文件大小不能超过 ${maxFileSize.value}MB!`)
    return false
  }

  // 自动填充文件名
  if (!form.value.name) {
    form.value.name = file.name
  }

  return true
}

const handleUploadSuccess = (response: any, file: UploadUserFile) => {
  ElMessage.success('文件上传成功')
  uploadProgress.value = 100
  
  // 处理上传成功后的逻辑
  console.log('Upload success:', response, file)
}

const handleUploadError = (error: Error) => {
  ElMessage.error('文件上传失败')
  uploadProgress.value = 0
  console.error('Upload error:', error)
}

const handleUploadProgress = (event: any) => {
  uploadProgress.value = Math.round(event.percent)
}

const removeTag = (tag: string) => {
  form.value.tags.splice(form.value.tags.indexOf(tag), 1)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value?.input?.focus()
  })
}

const handleInputConfirm = () => {
  if (inputValue.value && !form.value.tags.includes(inputValue.value)) {
    form.value.tags.push(inputValue.value)
  }
  inputVisible.value = false
  inputValue.value = ''
}

const loadFileData = async () => {
  if (!isEdit.value) return
  
  try {
    // 模拟API调用加载文件数据
    const mockFile = {
      name: 'IT运维系统架构图.pdf',
      category: 'document',
      directory: ['root', 'documents'],
      permission: 'department',
      description: '系统架构设计文档',
      tags: ['架构', '设计'],
      version_control: true,
      auto_backup: false,
      expire_at: null,
      download_limit: 0,
      encrypt: false,
      encrypt_password: '',
      notify_users: [],
      notify_methods: ['system'],
      notify_message: ''
    }
    
    Object.assign(form.value, mockFile)
  } catch (error) {
    console.error('加载文件数据失败:', error)
    ElMessage.error('加载文件数据失败')
  }
}

const saveFile = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    if (!isEdit.value) {
      // 触发文件上传
      uploadRef.value?.submit()
    }
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success(isEdit.value ? '文件信息更新成功' : '文件上传成功')
    router.push('/app/files')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadFileData()
})
</script>

<style scoped>
.file-form-page {
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

.file-form {
  background: white;
}

.form-section,
.upload-section {
  margin-bottom: 24px;
}

.form-section :deep(.el-card__header),
.upload-section :deep(.el-card__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  font-weight: 500;
}

.upload-dragger {
  width: 100%;
}

.upload-progress {
  margin-top: 16px;
  text-align: center;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.tag-item {
  margin-right: 8px;
  margin-bottom: 8px;
}

.tag-input {
  width: 90px;
  margin-right: 8px;
  margin-bottom: 8px;
}

.button-new-tag {
  margin-bottom: 8px;
  height: 24px;
  line-height: 22px;
  padding: 0 8px;
}

.preview-card {
  margin-bottom: 24px;
}

.file-preview {
  text-align: center;
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
}

.file-icon-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 48px;
}

.file-name {
  color: #606266;
  font-size: 14px;
  margin: 0;
  word-break: break-word;
}

.tips-card {
  margin-bottom: 24px;
}

.tips-content h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.tips-list {
  margin: 0 0 20px 0;
  padding-left: 20px;
  color: #606266;
  font-size: 12px;
}

.tips-list li {
  margin-bottom: 6px;
  line-height: 1.4;
}

.stats-card {
  margin-bottom: 24px;
}

.storage-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  color: #303133;
  font-weight: 500;
}

.storage-progress {
  margin-top: 8px;
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
}
</style>