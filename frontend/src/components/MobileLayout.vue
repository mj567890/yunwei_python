// @ts-nocheck
<template>
  <div class="mobile-layout" :class="{ 'is-mobile': isMobile }">
    <!-- 移动端顶部导航栏 -->
    <div v-if="isMobile" class="mobile-header">
      <div class="header-left">
        <el-button 
          v-if="showBack" 
          text 
          class="back-button" 
          @click="$emit('back')"
        >
          <i class="el-icon-arrow-left"></i>
        </el-button>
        <el-button 
          text 
          class="menu-button" 
          @click="toggleSidebar"
        >
          <i class="el-icon-menu"></i>
        </el-button>
      </div>
      
      <div class="header-center">
        <h3 class="page-title">{{ title }}</h3>
      </div>
      
      <div class="header-right">
        <slot name="header-actions">
          <el-button text class="user-button" @click="showUserMenu = !showUserMenu">
            <i class="el-icon-user"></i>
          </el-button>
        </slot>
      </div>
    </div>

    <!-- 移动端侧边栏 -->
    <div 
      v-if="isMobile" 
      class="mobile-sidebar-overlay" 
      :class="{ 'visible': sidebarVisible }"
      @click="closeSidebar"
    >
      <div class="mobile-sidebar" @click.stop>
        <div class="sidebar-header">
          <div class="user-info">
            <div class="avatar">
              <i class="el-icon-user"></i>
            </div>
            <div class="user-details">
              <div class="username">{{ userStore.userInfo?.username || '用户' }}</div>
              <div class="role">{{ userStore.userInfo?.roles?.[0]?.name || '普通用户' }}</div>
            </div>
          </div>
          <el-button text class="close-button" @click="closeSidebar">
            <i class="el-icon-close"></i>
          </el-button>
        </div>
        
        <div class="sidebar-menu">
          <div 
            v-for="item in menuItems" 
            :key="item.path"
            class="menu-item"
            :class="{ 'active': currentPath === item.path }"
            @click="navigateTo(item.path)"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </div>
        </div>
        
        <div class="sidebar-footer">
          <el-button class="logout-button" @click="handleLogout">
            <i class="el-icon-switch-button"></i>
            退出登录
          </el-button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content" :class="{ 'with-mobile-header': isMobile }">
      <slot></slot>
    </div>

    <!-- 移动端底部导航栏 -->
    <div v-if="isMobile && showBottomNav" class="mobile-bottom-nav">
      <div 
        v-for="item in bottomNavItems" 
        :key="item.path"
        class="nav-item"
        :class="{ 'active': currentPath === item.path }"
        @click="navigateTo(item.path)"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </div>
    </div>

    <!-- 移动端用户菜单 -->
    <div 
      v-if="isMobile && showUserMenu" 
      class="mobile-user-menu"
      @click="showUserMenu = false"
    >
      <div class="user-menu-content" @click.stop>
        <div class="menu-item" @click="navigateTo('/app/profile')">
          <i class="el-icon-user"></i>
          <span>个人信息</span>
        </div>
        <div class="menu-item" @click="navigateTo('/app/settings')">
          <i class="el-icon-setting"></i>
          <span>设置</span>
        </div>
        <div class="menu-item" @click="handleLogout">
          <i class="el-icon-switch-button"></i>
          <span>退出登录</span>
        </div>
      </div>
    </div>

    <!-- 移动端加载遮罩 -->
    <div v-if="loading" class="mobile-loading">
      <div class="loading-content">
        <i class="el-icon-loading"></i>
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { isMobile as checkIsMobile } from '@/utils/mobile'
import { useUserStore } from '@/stores/user'

interface MenuItem {
  path: string
  label: string
  icon: string
}

interface Props {
  title?: string
  showBack?: boolean
  showBottomNav?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: 'IT运维管理系统',
  showBack: false,
  showBottomNav: true,
  loading: false
})

const emit = defineEmits<{
  back: []
}>()

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 响应式状态
const isMobile = ref(false)
const sidebarVisible = ref(false)
const showUserMenu = ref(false)

// 当前路径
const currentPath = computed(() => route.path)

// 菜单项配置
const menuItems: MenuItem[] = [
  { path: '/app/dashboard', label: '仪表板', icon: 'el-icon-odometer' },
  { path: '/app/assets', label: '资产管理', icon: 'el-icon-box' },
  { path: '/app/network', label: '网络设备', icon: 'el-icon-connection' },
  { path: '/app/maintenance', label: '运维记录', icon: 'el-icon-tools' },
  { path: '/app/faults', label: '故障管理', icon: 'el-icon-warning' },
  { path: '/app/statistics', label: '统计分析', icon: 'el-icon-data-analysis' }
]

// 底部导航项
const bottomNavItems: MenuItem[] = [
  { path: '/app/dashboard', label: '首页', icon: 'el-icon-house' },
  { path: '/app/assets', label: '资产', icon: 'el-icon-box' },
  { path: '/app/maintenance', label: '运维', icon: 'el-icon-tools' },
  { path: '/app/statistics', label: '统计', icon: 'el-icon-data-analysis' }
]

// 事件处理
const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
}

const closeSidebar = () => {
  sidebarVisible.value = false
}

const navigateTo = (path: string) => {
  router.push(path)
  closeSidebar()
  showUserMenu.value = false
}

const handleLogout = async () => {
  try {
    await userStore.logout()
    router.push('/login')
    ElMessage.success('退出登录成功')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}

// 检测设备类型
const checkDeviceType = () => {
  isMobile.value = checkIsMobile() || window.innerWidth <= 768
}

// 监听窗口大小变化
const handleResize = () => {
  checkDeviceType()
  if (!isMobile.value) {
    sidebarVisible.value = false
    showUserMenu.value = false
  }
}

// 生命周期
onMounted(() => {
  checkDeviceType()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.mobile-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 移动端顶部导航栏 */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left,
.header-right {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
}

.header-center {
  flex: 1;
  text-align: center;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.back-button,
.menu-button,
.user-button {
  width: 40px;
  height: 40px;
  padding: 0;
  font-size: 20px;
}

/* 移动端侧边栏 */
.mobile-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1500;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.mobile-sidebar-overlay.visible {
  opacity: 1;
  visibility: visible;
}

.mobile-sidebar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 280px;
  background: #fff;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
}

.mobile-sidebar-overlay.visible .mobile-sidebar {
  transform: translateX(0);
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  margin-right: 12px;
}

.user-details {
  flex: 1;
}

.username {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.role {
  font-size: 12px;
  color: #909399;
}

.close-button {
  width: 32px;
  height: 32px;
  padding: 0;
  font-size: 16px;
}

.sidebar-menu {
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background: #f5f7fa;
}

.menu-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.menu-item i {
  width: 20px;
  margin-right: 12px;
  font-size: 16px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}

.logout-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-button i {
  margin-right: 8px;
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  min-height: 0;
}

.main-content.with-mobile-header {
  padding-top: 56px;
}

.is-mobile .main-content.with-mobile-header {
  padding-bottom: 60px; /* 为底部导航栏留空间 */
}

/* 移动端底部导航栏 */
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  display: flex;
  z-index: 1000;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 8px 4px;
  transition: color 0.2s;
  color: #909399;
}

.nav-item.active {
  color: #409eff;
}

.nav-item i {
  font-size: 20px;
  margin-bottom: 4px;
}

.nav-item span {
  font-size: 12px;
}

/* 移动端用户菜单 */
.mobile-user-menu {
  position: fixed;
  top: 56px;
  right: 0;
  width: 200px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1200;
  margin: 8px;
}

.user-menu-content {
  padding: 8px 0;
}

.user-menu-content .menu-item {
  padding: 12px 16px;
  border-radius: 0;
}

/* 移动端加载遮罩 */
.mobile-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.loading-content {
  text-align: center;
  color: #909399;
}

.loading-content i {
  font-size: 32px;
  margin-bottom: 12px;
  display: block;
}

.loading-content p {
  margin: 0;
  font-size: 14px;
}

/* 安全区域适配 */
@supports (padding: max(0px)) {
  .mobile-header {
    padding-top: max(env(safe-area-inset-top), 0px);
    height: calc(56px + max(env(safe-area-inset-top), 0px));
  }
  
  .main-content.with-mobile-header {
    padding-top: calc(56px + max(env(safe-area-inset-top), 0px));
  }
  
  .mobile-bottom-nav {
    padding-bottom: max(env(safe-area-inset-bottom), 0px);
    height: calc(60px + max(env(safe-area-inset-bottom), 0px));
  }
  
  .is-mobile .main-content.with-mobile-header {
    padding-bottom: calc(60px + max(env(safe-area-inset-bottom), 0px));
  }
}

/* 横屏优化 */
@media screen and (orientation: landscape) and (max-height: 500px) {
  .mobile-header {
    height: 48px;
  }
  
  .main-content.with-mobile-header {
    padding-top: 48px;
  }
  
  .mobile-bottom-nav {
    height: 50px;
  }
  
  .is-mobile .main-content.with-mobile-header {
    padding-bottom: 50px;
  }
}

/* 触控优化 */
.menu-item,
.nav-item,
.back-button,
.menu-button,
.user-button {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* 滚动优化 */
.sidebar-menu,
.main-content {
  -webkit-overflow-scrolling: touch;
}
</style>