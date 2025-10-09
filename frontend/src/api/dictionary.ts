import { request } from '@/utils/request'
import type { ApiResponse } from '@/types/common'

// 数据字典项接口
export interface DictItem {
  id: number
  name: string
  code: string
  description?: string
  parent_id?: number | null
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

// 部门接口
export interface Department {
  id: number
  name: string
  code: string
  description?: string
  parent_id?: number | null
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

// 数据字典API
export const dictionaryApi = {
  // =================== 运维记录类型管理 ===================
  
  // 获取运维记录类型列表
  getMaintenanceTypes: (): Promise<ApiResponse<DictItem[]>> => 
    request.get('/api/dictionary/maintenance-types'),

  // 创建运维记录类型
  createMaintenanceType: (data: Partial<DictItem>): Promise<ApiResponse<{id: number}>> => 
    request.post('/api/dictionary/maintenance-types', data),

  // 更新运维记录类型
  updateMaintenanceType: (id: number, data: Partial<DictItem>): Promise<ApiResponse<void>> => 
    request.put(`/api/dictionary/maintenance-types/${id}`, data),

  // 删除运维记录类型
  deleteMaintenanceType: (id: number): Promise<ApiResponse<void>> => 
    request.delete(`/api/dictionary/maintenance-types/${id}`),

  // =================== 运维维护类别管理 ===================
  
  // 获取运维维护类别列表
  getMaintenanceCategories: (): Promise<ApiResponse<DictItem[]>> => 
    request.get('/api/dictionary/maintenance-categories'),

  // 创建运维维护类别
  createMaintenanceCategory: (data: Partial<DictItem>): Promise<ApiResponse<{id: number}>> => 
    request.post('/api/dictionary/maintenance-categories', data),

  // 更新运维维护类别
  updateMaintenanceCategory: (id: number, data: Partial<DictItem>): Promise<ApiResponse<void>> => 
    request.put(`/api/dictionary/maintenance-categories/${id}`, data),

  // 删除运维维护类别
  deleteMaintenanceCategory: (id: number): Promise<ApiResponse<void>> => 
    request.delete(`/api/dictionary/maintenance-categories/${id}`),

  // =================== 组织机构管理 ===================
  
  // 获取组织机构列表
  getDepartments: (): Promise<ApiResponse<Department[]>> => 
    request.get('/api/dictionary/departments'),

  // 创建组织机构
  createDepartment: (data: Partial<Department>): Promise<ApiResponse<{id: number}>> => 
    request.post('/api/dictionary/departments', data),

  // 更新组织机构
  updateDepartment: (id: number, data: Partial<Department>): Promise<ApiResponse<void>> => 
    request.put(`/api/dictionary/departments/${id}`, data),

  // 删除组织机构
  deleteDepartment: (id: number): Promise<ApiResponse<void>> => 
    request.delete(`/api/dictionary/departments/${id}`),

  // =================== 表单选项接口 ===================
  
  // 获取运维类型选项（用于表单）
  getTypesForForm: (): Promise<ApiResponse<string[]>> => 
    request.get('/api/dictionary/maintenance/types'),

  // 获取维护类别选项（用于表单）
  getCategoriesForForm: (): Promise<ApiResponse<string[]>> => 
    request.get('/api/dictionary/maintenance/categories'),

  // 获取部门选项（用于表单）
  getDepartmentsForForm: (): Promise<ApiResponse<string[]>> => 
    request.get('/api/dictionary/departments/simple')
}

export default dictionaryApi