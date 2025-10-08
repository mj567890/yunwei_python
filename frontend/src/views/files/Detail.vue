<template>
  <div class="file-detail-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
          <div class="file-title">
            <h2>{{ fileInfo.name }}</h2>
            <el-tag :type="getFileTypeTag(fileInfo.type)" size="small">
              {{ getFileTypeName(fileInfo.type) }}
            </el-tag>
          </div>
        </div>
        <div class="header-actions">
          <el-dropdown @command="handleAction">
            <el-button type="primary">
              操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="download">下载文件</el-dropdown-item>
                <el-dropdown-item command="edit">编辑信息</el-dropdown-item>
                <el-dropdown-item command="share">分享文件</el-dropdown-item>
                <el-dropdown-item command="move">移动文件</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除文件</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <div class="page-content">
      <el-row :gutter="24">
        <el-col :span="16">
          <!-- 文件预览 -->
          <el-card title="文件预览" class="preview-card">
            <div class="file-preview">
              <div v-if="canPreview" class="preview-content">
                <!-- 图片预览 -->
                <img 
                  v-if="isImage" 
                  :src="fileInfo.url" 
                  :alt="fileInfo.name"
                  class="preview-image"
                />
                <!-- 文档预览 -->
                <div v-else-if="isDocument" class="document-preview">
                  <iframe 
                    :src="getDocumentPreviewUrl()" 
                    class="document-frame"
                    frameborder="0"
                  ></iframe>
                </div>
                <!-- 视频预览 -->
                <video 
                  v-else-if="isVideo" 
                  :src="fileInfo.url" 
                  controls 
                  class="preview-video"
                >
                  您的浏览器不支持视频播放
                </video>
                <!-- 音频预览 -->
                <audio 
                  v-else-if="isAudio" 
                  :src="fileInfo.url" 
                  controls 
                  class="preview-audio"
                >
                  您的浏览器不支持音频播放
                </audio>
              </div>
              
              <div v-else class="no-preview">
                <div class="file-icon">
                  <span class="icon">{{ getFileIcon(fileInfo.type) }}</span>
                </div>
                <p>此文件类型不支持预览</p>
                <el-button type="primary" @click="downloadFile">
                  <el-icon><Download /></el-icon>
                  下载查看
                </el-button>
              </div>
            </div>
          </el-card>

          <!-- 文件信息 -->
          <el-card title="文件信息" class="info-card">
            <div class="file-info">
              <div class="info-grid">
                <div class="info-item">
                  <label>文件名称</label>
                  <span>{{ fileInfo.name }}</span>
                </div>
                <div class="info-item">
                  <label>文件大小</label>
                  <span>{{ formatFileSize(fileInfo.size) }}</span>
                </div>
                <div class="info-item">
                  <label>文件类型</label>
                  <span>{{ fileInfo.mime_type }}</span>
                </div>
                <div class="info-item">
                  <label>文件扩展名</label>
                  <span>{{ getFileExtension(fileInfo.name) }}</span>
                </div>
                <div class="info-item">
                  <label>存储路径</label>
                  <span>{{ fileInfo.path }}</span>
                </div>
                <div class="info-item">
                  <label>MD5校验</label>
                  <span class="hash-value">{{ fileInfo.md5 || '计算中...' }}</span>
                </div>
                <div class="info-item">
                  <label>上传者</label>
                  <span>{{ fileInfo.uploader }}</span>
                </div>
                <div class="info-item">
                  <label>上传时间</label>
                  <span>{{ formatDate(fileInfo.created_at) }}</span>
                </div>
                <div class="info-item">
                  <label>最后修改</label>
                  <span>{{ formatDate(fileInfo.updated_at) }}</span>
                </div>
                <div class="info-item">
                  <label>下载次数</label>
                  <span>{{ fileInfo.download_count || 0 }}</span>
                </div>
                <div class="info-item full-width">
                  <label>文件描述</label>
                  <span>{{ fileInfo.description || '无描述' }}</span>
                </div>
                <div class="info-item full-width">
                  <label>标签</label>
                  <div class="file-tags">
                    <el-tag 
                      v-for="tag in fileInfo.tags" 
                      :key="tag"
                      size="small"
                      class="tag-item"
                    >
                      {{ tag }}
                    </el-tag>
                    <span v-if="!fileInfo.tags || fileInfo.tags.length === 0" class="no-tags">
                      暂无标签
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 版本历史 -->
          <el-card title="版本历史" class="version-card" v-if="fileVersions.length > 0">
            <el-table :data="fileVersions" stripe>
              <el-table-column prop="version" label="版本" width="80" />
              <el-table-column prop="size" label="大小" width="100">
                <template #default="{ row }">
                  {{ formatFileSize(row.size) }}
                </template>
              </el-table-column>
              <el-table-column prop="uploader" label="上传者" width="120" />
              <el-table-column prop="created_at" label="上传时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="comment" label="变更说明" />
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button size="small" @click="downloadVersion(row.id)">下载</el-button>
                  <el-button 
                    size="small" 
                    type="warning" 
                    @click="revertToVersion(row.id)"
                    v-if="row.version !== fileInfo.version"
                  >
                    恢复
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 快速操作 -->
          <el-card title="快速操作" class="actions-card">
            <div class="action-buttons">
              <el-button @click="downloadFile" :loading="downloading" type="primary" style="width: 100%">
                <el-icon><Download /></el-icon>
                下载文件
              </el-button>
              <el-button @click="shareFile" style="width: 100%">
                <el-icon><Share /></el-icon>
                分享文件
              </el-button>
              <el-button @click="editFile" style="width: 100%">
                <el-icon><Edit /></el-icon>
                编辑信息
              </el-button>
              <el-button @click="moveFile" style="width: 100%">
                <el-icon><FolderOpened /></el-icon>
                移动文件
              </el-button>
            </div>
          </el-card>

          <!-- 访问统计 -->
          <el-card title="访问统计" class="stats-card">
            <div class="stats-list">
              <div class="stat-item">
                <div class="stat-icon">📥</div>
                <div class="stat-content">
                  <div class="stat-value">{{ fileInfo.download_count || 0 }}</div>
                  <div class="stat-label">下载次数</div>
                </div>
              </div>
              
              <div class="stat-item">
                <div class="stat-icon">👁️</div>
                <div class="stat-content">
                  <div class="stat-value">{{ fileInfo.view_count || 0 }}</div>
                  <div class="stat-label">查看次数</div>
                </div>
              </div>
              
              <div class="stat-item">
                <div class="stat-icon">📤</div>
                <div class="stat-content">
                  <div class="stat-value">{{ fileInfo.share_count || 0 }}</div>
                  <div class="stat-label">分享次数</div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 相关文件 -->
          <el-card title="相关文件" class="related-card" v-if="relatedFiles.length > 0">
            <div class="related-list">
              <div v-for="file in relatedFiles" :key="file.id" class="related-item" @click="viewFile(file.id)">
                <div class="file-icon-small">{{ getFileIcon(file.type) }}</div>
                <div class="file-info-small">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-meta">{{ formatFileSize(file.size) }}</div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 权限信息 -->
          <el-card title="权限信息" class="permissions-card">
            <div class="permission-list">
              <div class="permission-item">
                <span class="permission-label">所有者：</span>
                <span class="permission-value">{{ fileInfo.owner || fileInfo.uploader }}</span>
              </div>
              <div class="permission-item">
                <span class="permission-label">访问权限：</span>
                <el-tag :type="getPermissionType(fileInfo.permission)" size="small">
                  {{ getPermissionText(fileInfo.permission) }}
                </el-tag>
              </div>
              <div class="permission-item">
                <span class="permission-label">是否公开：</span>
                <el-tag :type="fileInfo.is_public ? 'success' : 'info'" size="small">
                  {{ fileInfo.is_public ? '公开' : '私有' }}
                </el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, Download, Share, Edit, FolderOpened } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const fileId = route.params.id as string
const downloading = ref(false)

const fileInfo = ref({
  id: '',
  name: '',
  size: 0,
  type: '',
  mime_type: '',
  path: '',
  url: '',
  md5: '',
  uploader: '',
  owner: '',
  permission: 'read',
  is_public: false,
  description: '',
  tags: [] as string[],
  download_count: 0,
  view_count: 0,
  share_count: 0,
  version: '1.0',
  created_at: '',
  updated_at: ''
})

const fileVersions = ref([
  {
    id: 1,
    version: '1.0',
    size: 2048576,
    uploader: '张三',
    created_at: '2024-01-15 14:30:00',
    comment: '初始版本'
  }
])

const relatedFiles = ref([
  {
    id: 2,
    name: '相关文档.pdf',
    type: 'pdf',
    size: 1024000
  },
  {
    id: 3,
    name: '备份文件.zip',
    type: 'zip',
    size: 5120000
  }
])

const canPreview = computed(() => {
  return isImage.value || isDocument.value || isVideo.value || isAudio.value
})

const isImage = computed(() => {
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(getFileExtension(fileInfo.value.name).toLowerCase())
})

const isDocument = computed(() => {
  return ['pdf', 'doc', 'docx', 'txt'].includes(getFileExtension(fileInfo.value.name).toLowerCase())
})

const isVideo = computed(() => {
  return ['mp4', 'avi', 'mov', 'wmv', 'flv'].includes(getFileExtension(fileInfo.value.name).toLowerCase())
})

const isAudio = computed(() => {
  return ['mp3', 'wav', 'flac', 'aac'].includes(getFileExtension(fileInfo.value.name).toLowerCase())
})

const loadFileData = async () => {
  try {
    // 模拟API调用
    const mockFile = {
      id: fileId,
      name: 'IT运维系统架构图.pdf',
      size: 2048576,
      type: 'pdf',
      mime_type: 'application/pdf',
      path: '/files/2024/01/architecture.pdf',
      url: '/api/files/download/' + fileId,
      md5: 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6',
      uploader: '张三',
      owner: '李四',
      permission: 'read',
      is_public: false,
      description: '系统架构设计文档，包含详细的技术架构说明',
      tags: ['架构', '设计', '文档'],
      download_count: 25,
      view_count: 156,
      share_count: 8,
      version: '1.0',
      created_at: '2024-01-15 14:30:00',
      updated_at: '2024-01-15 14:30:00'
    }
    
    fileInfo.value = mockFile
  } catch (error) {
    console.error('加载文件数据失败:', error)
    ElMessage.error('加载文件数据失败')
  }
}

const getFileExtension = (filename: string) => {
  return filename.split('.').pop() || ''
}

const getFileIcon = (type: string) => {
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
    'gif': '🖼️',
    'mp4': '🎬',
    'avi': '🎬',
    'mp3': '🎵',
    'wav': '🎵'
  }
  return iconMap[type.toLowerCase()] || '📁'
}

const getFileTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'pdf': 'PDF文档',
    'doc': 'Word文档',
    'docx': 'Word文档',
    'xls': 'Excel表格',
    'xlsx': 'Excel表格',
    'ppt': 'PowerPoint',
    'pptx': 'PowerPoint',
    'txt': '文本文件',
    'zip': '压缩包',
    'rar': '压缩包',
    'jpg': '图片',
    'jpeg': '图片',
    'png': '图片',
    'gif': '动图',
    'mp4': '视频',
    'avi': '视频',
    'mp3': '音频',
    'wav': '音频'
  }
  return typeMap[type.toLowerCase()] || '未知类型'
}

const getFileTypeTag = (type: string) => {
  const tagMap: Record<string, string> = {
    'pdf': 'danger',
    'doc': 'primary',
    'docx': 'primary',
    'xls': 'success',
    'xlsx': 'success',
    'txt': 'info',
    'zip': 'warning',
    'jpg': 'success',
    'png': 'success',
    'mp4': 'warning',
    'mp3': 'info'
  }
  return tagMap[type.toLowerCase()] || 'info'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const getDocumentPreviewUrl = () => {
  // 这里可以使用文档预览服务
  return `/api/files/preview/${fileId}`
}

const getPermissionType = (permission: string) => {
  const typeMap: Record<string, string> = {
    'read': 'info',
    'write': 'warning',
    'admin': 'danger'
  }
  return typeMap[permission] || 'info'
}

const getPermissionText = (permission: string) => {
  const textMap: Record<string, string> = {
    'read': '只读',
    'write': '读写',
    'admin': '管理'
  }
  return textMap[permission] || '未知'
}

const handleAction = (command: string) => {
  switch (command) {
    case 'download':
      downloadFile()
      break
    case 'edit':
      editFile()
      break
    case 'share':
      shareFile()
      break
    case 'move':
      moveFile()
      break
    case 'delete':
      deleteFile()
      break
  }
}

const downloadFile = async () => {
  downloading.value = true
  try {
    // 模拟下载
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = fileInfo.value.url
    link.download = fileInfo.value.name
    link.click()
    
    ElMessage.success('文件下载完成')
    
    // 更新下载次数
    fileInfo.value.download_count++
  } catch (error) {
    ElMessage.error('文件下载失败')
  } finally {
    downloading.value = false
  }
}

const shareFile = () => {
  ElMessage.info('文件分享功能开发中...')
}

const editFile = () => {
  router.push(`/app/files/${fileId}/edit`)
}

const moveFile = () => {
  ElMessage.info('文件移动功能开发中...')
}

const deleteFile = async () => {
  try {
    await ElMessageBox.confirm('确定要删除此文件吗？此操作不可恢复。', '确认删除', {
      type: 'warning'
    })
    
    ElMessage.success('文件删除成功')
    router.push('/app/files')
  } catch {
    // 用户取消
  }
}

const downloadVersion = (versionId: number) => {
  ElMessage.info(`下载版本 ${versionId}...`)
}

const revertToVersion = async (versionId: number) => {
  try {
    await ElMessageBox.confirm('确定要恢复到此版本吗？', '确认恢复', {
      type: 'warning'
    })
    
    ElMessage.success('版本恢复成功')
    await loadFileData()
  } catch {
    // 用户取消
  }
}

const viewFile = (id: number) => {
  router.push(`/app/files/${id}`)
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadFileData()
})
</script>

<style scoped>
.file-detail-page {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.file-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.page-content {
  padding: 24px;
}

.preview-card,
.info-card,
.version-card {
  margin-bottom: 24px;
}

.preview-card :deep(.el-card__header),
.info-card :deep(.el-card__header),
.version-card :deep(.el-card__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  font-weight: 500;
}

.file-preview {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.document-frame {
  width: 100%;
  height: 400px;
  border-radius: 8px;
}

.preview-video {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.preview-audio {
  width: 100%;
}

.no-preview {
  text-align: center;
  color: #909399;
}

.file-icon .icon {
  font-size: 64px;
  margin-bottom: 16px;
  display: block;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.info-item span {
  color: #303133;
  word-break: break-word;
}

.hash-value {
  font-family: monospace;
  font-size: 12px;
}

.file-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  margin: 0;
}

.no-tags {
  color: #c0c4cc;
  font-style: italic;
}

.actions-card {
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stats-card {
  margin-bottom: 24px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-icon {
  font-size: 20px;
  min-width: 20px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.related-card {
  margin-bottom: 24px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.related-item:hover {
  background: #e9ecef;
}

.file-icon-small {
  font-size: 16px;
  min-width: 16px;
}

.file-info-small {
  flex: 1;
}

.file-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 2px;
}

.file-meta {
  font-size: 12px;
  color: #909399;
}

.permissions-card {
  margin-bottom: 24px;
}

.permission-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.permission-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.permission-label {
  font-size: 14px;
  color: #606266;
}

.permission-value {
  font-weight: 500;
  color: #303133;
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
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .file-preview {
    min-height: 300px;
  }
}
</style>