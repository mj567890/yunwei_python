// @ts-nocheck
/**
 * 认证相关组件测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Login from '@/views/auth/Login.vue'
import { useUserStore } from '@/stores/user'
import { createMockResponse, resetMocks } from '../setup'

describe('Login Component', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    resetMocks()
  })

  it('renders login form correctly', () => {
    const wrapper = mount(Login)
    
    expect(wrapper.find('h2').text()).toBe('IT运维管理系统')
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('validates required fields', async () => {
    const wrapper = mount(Login)
    
    // 尝试提交空表单
    const submitButton = wrapper.find('button[type="submit"]')
    await submitButton.trigger('click')
    
    // 应该显示验证错误
    expect(wrapper.text()).toContain('请输入用户名')
    expect(wrapper.text()).toContain('请输入密码')
  })

  it('validates username length', async () => {
    const wrapper = mount(Login)
    
    // 输入过短的用户名
    const usernameInput = wrapper.find('input[type="text"]')
    await usernameInput.setValue('ab')
    await usernameInput.trigger('blur')
    
    expect(wrapper.text()).toContain('用户名长度不能少于3位')
  })

  it('validates password length', async () => {
    const wrapper = mount(Login)
    
    // 输入过短的密码
    const passwordInput = wrapper.find('input[type="password"]')
    await passwordInput.setValue('123')
    await passwordInput.trigger('blur')
    
    expect(wrapper.text()).toContain('密码长度不能少于6位')
  })

  it('submits login form with valid data', async () => {
    // 模拟成功的登录响应
    const mockFetch = vi.fn().mockResolvedValue(createMockResponse({
      token: 'mock-token',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: { name: '管理员' }
      }
    }))
    global.fetch = mockFetch

    const wrapper = mount(Login)
    const userStore = useUserStore()
    
    // 填写表单
    await wrapper.find('input[type="text"]').setValue('testuser')
    await wrapper.find('input[type="password"]').setValue('password123')
    
    // 提交表单
    await wrapper.find('form').trigger('submit')
    
    // 验证API调用
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify({
          username: 'testuser',
          password: 'password123'
        })
      })
    )
  })

  it('handles login error', async () => {
    // 模拟登录失败响应
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({
        message: '用户名或密码错误'
      })
    })
    global.fetch = mockFetch

    const wrapper = mount(Login)
    
    // 填写表单
    await wrapper.find('input[type="text"]').setValue('wronguser')
    await wrapper.find('input[type="password"]').setValue('wrongpass')
    
    // 提交表单
    await wrapper.find('form').trigger('submit')
    
    // 等待错误处理
    await wrapper.vm.$nextTick()
    
    // 验证错误消息显示
    expect(wrapper.text()).toContain('用户名或密码错误')
  })

  it('toggles password visibility', async () => {
    const wrapper = mount(Login)
    
    const passwordInput = wrapper.find('input[type="password"]')
    const toggleButton = wrapper.find('.password-toggle')
    
    expect(passwordInput.attributes('type')).toBe('password')
    
    // 点击切换按钮
    await toggleButton.trigger('click')
    
    expect(passwordInput.attributes('type')).toBe('text')
    
    // 再次点击切换回来
    await toggleButton.trigger('click')
    
    expect(passwordInput.attributes('type')).toBe('password')
  })

  it('handles remember me functionality', async () => {
    const wrapper = mount(Login)
    
    const rememberCheckbox = wrapper.find('input[type="checkbox"]')
    
    // 默认不勾选
    expect(rememberCheckbox.element.checked).toBe(false)
    
    // 勾选记住我
    await rememberCheckbox.setChecked(true)
    
    expect(rememberCheckbox.element.checked).toBe(true)
  })
})

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    resetMocks()
  })

  it('initializes with default state', () => {
    const userStore = useUserStore()
    
    expect(userStore.user).toBeNull()
    expect(userStore.token).toBeNull()
    expect(userStore.isAuthenticated).toBe(false)
  })

  it('handles successful login', async () => {
    const mockResponse = {
      token: 'test-token',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        role: { name: '管理员' }
      }
    }

    const mockFetch = vi.fn().mockResolvedValue(createMockResponse(mockResponse))
    global.fetch = mockFetch

    const userStore = useUserStore()
    
    await userStore.login('testuser', 'password123')
    
    expect(userStore.token).toBe('test-token')
    expect(userStore.user).toEqual(mockResponse.user)
    expect(userStore.isAuthenticated).toBe(true)
    expect(localStorage.setItem).toHaveBeenCalledWith('token', 'test-token')
  })

  it('handles login failure', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ message: '登录失败' })
    })
    global.fetch = mockFetch

    const userStore = useUserStore()
    
    await expect(userStore.login('wronguser', 'wrongpass')).rejects.toThrow('登录失败')
    
    expect(userStore.token).toBeNull()
    expect(userStore.user).toBeNull()
    expect(userStore.isAuthenticated).toBe(false)
  })

  it('handles logout', async () => {
    const userStore = useUserStore()
    
    // 先设置登录状态
    userStore.token = 'test-token'
    userStore.user = { id: 1, username: 'testuser' }
    
    const mockFetch = vi.fn().mockResolvedValue(createMockResponse({ message: '退出成功' }))
    global.fetch = mockFetch
    
    await userStore.logout()
    
    expect(userStore.token).toBeNull()
    expect(userStore.user).toBeNull()
    expect(userStore.isAuthenticated).toBe(false)
    expect(localStorage.removeItem).toHaveBeenCalledWith('token')
  })

  it('loads user from token', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: { name: '管理员' }
    }

    const mockFetch = vi.fn().mockResolvedValue(createMockResponse(mockUser))
    global.fetch = mockFetch

    // 模拟本地存储中有token
    localStorage.getItem.mockReturnValue('stored-token')

    const userStore = useUserStore()
    
    await userStore.loadUserFromToken()
    
    expect(userStore.token).toBe('stored-token')
    expect(userStore.user).toEqual(mockUser)
    expect(userStore.isAuthenticated).toBe(true)
  })

  it('handles invalid token', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ message: 'Token无效' })
    })
    global.fetch = mockFetch

    localStorage.getItem.mockReturnValue('invalid-token')

    const userStore = useUserStore()
    
    await userStore.loadUserFromToken()
    
    expect(userStore.token).toBeNull()
    expect(userStore.user).toBeNull()
    expect(userStore.isAuthenticated).toBe(false)
    expect(localStorage.removeItem).toHaveBeenCalledWith('token')
  })

  it('updates user profile', async () => {
    const userStore = useUserStore()
    userStore.user = { id: 1, username: 'testuser', email: 'old@example.com' }
    
    const updatedUser = { id: 1, username: 'testuser', email: 'new@example.com' }
    const mockFetch = vi.fn().mockResolvedValue(createMockResponse(updatedUser))
    global.fetch = mockFetch
    
    await userStore.updateProfile({ email: 'new@example.com' })
    
    expect(userStore.user.email).toBe('new@example.com')
  })

  it('changes user password', async () => {
    const userStore = useUserStore()
    userStore.token = 'test-token'
    
    const mockFetch = vi.fn().mockResolvedValue(createMockResponse({ message: '密码修改成功' }))
    global.fetch = mockFetch
    
    await userStore.changePassword('oldpass', 'newpass')
    
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/auth/password',
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify({
          old_password: 'oldpass',
          new_password: 'newpass'
        })
      })
    )
  })
})