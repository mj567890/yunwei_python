import { defineStore } from 'pinia'
import { authApi, type UserInfo } from '@/api/auth'
import { setSecureToken, getSecureToken, clearSecureToken, isTokenExpired } from '@/utils/crypto'

interface UserState {
  token: string | null
  userInfo: UserInfo | null
  permissions: string[]
  isLoggedIn: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => {
    // 初始状态不加载token，由App.vue负责初始化
    return {
      token: null,
      userInfo: null,
      permissions: [],
      isLoggedIn: false
    }
  },

  actions: {
    // 登录
    async login(loginForm: any) {
      try {
        const response = await authApi.login(loginForm)
        
        this.token = response.data.access_token
        this.userInfo = response.data.user
        this.isLoggedIn = true
        
        // 使用安全方式存储Token
        setSecureToken(response.data.access_token)
        
        // 获取用户权限
        await this.getUserPermissions()
        
        return response
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },

    // 登出
    async logout() {
      try {
        if (this.token) {
          await authApi.logout()
        }
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        this.clearUserData()
      }
    },

    // 获取用户信息
    async getUserInfo() {
      try {
        const response = await authApi.getUserInfo()
        this.userInfo = response.data
        return response.data
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 不要在这里清除用户数据，让调用者决定如何处理
        throw error
      }
    },

    // 获取用户权限
    async getUserPermissions() {
      try {
        const response = await authApi.getUserPermissions()
        this.permissions = response.data.permissions
        return response.data
      } catch (error) {
        console.error('获取用户权限失败:', error)
        throw error
      }
    },

    // 清除用户数据
    clearUserData() {
      this.token = null
      this.userInfo = null
      this.permissions = []
      this.isLoggedIn = false
      
      // 使用安全方式清除Token
      clearSecureToken()
    },

    // 初始化用户状态
    async initUserState() {
      console.log('initUserState: 开始初始化')
      const token = getSecureToken()
      console.log('initUserState: 获取到token:', !!token)
      
      if (token && !isTokenExpired(token)) {
        this.token = token
        console.log('initUserState: token有效，开始获取用户信息')
        try {
          await this.getUserInfo()
          console.log('initUserState: 获取用户信息成功')
          await this.getUserPermissions()
          console.log('initUserState: 获取用户权限成功')
          this.isLoggedIn = true
          console.log('initUserState: 初始化完成，设置登录状态为true')
        } catch (error) {
          console.error('initUserState: API调用失败:', error)
          throw error
        }
      } else {
        console.log('initUserState: token无效或不存在')
        throw new Error('Token无效或已过期')
      }
    }
  },

  getters: {
    // 检查权限
    hasPermission: (state) => (permission: string): boolean => {
      return state.permissions.includes(permission)
    },

    // 检查角色
    hasRole: (state) => (roleCode: string): boolean => {
      return state.userInfo?.roles?.some(role => role.code === roleCode) || false
    }
  },
  
  // 持久化用户状态，但需要在应用启动时验证token有效性
  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['userInfo', 'permissions', 'isLoggedIn'] // 恢复 isLoggedIn 持久化
  }
})