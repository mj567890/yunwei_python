import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getSecureToken, isTokenExpired } from '@/utils/crypto'

const routes = [
  {
    path: '/',
    name: 'Root',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '首页',
      hideInMenu: true,
      noAuth: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      hideInMenu: true,
      noAuth: true
    }
  },
  {
    path: '/app',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Monitor' }
      },
      {
        path: 'assets',
        name: 'Assets',
        component: () => import('@/views/assets/Index.vue'),
        meta: { title: '资产管理' }
      },
      {
        path: 'assets/list',
        name: 'AssetList',
        component: () => import('@/views/assets/List.vue'),
        meta: { title: '资产列表' }
      },
      {
        path: 'assets/create',
        name: 'AssetCreate',
        component: () => import('@/views/assets/Form.vue'),
        meta: { title: '新增资产' }
      },
      {
        path: 'assets/edit/:id',
        name: 'AssetEdit',
        component: () => import('@/views/assets/Form.vue'),
        meta: { title: '编辑资产' }
      },
      {
        path: 'assets/:id',
        name: 'AssetDetail',
        component: () => import('@/views/assets/Detail.vue'),
        meta: { title: '资产详情' }
      },
      {
        path: 'network/topology',
        name: 'NetworkTopology',
        component: () => import('@/views/network/Topology.vue'),
        meta: { title: '网络拓扑' }
      },
      {
        path: 'network/devices',
        name: 'NetworkDevices',
        redirect: () => {
          // 跳转到资产管理的网络设备视图
          return { path: '/app/assets/list', query: { view: 'network' } }
        },
        meta: { title: '设备管理' }
      },
      {
        path: 'network/ports',
        name: 'NetworkPorts',
        component: () => import('@/views/network/Ports.vue'),
        meta: { title: '端口管理' }
      },
      {
        path: 'network/ports/:assetId',
        name: 'AssetPorts',
        component: () => import('@/views/network/AssetPorts.vue'),
        meta: { title: '设备端口' }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/statistics/Index.vue'),
        meta: { title: '统计分析' }
      },
      {
        path: 'maintenance',
        name: 'Maintenance',
        component: () => import('@/views/maintenance/Index.vue'),
        meta: { title: '运维记录' }
      },
      {
        path: 'maintenance/:id',
        name: 'MaintenanceDetail',
        component: () => import('@/views/maintenance/Detail.vue'),
        meta: { title: '运维详情' }
      },
      {
        path: 'maintenance/create',
        name: 'MaintenanceCreate',
        component: () => import('@/views/maintenance/Form.vue'),
        meta: { title: '新增运维记录' }
      },
      {
        path: 'maintenance/:id/edit',
        name: 'MaintenanceEdit',
        component: () => import('@/views/maintenance/Form.vue'),
        meta: { title: '编辑运维记录' }
      },
      {
        path: 'faults',
        name: 'Faults',
        component: () => import('@/views/faults/Index.vue'),
        meta: { title: '故障管理' }
      },
      {
        path: 'faults/:id',
        name: 'FaultDetail',
        component: () => import('@/views/faults/Detail.vue'),
        meta: { title: '故障详情' }
      },
      {
        path: 'faults/create',
        name: 'FaultCreate',
        component: () => import('@/views/faults/Form.vue'),
        meta: { title: '新增故障' }
      },
      {
        path: 'faults/:id/edit',
        name: 'FaultEdit',
        component: () => import('@/views/faults/Form.vue'),
        meta: { title: '编辑故障' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/Index.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'users/:id',
        name: 'UserDetail',
        component: () => import('@/views/users/Detail.vue'),
        meta: { title: '用户详情' }
      },
      {
        path: 'users/create',
        name: 'UserCreate',
        component: () => import('@/views/users/Form.vue'),
        meta: { title: '新增用户' }
      },
      {
        path: 'users/:id/edit',
        name: 'UserEdit',
        component: () => import('@/views/users/Form.vue'),
        meta: { title: '编辑用户' }
      },
      {
        path: 'files',
        name: 'Files',
        component: () => import('@/views/files/Index.vue'),
        meta: { title: '文件管理' }
      },
      {
        path: 'files/:id',
        name: 'FileDetail',
        component: () => import('@/views/files/Detail.vue'),
        meta: { title: '文件详情' }
      },
      {
        path: 'files/create',
        name: 'FileCreate',
        component: () => import('@/views/files/Form.vue'),
        meta: { title: '上传文件' }
      },
      {
        path: 'files/:id/edit',
        name: 'FileEdit',
        component: () => import('@/views/files/Form.vue'),
        meta: { title: '编辑文件' }
      },
      {
        path: 'locations',
        name: 'Locations',
        component: () => import('@/views/locations/Index.vue'),
        meta: { title: '位置管理' }
      },
      {
        path: 'locations/:id',
        name: 'LocationDetail',
        component: () => import('@/views/locations/Detail.vue'),
        meta: { title: '位置详情' }
      },
      {
        path: 'locations/create',
        name: 'LocationCreate',
        component: () => import('@/views/locations/Form.vue'),
        meta: { title: '新增位置' }
      },
      {
        path: 'locations/:id/edit',
        name: 'LocationEdit',
        component: () => import('@/views/locations/Form.vue'),
        meta: { title: '编辑位置' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/Index.vue'),
        meta: { title: '系统设置' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/categories/Management.vue'),
        meta: { title: '类别管理' }
      },
      {
        path: 'dictionary/maintenance-types',
        name: 'MaintenanceTypes',
        component: () => import('@/views/dictionary/MaintenanceTypes.vue'),
        meta: { title: '运维记录类型管理' }
      },
      {
        path: 'dictionary/maintenance-categories',
        name: 'MaintenanceCategories',
        component: () => import('@/views/dictionary/MaintenanceCategories.vue'),
        meta: { title: '运维维护类别管理' }
      },
      {
        path: 'dictionary/departments',
        name: 'Departments',
        component: () => import('@/views/dictionary/Departments.vue'),
        meta: { title: '组织机构管理' }
      }
    ]
  },
  {
    path: '/error',
    name: 'Error',
    component: () => import('@/views/ErrorPage.vue'),
    meta: {
      title: '错误页面',
      hideInMenu: true,
      noAuth: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/ErrorPage.vue'),
    meta: {
      title: '页面未找到',
      hideInMenu: true,
      noAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  console.log('路由守卫执行:', {
    to: to.path,
    from: from.path,
    hasUserInfo: !!userStore.userInfo,
    isLoggedIn: userStore.isLoggedIn,
    noAuth: to.meta.noAuth
  })
  
  // 增强的登录状态检查：同时检查store状态和token有效性
  const token = getSecureToken()
  const tokenValid = token && !isTokenExpired(token)
  
  console.log('路由守卫: 登录状态检查', {
    hasToken: !!token,
    tokenValid,
    storeLoggedIn: userStore.isLoggedIn,
    hasUserInfo: !!userStore.userInfo
  })
  
  const isAuthenticated = userStore.isLoggedIn && userStore.userInfo && tokenValid
  
  // 特殊处理：用户主动访问登录页面时清除持久化状态
  if (to.path === '/login' || to.path === '/') {
    console.log('路由守卫: 用户主动访问登录页面，清除持久化状态')
    // 清除所有登录状态，要求重新登录
    userStore.clearUserData()
    
    // 如果访问根路径，重定向到登录页
    if (to.path === '/') {
      next('/login')
      return
    }
    
    // 访问登录页，直接通过
    next()
    return
  }
  
  // 不需要认证的页面（除了登录页）
  if (to.meta.noAuth) {
    console.log('路由守卫: 不需要认证的页面，直接通过')
    next()
    return
  }
  
  // 需要认证的页面：检查登录状态
  if (!isAuthenticated) {
    console.log('路由守卫: 用户未登录或token无效，跳转到登录页')
    
    // 清除无效状态
    if (!tokenValid) {
      userStore.clearUserData()
    }
    
    next('/login')
    return
  }
  
  console.log('路由守卫: 检查通过，允许访问内部页面')
  next()
})

export default router