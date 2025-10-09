<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from './stores/user'
import { getSecureToken, isTokenExpired } from './utils/crypto'

const userStore = useUserStore()

console.log('App.vue script setup 执行')

// 在应用启动时检查用户状态
onMounted(async () => {
  console.log('App.vue onMounted 执行')
  console.log('持久化恢复后的 userStore 状态:', {
    userInfo: !!userStore.userInfo,
    isLoggedIn: userStore.isLoggedIn,
    permissions: userStore.permissions?.length || 0
  })
  
  const token = getSecureToken()
  const currentPath = window.location.pathname
  console.log('从存储获取的token:', !!token)
  console.log('当前访问路径:', currentPath)
  
  // 如果用户主动访问登录页面，不恢复持久化状态
  if (currentPath === '/login' || currentPath === '/') {
    console.log('用户主动访问登录页面，跳过状态恢复（由路由守卫处理）')
    return
  }
  
  // 只有在访问内部页面时才尝试恢复持久化状态
  console.log('访问内部页面，检查状态一致性')
  
  // 检查状态一致性：持久化状态和token状态必须一致
  if (userStore.isLoggedIn && userStore.userInfo) {
    // 持久化状态显示已登录，检查token是否有效
    if (token && !isTokenExpired(token)) {
      console.log('持久化状态和token都有效，保持登录状态')
      // 确保 store 中有 token
      userStore.token = token
    } else {
      console.log('token无效或不存在，清除持久化状态')
      // token无效，清除所有状态
      userStore.clearUserData()
    }
  } else if (token && !isTokenExpired(token)) {
    // 有有效token但没有持久化状态，尝试恢复状态
    console.log('有有效token但缺少持久化状态，尝试恢复')
    try {
      await userStore.initUserState()
      console.log('用户状态恢复成功')
    } catch (error) {
      console.error('Token验证失败:', error)
      // 清除无效token
      userStore.clearUserData()
    }
  } else {
    console.log('无有效token，确保状态已清除')
    // 确保清除状态
    userStore.clearUserData()
  }
  
  console.log('最终 userStore 状态:', {
    token: !!userStore.token,
    userInfo: !!userStore.userInfo,
    isLoggedIn: userStore.isLoggedIn
  })
})
</script>

<style scoped>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  width: 100vw;
}
</style>