<template>
  <div class="file-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>文件管理</h1>
      <div class="header-actions">
        <button @click="refreshFiles" class="btn btn-secondary">🔄 刷新</button>
        <button @click="toggleView" class="btn btn-secondary">
          {{ viewMode === 'grid' ? '📋 列表视图' : '🔲 网格视图' }}
        </button>
        <button @click="showUploadDialog = true" class="btn btn-primary">📤 上传文件</button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stats-card">
        <div class="stats-icon">📁</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.totalFiles }}</div>
          <div class="stats-label">文件总数</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">💾</div>
        <div class="stats-content">
          <div class="stats-number">{{ formatFileSize(stats.totalSize) }}</div>
          <div class="stats-label">总存储空间</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">📊</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.imageFiles }}</div>
          <div class="stats-label">图片文件</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">📄</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.documentFiles }}</div>
          <div class="stats-label">文档文件</div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>文件名搜索</label>
          <input 
            v-model="searchParams.keyword" 
            placeholder="搜索文件名或描述" 
            @input="handleSearch"
          />
        </div>
        <div class="form-group">
          <label>文件类型</label>
          <select v-model="searchParams.fileType" @change="handleSearch">
            <option value="">全部类型</option>
            <option value="image">图片</option>
            <option value="document">文档</option>
            <option value="video">视频</option>
            <option value="audio">音频</option>
            <option value="archive">压缩包</option>
            <option value="other">其他</option>
          </select>
        </div>
        <div class="form-group">
          <label>上传时间</label>
          <select v-model="searchParams.timeRange" @change="handleSearch">
            <option value="">全部时间</option>
            <option value="today">今天</option>
            <option value="week">最近一周</option>
            <option value="month">最近一个月</option>
            <option value="year">最近一年</option>
          </select>
        </div>
        <div class="form-group">
          <label>文件大小</label>
          <select v-model="searchParams.sizeRange" @change="handleSearch">
            <option value="">全部大小</option>
            <option value="small">小于1MB</option>
            <option value="medium">1-10MB</option>
            <option value="large">10-100MB</option>
            <option value="xlarge">大于100MB</option>
          </select>
        </div>
        <div class="form-group">
          <button @click="resetSearch" class="btn btn-secondary">🔄 重置</button>
        </div>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="file-content">
      <div v-if="loading" class="loading">
        <div class="loading-spinner">🔄</div>
        <p>加载中...</p>
      </div>
      
      <!-- 网格视图 -->
      <div v-else-if="viewMode === 'grid'" class="file-grid">
        <div 
          v-for="file in filteredFiles" 
          :key="file.id"
          class="file-card"
          @click="selectFile(file)"
          :class="{ selected: selectedFiles.includes(file.id) }"
        >
          <div class="file-preview">
            <img 
              v-if="isImageFile(file.file_type)" 
              :src="file.thumbnail_url || file.file_url" 
              :alt="file.original_name"
              @error="handleImageError"
            />
            <div v-else class="file-icon">
              {{ getFileIcon(file.file_type) }}
            </div>
          </div>
          <div class="file-info">
            <div class="file-name" :title="file.original_name">
              {{ file.original_name }}
            </div>
            <div class="file-meta">
              <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
              <span class="file-date">{{ formatDate(file.created_at) }}</span>
            </div>
            <div class="file-tags" v-if="file.tags && file.tags.length > 0">
              <span 
                v-for="tag in file.tags.slice(0, 2)" 
                :key="tag" 
                class="tag"
              >
                {{ tag }}
              </span>
              <span v-if="file.tags.length > 2" class="more-tags">
                +{{ file.tags.length - 2 }}
              </span>
            </div>
          </div>
          <div class="file-actions">
            <button @click.stop="downloadFile(file)" class="btn-icon" title="下载">
              📥
            </button>
            <button @click.stop="openPreviewFile(file)" class="btn-icon" title="预览">
              👁️
            </button>
            <button @click.stop="editFile(file)" class="btn-icon" title="编辑">
              ✏️
            </button>
            <button @click.stop="deleteFile(file)" class="btn-icon btn-danger" title="删除">
              🗑️
            </button>
          </div>
        </div>
      </div>
      
      <!-- 列表视图 -->
      <div v-else class="file-table-container">
        <table class="file-table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  @change="toggleSelectAll"
                  :checked="allSelected"
                  :indeterminate="someSelected"
                />
              </th>
              <th width="60">序号</th>
              <th>文件名</th>
              <th>类型</th>
              <th>大小</th>
              <th>上传者</th>
              <th>上传时间</th>
              <th>下载次数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(file, index) in filteredFiles" 
              :key="file.id"
              :class="{ selected: selectedFiles.includes(file.id) }"
            >
              <td>
                <input 
                  type="checkbox" 
                  :value="file.id"
                  v-model="selectedFiles"
                />
              </td>
              <td class="row-number">{{ index + 1 }}</td>
              <td class="file-name-cell">
                <div class="name-content">
                  <div class="file-icon-small">{{ getFileIcon(file.file_type) }}</div>
                  <div class="name-info">
                    <div class="file-name">{{ file.original_name }}</div>
                    <div class="file-description" v-if="file.description">
                      {{ file.description }}
                    </div>
                  </div>
                </div>
              </td>
              <td>
                <span class="file-type-tag">{{ getFileTypeName(file.file_type) }}</span>
              </td>
              <td>{{ formatFileSize(file.file_size) }}</td>
              <td>{{ file.uploader_name || '-' }}</td>
              <td>{{ formatDate(file.created_at) }}</td>
              <td>{{ file.download_count || 0 }}</td>
              <td class="actions">
                <button @click="downloadFile(file)" class="btn-sm btn-info">下载</button>
                <button @click="openPreviewFile(file)" class="btn-sm btn-secondary">预览</button>
                <button @click="editFile(file)" class="btn-sm btn-primary">编辑</button>
                <button @click="deleteFile(file)" class="btn-sm btn-danger">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && filteredFiles.length === 0" class="empty-state">
        <div class="empty-icon">📁</div>
        <p>暂无文件</p>
        <button @click="showUploadDialog = true" class="btn btn-primary">上传第一个文件</button>
      </div>
    </div>

    <!-- 批量操作栏 -->
    <div v-if="selectedFiles.length > 0" class="batch-actions">
      <div class="selected-info">
        已选择 {{ selectedFiles.length }} 个文件
      </div>
      <div class="actions">
        <button @click="batchDownload" class="btn btn-info">批量下载</button>
        <button @click="batchDelete" class="btn btn-danger">批量删除</button>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total > 0" class="pagination">
      <div class="pagination-left">
        <span class="page-size-label">每页显示</span>
        <select v-model="pagination.pageSize" @change="changePageSize" class="page-size-select">
          <option value="10">10条</option>
          <option value="20">20条</option>
          <option value="50">50条</option>
          <option value="100">100条</option>
        </select>
      </div>
      <div class="pagination-center">
        <button 
          @click="changePage(pagination.page - 1)" 
          :disabled="pagination.page <= 1"
          class="btn btn-secondary"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ pagination.page }} / {{ Math.ceil(pagination.total / pagination.pageSize) }} 页
          (共 {{ pagination.total }} 条)
        </span>
        <button 
          @click="changePage(pagination.page + 1)" 
          :disabled="pagination.page >= Math.ceil(pagination.total / pagination.pageSize)"
          class="btn btn-secondary"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 上传对话框 -->
    <div v-if="showUploadDialog" class="modal-overlay" @click="closeUploadDialog">
      <div class="modal-content upload-modal" @click.stop>
        <div class="modal-header">
          <h3>上传文件</h3>
          <button @click="closeUploadDialog" class="close-btn">✕</button>
        </div>
        
        <div class="modal-body">
          <!-- 拖拽上传区域 -->
          <div 
            class="upload-area"
            :class="{ 'drag-over': isDragOver }"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave" 
            @drop.prevent="handleDrop"
            @click="triggerFileSelect"
          >
            <div class="upload-icon">📤</div>
            <div class="upload-text">
              <p>拖拽文件到此处或<span class="link-text">点击选择文件</span></p>
              <p class="upload-hint">支持多文件上传，单个文件最大100MB</p>
            </div>
            <input 
              ref="fileInput"
              type="file" 
              multiple 
              @change="handleFileSelect"
              style="display: none"
            />
          </div>

          <!-- 文件列表 -->
          <div v-if="uploadQueue.length > 0" class="upload-queue">
            <h4>待上传文件 ({{ uploadQueue.length }})</h4>
            <div class="upload-list">
              <div 
                v-for="(item, index) in uploadQueue" 
                :key="index"
                class="upload-item"
              >
                <div class="file-info">
                  <div class="file-icon">{{ getFileIcon(item.file.type) }}</div>
                  <div class="file-details">
                    <div class="file-name">{{ item.file.name }}</div>
                    <div class="file-size">{{ formatFileSize(item.file.size) }}</div>
                  </div>
                </div>
                
                <div class="upload-progress">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: item.progress + '%' }"
                    ></div>
                  </div>
                  <div class="progress-text">{{ item.progress }}%</div>
                </div>
                
                <div class="upload-status">
                  <span v-if="item.status === 'waiting'" class="status waiting">等待中</span>
                  <span v-else-if="item.status === 'uploading'" class="status uploading">上传中</span>
                  <span v-else-if="item.status === 'success'" class="status success">成功</span>
                  <span v-else-if="item.status === 'error'" class="status error">失败</span>
                </div>
                
                <button 
                  @click="removeFromQueue(index)" 
                  class="btn-icon btn-danger"
                  :disabled="item.status === 'uploading'"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          <!-- 上传设置 -->
          <div class="upload-settings">
            <div class="form-group">
              <label>文件描述</label>
              <textarea 
                v-model="uploadConfig.description" 
                rows="2" 
                placeholder="可选：为这批文件添加描述"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label>文件标签</label>
              <input 
                v-model="uploadConfig.tags" 
                type="text" 
                placeholder="用逗号分隔多个标签，如：重要,合同,2024"
              />
            </div>
            
            <div class="form-group">
              <label>
                <input v-model="uploadConfig.isPublic" type="checkbox" />
                公开文件（其他用户可见）
              </label>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeUploadDialog" class="btn btn-secondary">取消</button>
          <button 
            @click="startUpload" 
            :disabled="uploadQueue.length === 0 || uploading"
            class="btn btn-primary"
          >
            {{ uploading ? '上传中...' : `上传 ${uploadQueue.length} 个文件` }}
          </button>
        </div>
      </div>
    </div>

    <!-- 文件预览对话框 -->
    <div v-if="showPreviewDialog" class="modal-overlay" @click="closePreviewDialog">
      <div class="modal-content preview-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ previewFileData?.original_name }}</h3>
          <button @click="closePreviewDialog" class="close-btn">✕</button>
        </div>
        
        <div class="modal-body preview-body">
          <!-- 图片预览 -->
          <div v-if="previewFileData && isImageFile(previewFileData.file_type)" class="image-preview">
            <img :src="previewFileData.file_url" :alt="previewFileData.original_name" />
          </div>
          
          <!-- 视频预览 -->
          <div v-else-if="previewFileData && isVideoFile(previewFileData.file_type)" class="video-preview">
            <video controls>
              <source :src="previewFileData.file_url" :type="previewFileData.file_type">
              您的浏览器不支持视频播放
            </video>
          </div>
          
          <!-- 文档预览 -->
          <div v-else-if="previewFileData && isDocumentFile(previewFileData.file_type)" class="document-preview">
            <iframe :src="previewFileData.file_url" frameborder="0"></iframe>
          </div>
          
          <!-- 其他文件类型 -->
          <div v-else class="file-info-preview">
            <div class="file-icon-large">{{ getFileIcon(previewFileData?.file_type || '') }}</div>
            <div class="file-details">
              <h4>{{ previewFileData?.original_name }}</h4>
              <p>文件类型: {{ getFileTypeName(previewFileData?.file_type || '') }}</p>
              <p>文件大小: {{ formatFileSize(previewFileData?.file_size || 0) }}</p>
              <p>上传时间: {{ formatDate(previewFileData?.created_at || '') }}</p>
              <p v-if="previewFileData?.description">描述: {{ previewFileData.description }}</p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="downloadFile(previewFileData!)" class="btn btn-primary">下载文件</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'

// 接口定义
interface FileItem {
  id: number
  original_name: string
  file_name: string
  file_path: string
  file_url: string
  thumbnail_url?: string
  file_type: string
  file_size: number
  description?: string
  tags?: string[]
  uploader_id: number
  uploader_name: string
  download_count: number
  is_public: boolean
  created_at: string
  updated_at: string
}

interface UploadItem {
  file: File
  progress: number
  status: 'waiting' | 'uploading' | 'success' | 'error'
  error?: string
}

// 响应式数据
const loading = ref(false)
const uploading = ref(false)
const showUploadDialog = ref(false)
const showPreviewDialog = ref(false)
const viewMode = ref<'grid' | 'list'>('grid')
const isDragOver = ref(false)

const fileList = ref<FileItem[]>([])
const selectedFiles = ref<number[]>([])
const uploadQueue = ref<UploadItem[]>([])
const previewFileData = ref<FileItem | null>(null)
const fileInput = ref<HTMLInputElement>()

const searchParams = reactive({
  keyword: '',
  fileType: '',
  timeRange: '',
  sizeRange: '',
  page: 1,
  pageSize: 20
})

const pagination = reactive({
  total: 0,
  page: 1,
  pageSize: 20
})

const stats = reactive({
  totalFiles: 0,
  totalSize: 0,
  imageFiles: 0,
  documentFiles: 0
})

const uploadConfig = reactive({
  description: '',
  tags: '',
  isPublic: false
})

// 计算属性
const filteredFiles = computed(() => {
  let result = [...fileList.value]
  
  if (searchParams.keyword) {
    const keyword = searchParams.keyword.toLowerCase()
    result = result.filter(file => 
      file.original_name.toLowerCase().includes(keyword) ||
      file.description?.toLowerCase().includes(keyword)
    )
  }
  
  if (searchParams.fileType) {
    result = result.filter(file => {
      const type = getFileCategory(file.file_type)
      return type === searchParams.fileType
    })
  }
  
  if (searchParams.timeRange) {
    const now = new Date()
    const ranges = {
      today: 1,
      week: 7,
      month: 30,
      year: 365
    }
    const days = ranges[searchParams.timeRange as keyof typeof ranges]
    const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
    
    result = result.filter(file => new Date(file.created_at) >= cutoff)
  }
  
  if (searchParams.sizeRange) {
    result = result.filter(file => {
      const size = file.file_size
      switch (searchParams.sizeRange) {
        case 'small': return size < 1024 * 1024
        case 'medium': return size >= 1024 * 1024 && size < 10 * 1024 * 1024
        case 'large': return size >= 10 * 1024 * 1024 && size < 100 * 1024 * 1024
        case 'xlarge': return size >= 100 * 1024 * 1024
        default: return true
      }
    })
  }
  
  return result
})

const allSelected = computed(() => {
  return filteredFiles.value.length > 0 && selectedFiles.value.length === filteredFiles.value.length
})

const someSelected = computed(() => {
  return selectedFiles.value.length > 0 && selectedFiles.value.length < filteredFiles.value.length
})

// 工具函数
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getFileIcon = (fileType: string): string => {
  if (isImageFile(fileType)) return '🖼️'
  if (isVideoFile(fileType)) return '🎥'
  if (isAudioFile(fileType)) return '🎵'
  if (isDocumentFile(fileType)) return '📄'
  if (isArchiveFile(fileType)) return '📦'
  return '📁'
}

const getFileCategory = (fileType: string): string => {
  if (isImageFile(fileType)) return 'image'
  if (isVideoFile(fileType)) return 'video'
  if (isAudioFile(fileType)) return 'audio'
  if (isDocumentFile(fileType)) return 'document'
  if (isArchiveFile(fileType)) return 'archive'
  return 'other'
}

const getFileTypeName = (fileType: string): string => {
  const types: Record<string, string> = {
    'image/jpeg': 'JPEG图片',
    'image/png': 'PNG图片',
    'image/gif': 'GIF图片',
    'video/mp4': 'MP4视频',
    'video/avi': 'AVI视频',
    'audio/mp3': 'MP3音频',
    'audio/wav': 'WAV音频',
    'application/pdf': 'PDF文档',
    'application/msword': 'Word文档',
    'application/vnd.ms-excel': 'Excel表格',
    'text/plain': '文本文件',
    'application/zip': 'ZIP压缩包'
  }
  return types[fileType] || fileType
}

const isImageFile = (fileType: string): boolean => {
  return fileType.startsWith('image/')
}

const isVideoFile = (fileType: string): boolean => {
  return fileType.startsWith('video/')
}

const isAudioFile = (fileType: string): boolean => {
  return fileType.startsWith('audio/')
}

const isDocumentFile = (fileType: string): boolean => {
  return fileType.includes('pdf') || 
         fileType.includes('word') || 
         fileType.includes('excel') ||
         fileType.includes('powerpoint') ||
         fileType.startsWith('text/')
}

const isArchiveFile = (fileType: string): boolean => {
  return fileType.includes('zip') || 
         fileType.includes('rar') || 
         fileType.includes('tar') ||
         fileType.includes('gz')
}

// 数据加载
const loadFiles = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟数据
    fileList.value = [
      {
        id: 1,
        original_name: '系统架构图.png',
        file_name: 'sys_arch_20240101.png',
        file_path: '/uploads/images/sys_arch_20240101.png',
        file_url: '/api/files/download/1',
        thumbnail_url: '/api/files/thumbnail/1',
        file_type: 'image/png',
        file_size: 2048576,
        description: '系统整体架构设计图',
        tags: ['架构', '设计', '重要'],
        uploader_id: 1,
        uploader_name: '张三',
        download_count: 15,
        is_public: true,
        created_at: '2024-01-15 09:30:00',
        updated_at: '2024-01-15 09:30:00'
      },
      {
        id: 2,
        original_name: '需求文档.pdf',
        file_name: 'requirements_20240102.pdf',
        file_path: '/uploads/documents/requirements_20240102.pdf',
        file_url: '/api/files/download/2',
        file_type: 'application/pdf',
        file_size: 5242880,
        description: '项目需求分析文档',
        tags: ['需求', '文档'],
        uploader_id: 2,
        uploader_name: '李四',
        download_count: 8,
        is_public: false,
        created_at: '2024-01-14 14:20:00',
        updated_at: '2024-01-14 14:20:00'
      }
    ]
    
    updateStats()
    pagination.total = fileList.value.length
  } catch (error) {
    console.error('加载文件列表失败:', error)
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  stats.totalFiles = fileList.value.length
  stats.totalSize = fileList.value.reduce((total, file) => total + file.file_size, 0)
  stats.imageFiles = fileList.value.filter(file => isImageFile(file.file_type)).length
  stats.documentFiles = fileList.value.filter(file => isDocumentFile(file.file_type)).length
}

// 视图切换
const toggleView = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
}

// 搜索功能
const handleSearch = () => {
  // 搜索逻辑在计算属性中处理
}

const resetSearch = () => {
  searchParams.keyword = ''
  searchParams.fileType = ''
  searchParams.timeRange = ''
  searchParams.sizeRange = ''
}

// 文件选择
const selectFile = (file: FileItem) => {
  const index = selectedFiles.value.indexOf(file.id)
  if (index > -1) {
    selectedFiles.value.splice(index, 1)
  } else {
    selectedFiles.value.push(file.id)
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedFiles.value = []
  } else {
    selectedFiles.value = filteredFiles.value.map(file => file.id)
  }
}

// 文件操作
const downloadFile = (file: FileItem) => {
  window.open(file.file_url, '_blank')
  console.log('下载文件:', file.original_name)
}

const openPreviewFile = (file: FileItem) => {
  previewFileData.value = file
  showPreviewDialog.value = true
}

const editFile = (file: FileItem) => {
  console.log('编辑文件:', file)
  // TODO: 实现文件编辑功能
}

const deleteFile = async (file: FileItem) => {
  if (confirm(`确认删除文件 "${file.original_name}" 吗？此操作不可恢复！`)) {
    try {
      // 这里应该调用删除API
      const index = fileList.value.findIndex(f => f.id === file.id)
      if (index > -1) {
        fileList.value.splice(index, 1)
        updateStats()
      }
      console.log('删除成功')
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

// 批量操作
const batchDownload = () => {
  const files = fileList.value.filter(file => selectedFiles.value.includes(file.id))
  files.forEach(file => downloadFile(file))
  selectedFiles.value = []
}

const batchDelete = async () => {
  if (confirm(`确认删除选中的 ${selectedFiles.value.length} 个文件吗？此操作不可恢复！`)) {
    try {
      fileList.value = fileList.value.filter(file => !selectedFiles.value.includes(file.id))
      selectedFiles.value = []
      updateStats()
      console.log('批量删除成功')
    } catch (error) {
      console.error('批量删除失败:', error)
    }
  }
}

// 分页
const changePage = (page: number) => {
  searchParams.page = page
  loadFiles()
}

// 改变每页条数
const changePageSize = () => {
  searchParams.pageSize = pagination.pageSize
  searchParams.page = 1  // 重置到第一页
  pagination.page = 1
  loadFiles()
}

// 上传功能
const triggerFileSelect = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    addFilesToQueue(Array.from(files))
  }
}

const handleDragOver = (event: DragEvent) => {
  isDragOver.value = true
}

const handleDragLeave = (event: DragEvent) => {
  isDragOver.value = false
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  const files = Array.from(event.dataTransfer?.files || [])
  addFilesToQueue(files)
}

const addFilesToQueue = (files: File[]) => {
  const validFiles = files.filter(file => file.size <= 100 * 1024 * 1024) // 100MB限制
  
  validFiles.forEach(file => {
    uploadQueue.value.push({
      file,
      progress: 0,
      status: 'waiting'
    })
  })
  
  if (files.length > validFiles.length) {
    alert(`有 ${files.length - validFiles.length} 个文件超过100MB限制，已被忽略`)
  }
}

const removeFromQueue = (index: number) => {
  uploadQueue.value.splice(index, 1)
}

const startUpload = async () => {
  uploading.value = true
  
  for (const item of uploadQueue.value) {
    if (item.status !== 'waiting') continue
    
    item.status = 'uploading'
    
    try {
      // 模拟上传进度
      for (let i = 0; i <= 100; i += 10) {
        item.progress = i
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      item.status = 'success'
      
      // 添加到文件列表
      const newFile: FileItem = {
        id: Date.now() + Math.random(),
        original_name: item.file.name,
        file_name: `${Date.now()}_${item.file.name}`,
        file_path: `/uploads/${item.file.name}`,
        file_url: `/api/files/download/${Date.now()}`,
        file_type: item.file.type,
        file_size: item.file.size,
        description: uploadConfig.description,
        tags: uploadConfig.tags ? uploadConfig.tags.split(',').map(tag => tag.trim()) : [],
        uploader_id: 1,
        uploader_name: '当前用户',
        download_count: 0,
        is_public: uploadConfig.isPublic,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      fileList.value.unshift(newFile)
      
    } catch (error) {
      item.status = 'error'
      item.error = '上传失败'
    }
  }
  
  uploading.value = false
  updateStats()
  
  // 3秒后自动关闭对话框
  setTimeout(() => {
    closeUploadDialog()
  }, 3000)
}

const closeUploadDialog = () => {
  showUploadDialog.value = false
  uploadQueue.value = []
  uploadConfig.description = ''
  uploadConfig.tags = ''
  uploadConfig.isPublic = false
}

const closePreviewDialog = () => {
  showPreviewDialog.value = false
  previewFileData.value = null
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

const refreshFiles = () => loadFiles()

// 初始化
onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.file-management-container {
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
  font-size: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stats-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  font-size: 32px;
  opacity: 0.8;
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
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
  flex-wrap: wrap;
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
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #409eff;
}

.file-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.loading-spinner {
  font-size: 24px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 网格视图样式 */
.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px;
}

.file-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.file-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.file-card.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.file-preview {
  height: 120px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.file-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  font-size: 48px;
  opacity: 0.6;
}

.file-info {
  padding: 12px;
}

.file-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.file-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag {
  background: #e1f3ff;
  color: #409eff;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
}

.more-tags {
  background: #f0f2f5;
  color: #909399;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
}

.file-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  padding: 4px;
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s;
}

.file-card:hover .file-actions {
  opacity: 1;
}

.btn-icon {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: rgba(0, 0, 0, 0.1);
}

.btn-icon.btn-danger:hover {
  background: #f56c6c;
  color: white;
}

/* 列表视图样式 */
.file-table-container {
  overflow-x: auto;
}

.file-table {
  width: 100%;
  border-collapse: collapse;
}

.file-table th,
.file-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.file-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.file-table tbody tr:hover {
  background: #f8f9fa;
}

.file-table tbody tr.selected {
  background: #e3f2fd;
}

.file-name-cell .name-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon-small {
  font-size: 20px;
}

.name-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #303133;
}

.file-description {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.file-type-tag {
  background: #e1f3ff;
  color: #409eff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.actions {
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 16px;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 16px 24px;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 20px;
  z-index: 100;
}

.selected-info {
  color: #606266;
  font-size: 14px;
}

.batch-actions .actions {
  display: flex;
  gap: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-info {
  color: #606266;
  font-size: 14px;
}

.btn {
  padding: 10px 16px;
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

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  margin-right: 6px;
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

.btn-info {
  background: #909399;
  color: white;
}

.btn-info:hover {
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

/* Modal样式 */
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
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.upload-modal {
  max-width: 800px;
}

.preview-modal {
  max-width: 90%;
  max-height: 90%;
}

.modal-header {
  padding: 20px 30px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #909399;
  padding: 4px;
}

.close-btn:hover {
  color: #f56c6c;
}

.modal-body {
  padding: 30px;
  flex: 1;
  overflow-y: auto;
}

.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 上传区域样式 */
.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 20px;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.05);
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text p {
  margin: 8px 0;
  color: #606266;
}

.link-text {
  color: #409eff;
  text-decoration: underline;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

/* 上传队列样式 */
.upload-queue {
  margin-bottom: 20px;
}

.upload-queue h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.upload-list {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.upload-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f0f2f5;
}

.upload-item:last-child {
  border-bottom: none;
}

.upload-item .file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.upload-item .file-icon {
  font-size: 16px;
}

.file-details {
  flex: 1;
}

.upload-item .file-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.upload-item .file-size {
  font-size: 12px;
  color: #909399;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 120px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: #f0f2f5;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #409eff;
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
}

.upload-status {
  width: 60px;
  text-align: center;
}

.status {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.status.waiting {
  background: #f0f2f5;
  color: #909399;
}

.status.uploading {
  background: #e1f3ff;
  color: #409eff;
}

.status.success {
  background: #f0f9ff;
  color: #67c23a;
}

.status.error {
  background: #fef0f0;
  color: #f56c6c;
}

/* 上传设置样式 */
.upload-settings {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.upload-settings .form-group {
  margin-bottom: 16px;
}

.upload-settings label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.upload-settings input,
.upload-settings textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.upload-settings input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

/* 预览模态框样式 */
.preview-body {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.image-preview img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.video-preview video {
  max-width: 100%;
  max-height: 70vh;
}

.document-preview iframe {
  width: 100%;
  height: 70vh;
}

.file-info-preview {
  text-align: center;
}

.file-icon-large {
  font-size: 80px;
  color: #c0c4cc;
  margin-bottom: 20px;
}

.file-info-preview .file-details h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.file-info-preview .file-details p {
  margin: 8px 0;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-management-container {
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
  
  .search-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .file-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
    padding: 12px;
  }
  
  .file-table th,
  .file-table td {
    padding: 8px 12px;
    font-size: 14px;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .upload-area {
    padding: 20px;
  }
  
  .batch-actions {
    position: relative;
    left: auto;
    bottom: auto;
    transform: none;
    margin: 20px;
    border-radius: 8px;
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .file-grid {
    grid-template-columns: 1fr;
  }
  
  .batch-actions {
    flex-direction: column;
    gap: 12px;
  }
}

.row-number {
  text-align: center;
  font-weight: 500;
  color: #909399;
  font-size: 13px;
  width: 60px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size-label {
  color: #606266;
  font-size: 14px;
}

.page-size-select {
  padding: 4px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.pagination-center {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>