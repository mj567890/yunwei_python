// 位置管理API
import { request } from '@/utils/request'
import type { ApiResponse } from '@/types/common'

export interface Building {
  id: number
  name: string
  code: string
  address?: string
  description?: string
  status: number
  floor_count?: number
}

export interface Floor {
  id: number
  building_id: number
  name: string
  code: string
  floor_number: number
  description?: string
  status: number
  building_name?: string
  room_count?: number
}

export interface Room {
  id: number
  floor_id: number
  name: string
  code: string
  room_type?: string
  area?: number
  capacity?: number
  description?: string
  status: number
  floor_name?: string
  building_name?: string
  building_id?: number
}

// 位置管理API
export const locationApi = {
  // 楼宇管理
  getBuildings: (): Promise<ApiResponse<Building[]>> => request.get('/locations/buildings'),
  getBuilding: (id: number): Promise<ApiResponse<Building>> => request.get(`/locations/buildings/${id}`),
  createBuilding: (data: Partial<Building>): Promise<ApiResponse<Building>> => request.post('/locations/buildings', data),
  updateBuilding: (id: number, data: Partial<Building>): Promise<ApiResponse<Building>> => request.put(`/locations/buildings/${id}`, data),
  deleteBuilding: (id: number): Promise<ApiResponse<void>> => request.delete(`/locations/buildings/${id}`),

  // 楼层管理
  getFloors: (buildingId?: number): Promise<ApiResponse<Floor[]>> => request.get('/locations/floors', buildingId ? { building_id: buildingId } : undefined),
  getFloor: (id: number): Promise<ApiResponse<Floor>> => request.get(`/locations/floors/${id}`),
  createFloor: (data: Partial<Floor>): Promise<ApiResponse<Floor>> => request.post('/locations/floors', data),
  updateFloor: (id: number, data: Partial<Floor>): Promise<ApiResponse<Floor>> => request.put(`/locations/floors/${id}`, data),
  deleteFloor: (id: number): Promise<ApiResponse<void>> => request.delete(`/locations/floors/${id}`),

  // 房间管理
  getRooms: (floorId?: number, buildingId?: number): Promise<ApiResponse<Room[]>> => {
    const params: any = {}
    if (floorId) params.floor_id = floorId
    if (buildingId) params.building_id = buildingId
    return request.get('/locations/rooms', params)
  },
  getRoom: (id: number): Promise<ApiResponse<Room>> => request.get(`/locations/rooms/${id}`),
  createRoom: (data: Partial<Room>): Promise<ApiResponse<Room>> => request.post('/locations/rooms', data),
  updateRoom: (id: number, data: Partial<Room>): Promise<ApiResponse<Room>> => request.put(`/locations/rooms/${id}`, data),
  deleteRoom: (id: number): Promise<ApiResponse<void>> => request.delete(`/locations/rooms/${id}`),

  // 获取位置树形结构
  getLocationTree: (): Promise<ApiResponse<any>> => request.get('/locations/tree')
}