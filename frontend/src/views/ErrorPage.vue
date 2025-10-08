<template>
  <div class="error-page">
    <div class="error-container">
      <div class="error-content">
        <div class="error-illustration">
          <div class="error-code">{{ errorCode }}</div>
          <div class="error-icon">{{ getErrorIcon() }}</div>
        </div>
        
        <div class="error-info">
          <h1>{{ getErrorTitle() }}</h1>
          <p class="error-description">{{ getErrorDescription() }}</p>
          
          <div class="error-suggestions" v-if="getSuggestions().length > 0">
            <h3>可能的解决方案：</h3>
            <ul>
              <li v-for="suggestion in getSuggestions()" :key="suggestion">
                {{ suggestion }}
              </li>
            </ul>
          </div>
        </div>
        
        <div class="error-actions">
          <el-button type="primary" @click="goHome" size="large">
            <el-icon><House /></el-icon>
            返回首页
          </el-button>
          <el-button @click="goBack" size="large">
            <el-icon><ArrowLeft /></el-icon>
            返回上页
          </el-button>
          <el-button @click="refresh" size="large">
            <el-icon><Refresh /></el-icon>
            刷新页面
          </el-button>
        </div>
        
        <div class="error-help">
          <p>如果问题持续存在，请联系系统管理员</p>
          <div class="help-links">
            <a href="#" @click="reportProblem">反馈问题</a>
            <span>|</span>
            <a href="#" @click="viewHelp">帮助文档</a>
          </div>
        </div>
      </div>
      
      <div class="error-details" v-if="showDetails">
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="错误详情" name="details">
            <div class="detail-item">
              <strong>时间：</strong> {{ new Date().toLocaleString() }}
            </div>
            <div class="detail-item">
              <strong>请求路径：</strong> {{ $route.path }}
            </div>
            <div class="detail-item">
              <strong>用户代理：</strong> {{ userAgent }}
            </div>
            <div class="detail-item" v-if="errorDetails">
              <strong>错误信息：</strong> {{ errorDetails }}
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { House, ArrowLeft, Refresh } from '@element-plus/icons-vue'

interface Props {
  code?: number | string
  message?: string
  details?: string
}

const props = withDefaults(defineProps<Props>(), {
  code: 404,
  message: '',
  details: ''
})

const route = useRoute()
const router = useRouter()

const showDetails = ref(false)
const activeCollapse = ref([''])

const errorCode = computed(() => {
  const queryCode = Array.isArray(route.query.code) ? route.query.code[0] : route.query.code
  return props.code || queryCode || 404
})

const errorDetails = computed(() => {
  const queryDetails = Array.isArray(route.query.details) ? route.query.details[0] : route.query.details
  return props.details || queryDetails || ''
})

const userAgent = computed(() => {
  return typeof window !== 'undefined' ? window.navigator.userAgent : ''
})

const getErrorIcon = () => {
  const iconMap: Record<string | number, string> = {
    400: '🤔',
    401: '🔐',
    403: '🚫', 
    404: '🔍',
    500: '💥',
    502: '⚠️',
    503: '🔧'
  }
  return iconMap[errorCode.value] || '❓'
}

const getErrorTitle = () => {
  const titleMap: Record<string | number, string> = {
    400: '请求错误',
    401: '未经授权',
    403: '访问被拒绝',
    404: '页面未找到',
    500: '服务器内部错误',
    502: '网关错误',
    503: '服务不可用'
  }
  return props.message || titleMap[errorCode.value] || '未知错误'
}

const getErrorDescription = () => {
  const descMap: Record<string | number, string> = {
    400: '您的请求有误，请检查请求参数。',
    401: '您需要登录后才能访问此页面。',
    403: '您没有权限访问此页面或资源。',
    404: '抱歉，您访问的页面不存在或已被移动。',
    500: '服务器遇到了一个意外的情况，无法完成您的请求。',
    502: '网关或代理服务器从上游服务器接收到无效响应。',
    503: '服务暂时不可用，可能正在维护中。'
  }
  return descMap[errorCode.value] || '发生了一个未知错误。'
}

const getSuggestions = () => {
  const suggestionMap: Record<string | number, string[]> = {
    400: [
      '检查URL地址是否正确',
      '确认请求参数格式正确',
      '联系技术支持获取帮助'
    ],
    401: [
      '重新登录您的账户',
      '检查登录凭证是否过期',
      '清除浏览器缓存和Cookie'
    ],
    403: [
      '联系管理员申请相关权限',
      '确认您的账户状态正常',
      '尝试使用其他账户登录'
    ],
    404: [
      '检查URL地址是否正确',
      '使用导航菜单重新访问',
      '通过搜索功能查找所需内容',
      '返回首页重新开始'
    ],
    500: [
      '稍后再试',
      '刷新页面',
      '联系系统管理员',
      '检查网络连接'
    ],
    502: [
      '稍后再试',
      '检查网络连接',
      '联系系统管理员'
    ],
    503: [
      '等待系统维护完成',
      '稍后再试',
      '关注系统公告'
    ]
  }
  return suggestionMap[errorCode.value] || [
    '刷新页面重试',
    '检查网络连接',
    '联系技术支持'
  ]
}

const goHome = () => {
  router.push('/app/dashboard')
}

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/app/dashboard')
  }
}

const refresh = () => {
  window.location.reload()
}

const reportProblem = () => {
  ElMessage.info('问题反馈功能开发中...')
  // 这里可以打开问题反馈表单或发送错误报告
}

const viewHelp = () => {
  ElMessage.info('帮助文档功能开发中...')
  // 这里可以打开帮助文档页面
}

const toggleDetails = () => {
  showDetails.value = !showDetails.value
}
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.error-container {
  max-width: 600px;
  width: 100%;
}

.error-content {
  background: white;
  border-radius: 16px;
  padding: 48px 32px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.error-illustration {
  margin-bottom: 32px;
}

.error-code {
  font-size: 72px;
  font-weight: 700;
  color: #409eff;
  line-height: 1;
  margin-bottom: 16px;
  background: linear-gradient(45deg, #409eff, #67c23a);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 24px;
  opacity: 0.8;
}

.error-info h1 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.error-description {
  font-size: 16px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 24px;
}

.error-suggestions {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 32px;
  text-align: left;
}

.error-suggestions h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.error-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.error-suggestions li {
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.error-help {
  border-top: 1px solid #f0f0f0;
  padding-top: 24px;
  color: #909399;
  font-size: 14px;
}

.help-links {
  margin-top: 8px;
}

.help-links a {
  color: #409eff;
  text-decoration: none;
  margin: 0 8px;
}

.help-links a:hover {
  text-decoration: underline;
}

.error-details {
  background: white;
  border-radius: 16px;
  margin-top: 20px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.detail-item {
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
  word-break: break-all;
}

.detail-item strong {
  color: #303133;
}

@media (max-width: 768px) {
  .error-content {
    padding: 32px 24px;
  }
  
  .error-code {
    font-size: 56px;
  }
  
  .error-icon {
    font-size: 48px;
  }
  
  .error-info h1 {
    font-size: 24px;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .error-actions .el-button {
    width: 200px;
  }
}

@media (max-width: 480px) {
  .error-page {
    padding: 10px;
  }
  
  .error-content {
    padding: 24px 16px;
  }
  
  .error-code {
    font-size: 48px;
  }
  
  .error-suggestions {
    padding: 16px;
  }
}
</style>