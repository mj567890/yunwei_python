// 用户管理API
import { request } from '@/utils/request'
import type { UserInfo, UserSearchParams, ApiResponse, PaginationInfo } from '@/types/common'

// 用户角色接口
export interface UserRole {
  id: number
  name: string
  code: string
}

// 用户创建参数
export interface UserCreateParams {
  username: string
  password: string
  email?: string
  phone?: string
  real_name?: string
  role_ids?: number[]
  status?: number
}

// 用户更新参数
export interface UserUpdateParams {
  email?: string
  phone?: string
  real_name?: string
  role_ids?: number[]
  status?: number
}

// 密码重置参数
export interface ResetPasswordParams {
  new_password?: string
}

// 用户管理API接口
export const userApi = {
  // 获取用户列表
  getUsers: (params?: UserSearchParams): Promise<ApiResponse<{
    list: UserInfo[]
    pagination: PaginationInfo
  }>> => 
    request.get('/user', params),

  // 获取用户详情
  getUser: (id: number): Promise<ApiResponse<UserInfo>> => 
    request.get(`/user/${id}`),

  // 创建用户
  createUser: (data: UserCreateParams): Promise<ApiResponse<UserInfo>> => 
    request.post('/user', data),

  // 更新用户
  updateUser: (id: number, data: UserUpdateParams): Promise<ApiResponse<UserInfo>> => 
    request.put(`/user/${id}`, data),

  // 删除用户
  deleteUser: (id: number): Promise<ApiResponse<void>> => 
    request.delete(`/user/${id}`),

  // 重置用户密码
  resetPassword: (id: number, data?: ResetPasswordParams): Promise<ApiResponse<void>> => 
    request.post(`/user/${id}/reset-password`, data),

  // 解锁用户账户
  unlockUser: (id: number): Promise<ApiResponse<void>> => 
    request.post(`/user/${id}/unlock`),

  // 获取角色列表
  getRoles: (): Promise<ApiResponse<UserRole[]>> => 
    request.get('/user/roles'),

  // 批量启用用户
  batchEnable: (userIds: number[]): Promise<ApiResponse<void>> => 
    request.post('/user/batch/enable', { user_ids: userIds }),

  // 批量禁用用户
  batchDisable: (userIds: number[]): Promise<ApiResponse<void>> => 
    request.post('/user/batch/disable', { user_ids: userIds }),

  // 批量删除用户
  batchDelete: (userIds: number[]): Promise<ApiResponse<void>> => 
    request.post('/user/batch/delete', { user_ids: userIds }),

  // 导出用户数据
  exportUsers: (params?: UserSearchParams): Promise<ApiResponse<any>> => 
    request.get('/user/export', params)
}