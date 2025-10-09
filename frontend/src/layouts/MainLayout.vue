<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <div class="layout-header">
      <div class="header-left">
        <div class="logo">
          <span class="logo-icon">🏢</span>
          <span class="logo-text">IT运维管理系统</span>
        </div>
        <button @click="toggleSidebar" class="sidebar-toggle">☰</button>
      </div>
      
      <div class="header-right">
        <div class="header-item notification" @click="showNotifications">
          <span class="notification-icon">🔔</span>
          <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
        </div>
        
        <div class="header-item user-info" @click="toggleUserMenu">
          <img :src="userAvatar" :alt="userName" class="user-avatar" />
          <span class="user-name">{{ userName }}</span>
          <span class="dropdown-arrow">▼</span>
          
          <div v-if="showUserMenu" class="user-dropdown">
            <a @click="goToProfile" class="dropdown-item">👤 个人中心</a>
            <a @click="logout" class="dropdown-item">🚪 退出登录</a>
          </div>
        </div>
      </div>
    </div>

    <div class="layout-body">
      <!-- 侧边栏 -->
      <div class="layout-sidebar" :class="{ 'is-collapsed': sidebarCollapsed }">
        <nav class="sidebar-nav">
          <router-link to="/app/dashboard" class="nav-item">
            <span class="nav-icon">📊</span>
            <span class="nav-text">仪表盘</span>
          </router-link>
          
          <div class="nav-group">
            <div class="nav-item nav-parent" @click="toggleMenu('assets')">
              <span class="nav-icon">📦</span>
              <span class="nav-text">资产管理</span>
              <span class="nav-arrow">›</span>
            </div>
            <div v-if="openMenus.assets" class="nav-children">
              <router-link to="/app/assets/list" class="nav-child">资产列表</router-link>
              <router-link to="/app/assets/create" class="nav-child">新增资产</router-link>
            </div>
          </div>
          
          <div class="nav-group">
            <div class="nav-item nav-parent" @click="toggleMenu('network')">
              <span class="nav-icon">🌐</span>
              <span class="nav-text">网络管理</span>
              <span class="nav-arrow">›</span>
            </div>
            <div v-if="openMenus.network" class="nav-children">
              <router-link to="/app/network/topology" class="nav-child">网络拓扑</router-link>
              <router-link to="/app/network/ports" class="nav-child">端口管理</router-link>
            </div>
          </div>
          
          <router-link to="/app/statistics" class="nav-item">
            <span class="nav-icon">📈</span>
            <span class="nav-text">统计分析</span>
          </router-link>
          
          <router-link to="/app/maintenance" class="nav-item">
            <span class="nav-icon">🔧</span>
            <span class="nav-text">运维记录</span>
          </router-link>
          
          <router-link to="/app/faults" class="nav-item">
            <span class="nav-icon">⚠️</span>
            <span class="nav-text">故障管理</span>
          </router-link>
          
          <router-link to="/app/files" class="nav-item">
            <span class="nav-icon">📁</span>
            <span class="nav-text">文件管理</span>
          </router-link>
          
          <router-link to="/app/locations" class="nav-item">
            <span class="nav-icon">📍</span>
            <span class="nav-text">位置管理</span>
          </router-link>
          
          <router-link to="/app/users" class="nav-item">
            <span class="nav-icon">👥</span>
            <span class="nav-text">用户管理</span>
          </router-link>
          
          <div class="nav-group">
            <div class="nav-item nav-parent" @click="toggleMenu('dictionary')">
              <span class="nav-icon">📚</span>
              <span class="nav-text">数据字典</span>
              <span class="nav-arrow">›</span>
            </div>
            <div v-if="openMenus.dictionary" class="nav-children">
              <router-link to="/app/categories" class="nav-child">类别管理</router-link>
              <router-link to="/app/dictionary/maintenance-types" class="nav-child">运维记录类型管理</router-link>
              <router-link to="/app/dictionary/maintenance-categories" class="nav-child">运维维护类别管理</router-link>
              <router-link to="/app/dictionary/departments" class="nav-child">组织机构管理</router-link>
            </div>
          </div>
          
          <router-link to="/app/settings" class="nav-item">
            <span class="nav-icon">⚙️</span>
            <span class="nav-text">系统设置</span>
          </router-link>
        </nav>
      </div>

      <!-- 主内容区 -->
      <div class="layout-content">
        <div class="content-header">
          <div class="breadcrumb">
            <span v-for="(item, index) in breadcrumbs" :key="index" class="breadcrumb-item">
              <router-link v-if="item.path" :to="item.path">{{ item.title }}</router-link>
              <span v-else>{{ item.title }}</span>
              <span v-if="index !== breadcrumbs.length - 1" class="separator">›</span>
            </span>
          </div>
          <button @click="refreshPage" class="refresh-btn">🔄</button>
        </div>
        
        <div class="content-main">
          <router-view />
        </div>
      </div>
    </div>

    <div v-if="showUserMenu || showNotificationPanel" class="layout-overlay" @click="closeAllDropdowns"></div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const sidebarCollapsed = ref(false)
const showUserMenu = ref(false)
const showNotificationPanel = ref(false)
const openMenus = ref({ assets: false, network: false, dictionary: false })
const unreadCount = ref(2)

const userName = computed(() => userStore.userInfo?.real_name || 'Admin')
const userAvatar = computed(() => '/default-avatar.jpg')

const breadcrumbs = computed(() => {
  const pathMap = {
    '/app/dashboard': [{ title: '仪表盘' }],
    '/app/assets/list': [
      { title: '资产管理', path: '/app/assets' }, 
      // 如果是网络设备视图，显示网络设备面包屑
      route.query.view === 'network' 
        ? { title: '网络设备' } 
        : { title: '资产列表' }
    ],
    '/app/assets/create': [{ title: '资产管理', path: '/app/assets' }, { title: '新增资产' }],
    '/app/network/topology': [{ title: '网络管理', path: '/app/network' }, { title: '网络拓扑' }],
    '/app/network/ports': [{ title: '网络管理', path: '/app/network' }, { title: '端口管理' }],
    '/app/statistics': [{ title: '统计分析' }],
    '/app/maintenance': [{ title: '运维记录' }],
    '/app/maintenance/create': [{ title: '运维记录', path: '/app/maintenance' }, { title: '新增记录' }],
    '/app/faults': [{ title: '故障管理' }],
    '/app/faults/create': [{ title: '故障管理', path: '/app/faults' }, { title: '新增故障' }],
    '/app/users': [{ title: '用户管理' }],
    '/app/users/create': [{ title: '用户管理', path: '/app/users' }, { title: '新增用户' }],
    '/app/files': [{ title: '文件管理' }],
    '/app/locations': [{ title: '位置管理' }],
    '/app/settings': [{ title: '系统设置' }],
    '/app/categories': [{ title: '数据字典', path: '/app/dictionary' }, { title: '类别管理' }],
    '/app/dictionary/maintenance-types': [{ title: '数据字典', path: '/app/dictionary' }, { title: '运维记录类型管理' }],
    '/app/dictionary/maintenance-categories': [{ title: '数据字典', path: '/app/dictionary' }, { title: '运维维护类别管理' }],
    '/app/dictionary/departments': [{ title: '数据字典', path: '/app/dictionary' }, { title: '组织机构管理' }]
  }
  
  // 处理动态路由（如详情页面）
  let currentPath = route.path
  let breadcrumb = pathMap[currentPath]
  
  if (!breadcrumb) {
    // 匹配动态路由
    if (currentPath.match(/\/app\/users\/\d+$/)) {
      breadcrumb = [{ title: '用户管理', path: '/app/users' }, { title: '用户详情' }]
    } else if (currentPath.match(/\/app\/users\/\d+\/edit$/)) {
      breadcrumb = [{ title: '用户管理', path: '/app/users' }, { title: '编辑用户' }]
    } else if (currentPath.match(/\/app\/network\/ports\/\d+$/)) {
      breadcrumb = [{ title: '网络管理', path: '/app/network' }, { title: '端口管理', path: '/app/network/ports' }, { title: '设备端口' }]
    } else if (currentPath.match(/\/app\/faults\/\d+$/)) {
      breadcrumb = [{ title: '故障管理', path: '/app/faults' }, { title: '故障详情' }]
    } else if (currentPath.match(/\/app\/faults\/\d+\/edit$/)) {
      breadcrumb = [{ title: '故障管理', path: '/app/faults' }, { title: '编辑故障' }]
    } else if (currentPath.match(/\/app\/maintenance\/\d+$/)) {
      breadcrumb = [{ title: '运维记录', path: '/app/maintenance' }, { title: '运维详情' }]
    } else if (currentPath.match(/\/app\/maintenance\/\d+\/edit$/)) {
      breadcrumb = [{ title: '运维记录', path: '/app/maintenance' }, { title: '编辑记录' }]
    } else {
      breadcrumb = [{ title: '未知页面' }]
    }
  }
  
  return breadcrumb
})

const toggleSidebar = () => sidebarCollapsed.value = !sidebarCollapsed.value
const toggleMenu = (key: string) => openMenus.value[key] = !openMenus.value[key]
const toggleUserMenu = () => showUserMenu.value = !showUserMenu.value
const showNotifications = () => showNotificationPanel.value = !showNotificationPanel.value
const closeAllDropdowns = () => { showUserMenu.value = false; showNotificationPanel.value = false }
const goToProfile = () => { router.push('/app/profile'); closeAllDropdowns() }
const logout = () => { userStore.logout(); router.push('/login'); closeAllDropdowns() }
const refreshPage = () => window.location.reload()

// 根据路由自动展开菜单
watch(() => route.path, (path) => {
  if (path.includes('/assets')) openMenus.value.assets = true
  if (path.includes('/network')) openMenus.value.network = true
  if (path.includes('/dictionary') || path.includes('/categories')) openMenus.value.dictionary = true
}, { immediate: true })
</script>

<style scoped>
.main-layout { height: 100vh; display: flex; flex-direction: column; background: #f5f7fa; }

.layout-header { 
  height: 60px; background: #fff; border-bottom: 1px solid #e6e6e6; 
  display: flex; justify-content: space-between; align-items: center; padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1); z-index: 100;
}

.header-left, .header-right { display: flex; align-items: center; gap: 20px; }

.logo { display: flex; align-items: center; gap: 8px; font-weight: 600; color: #303133; }
.logo-icon { font-size: 24px; }
.logo-text { font-size: 18px; }

.sidebar-toggle { background: none; border: none; font-size: 20px; cursor: pointer; }

.header-item { position: relative; cursor: pointer; display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 6px; }
.header-item:hover { background: #f5f7fa; }

.notification { position: relative; }
.notification-badge { position: absolute; top: -5px; right: -5px; background: #f56c6c; color: white; border-radius: 10px; font-size: 12px; min-width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; }

.user-avatar { width: 32px; height: 32px; border-radius: 50%; }
.user-name { font-weight: 500; color: #303133; }
.dropdown-arrow { font-size: 12px; color: #909399; }

.user-dropdown { position: absolute; top: 100%; right: 0; background: white; border: 1px solid #e6e6e6; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); min-width: 180px; padding: 8px 0; z-index: 1000; }
.dropdown-item { display: block; padding: 12px 16px; color: #606266; text-decoration: none; cursor: pointer; }
.dropdown-item:hover { background: #f5f7fa; color: #303133; }

.layout-body { flex: 1; display: flex; overflow: hidden; }

.layout-sidebar { width: 240px; background: #001529; transition: width 0.3s; overflow-y: auto; }
.layout-sidebar.is-collapsed { width: 64px; }

.sidebar-nav { padding: 20px 0; }

.nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 20px; color: #fff; text-decoration: none; cursor: pointer; }
.nav-item:hover { background: #1890ff; }
.nav-item.router-link-active { background: #1890ff; }

.nav-icon { font-size: 18px; min-width: 18px; }
.nav-text { font-size: 14px; white-space: nowrap; }
.nav-arrow { margin-left: auto; font-size: 12px; }

.is-collapsed .nav-text, .is-collapsed .nav-arrow { display: none; }

.nav-children { background: rgba(0,0,0,0.3); }
.nav-child { display: block; padding: 8px 20px 8px 52px; color: #d9d9d9; text-decoration: none; font-size: 13px; }
.nav-child:hover { background: rgba(24,144,255,0.3); color: #fff; }
.nav-child.router-link-active { background: rgba(24,144,255,0.5); color: #fff; }

.layout-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.content-header { height: 56px; background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; justify-content: space-between; align-items: center; padding: 0 24px; }

.breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.breadcrumb-item { color: #606266; }
.breadcrumb-item a { color: #1890ff; text-decoration: none; }
.separator { color: #c0c4cc; margin: 0 4px; }

.refresh-btn { border: 1px solid #d9d9d9; background: #fff; border-radius: 4px; cursor: pointer; padding: 8px; }

.content-main { flex: 1; overflow: auto; padding: 24px; }

.layout-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); z-index: 999; }

@media (max-width: 768px) {
  .layout-sidebar { position: fixed; top: 60px; left: 0; bottom: 0; z-index: 200; transform: translateX(-100%); }
  .layout-sidebar:not(.is-collapsed) { transform: translateX(0); }
  .logo-text, .user-name { display: none; }
  .content-main { padding: 16px; }
}
</style>