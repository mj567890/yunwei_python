// 认证相关API
import { request } from '@/utils/request'
import type { ApiResponse } from '@/types/common'

export interface LoginForm {
  username: string
  password: string
  remember_me?: boolean
}

export interface UserInfo {
  id: number
  username: string
  email: string
  real_name: string
  roles: Array<{
    id: number
    name: string
    code: string
  }>
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: UserInfo
  expires_in: number
}

// 认证API
export const authApi = {
  // 用户登录
  login: (data: LoginForm): Promise<ApiResponse<LoginResponse>> => 
    request.post('/auth/login', data),

  // 用户登出
  logout: (): Promise<ApiResponse<void>> => 
    request.post('/auth/logout'),

  // 刷新token
  refreshToken: (): Promise<ApiResponse<{access_token: string, expires_in: number}>> => 
    request.post('/auth/refresh'),

  // 获取用户信息
  getUserInfo: (): Promise<ApiResponse<UserInfo>> => 
    request.get('/auth/profile'),

  // 获取用户权限
  getUserPermissions: (): Promise<ApiResponse<{permissions: string[], roles: any[]}>> => 
    request.get('/auth/permissions'),

  // 修改密码
  changePassword: (data: {
    old_password: string
    new_password: string
    confirm_password: string
  }): Promise<ApiResponse<void>> => 
    request.post('/auth/change-password', data)
}