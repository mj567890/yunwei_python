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
    userInfo: userStore.userInfo,
    isLoggedIn: userStore.isLoggedIn,
    permissions: userStore.permissions
  })
  
  const token = getSecureToken()
  console.log('从存储获取的token:', !!token)
  
  // 如果有持久化的用户信息但没有token，或者有token但没有用户信息
  if (userStore.isLoggedIn && userStore.userInfo && token && !isTokenExpired(token)) {
    // 状态完整，不需要初始化
    userStore.token = token // 确保 token 在 store 中
    console.log('用户状态完整，无需初始化')
  } else if (token && !isTokenExpired(token) && !userStore.userInfo) {
    // 有token但没有用户信息，需要初始化
    console.log('有token但缺少用户信息，开始初始化')
    try {
      await userStore.initUserState()
      console.log('用户状态初始化成功')
    } catch (error) {
      console.error('用户状态初始化失败:', error)
      // 清除无效的持久化状态
      userStore.clearUserData()
    }
  } else if (userStore.isLoggedIn && (!token || isTokenExpired(token))) {
    // 有持久化状态但token无效，清除状态
    console.log('持久化状态存在但token无效，清除状态')
    userStore.clearUserData()
  } else {
    console.log('无需初始化或没有有效token')
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