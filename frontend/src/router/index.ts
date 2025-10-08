import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    redirect: '/app/dashboard'
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
        path: 'network/devices/:id',
        name: 'NetworkDeviceDetail',
        component: () => import('@/views/network/Detail.vue'),
        meta: { title: '设备详情' }
      },
      {
        path: 'network/devices/create',
        name: 'NetworkDeviceCreate',
        component: () => import('@/views/network/DeviceForm.vue'),
        meta: { title: '新增设备' }
      },
      {
        path: 'network/devices/:id/edit',
        name: 'NetworkDeviceEdit',
        component: () => import('@/views/network/DeviceForm.vue'),
        meta: { title: '编辑设备' }
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
  
  // 不需要认证的页面
  if (to.meta.noAuth) {
    console.log('路由守卫: 不需要认证的页面，直接通过')
    next()
    return
  }
  
  // 检查用户是否已登录
  if (!userStore.isLoggedIn || !userStore.userInfo) {
    console.log('路由守卫: 用户未登录，跳转到登录页')
    next('/login')
    return
  }
  
  console.log('路由守卫: 检查通过，允许访问')
  next()
})

export default router