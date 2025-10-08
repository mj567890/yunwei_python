<template>
  <div class="location-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>位置管理</h1>
      <div class="header-actions">
        <button @click="refreshLocations" class="btn btn-secondary">🔄 刷新</button>
        <button @click="expandAll" class="btn btn-secondary">📂 展开全部</button>
        <button @click="collapseAll" class="btn btn-secondary">📁 收起全部</button>
        <button @click="createBuilding" class="btn btn-primary">🏢 新建楼宇</button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stats-card">
        <div class="stats-icon">🏢</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.buildings }}</div>
          <div class="stats-label">建筑总数</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">🏬</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.floors }}</div>
          <div class="stats-label">楼层总数</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">🚪</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.rooms }}</div>
          <div class="stats-label">房间总数</div>
        </div>
      </div>
      <div class="stats-card">
        <div class="stats-icon">📦</div>
        <div class="stats-content">
          <div class="stats-number">{{ stats.assets }}</div>
          <div class="stats-label">关联资产</div>
        </div>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>关键词搜索</label>
          <input 
            v-model="searchParams.keyword" 
            placeholder="搜索建筑、楼层或房间名称" 
            @input="handleSearch"
          />
        </div>
        <div class="form-group">
          <label>位置类型</label>
          <select v-model="searchParams.type" @change="handleSearch">
            <option value="">全部类型</option>
            <option value="building">建筑</option>
            <option value="floor">楼层</option>
            <option value="room">房间</option>
          </select>
        </div>
        <div class="form-group">
          <label>状态</label>
          <select v-model="searchParams.status" @change="handleSearch">
            <option value="">全部状态</option>
            <option value="1">启用</option>
            <option value="0">禁用</option>
          </select>
        </div>
        <div class="form-group">
          <button @click="resetSearch" class="btn btn-secondary">🔄 重置</button>
        </div>
      </div>
    </div>

    <!-- 位置树形结构 -->
    <div class="location-tree-container">
      <div v-if="loading" class="loading">
        <div class="loading-spinner">🔄</div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="filteredLocations.length > 0" class="location-tree">
        <div 
          v-for="building in filteredLocations" 
          :key="`building-${building.id}`"
          class="location-node building-node"
        >
          <!-- 建筑节点 -->
          <div class="node-content">
            <div class="node-info">
              <button 
                @click="toggleExpand(building)" 
                class="expand-btn"
                :class="{ expanded: building.expanded }"
              >
                <span v-if="building.floors && building.floors.length > 0">
                  {{ building.expanded ? '📂' : '📁' }}
                </span>
                <span v-else>📄</span>
              </button>
              <div class="node-icon">🏢</div>
              <div class="node-details">
                <div class="node-title">{{ building.name }}</div>
                <div class="node-subtitle">
                  {{ building.code }} 
                  <span v-if="building.address">• {{ building.address }}</span>
                  <span class="stats-info">
                    {{ building.floor_count || 0 }}层 • {{ building.total_rooms || 0 }}间
                  </span>
                </div>
              </div>
            </div>
            <div class="node-actions">
              <span 
                :class="`status-tag ${building.status ? 'active' : 'inactive'}`"
              >
                {{ building.status ? '启用' : '禁用' }}
              </span>
              <button @click="addFloor(building)" class="btn-sm btn-primary">➕ 楼层</button>
              <button @click="editBuilding(building)" class="btn-sm btn-secondary">编辑</button>
              <button @click="deleteBuilding(building)" class="btn-sm btn-danger">删除</button>
            </div>
          </div>

          <!-- 楼层节点 -->
          <div v-if="building.expanded && building.floors" class="children-container">
            <div 
              v-for="floor in building.floors" 
              :key="`floor-${floor.id}`"
              class="location-node floor-node"
            >
              <div class="node-content">
                <div class="node-info">
                  <button 
                    @click="toggleExpand(floor)" 
                    class="expand-btn"
                    :class="{ expanded: floor.expanded }"
                  >
                    <span v-if="floor.rooms && floor.rooms.length > 0">
                      {{ floor.expanded ? '📂' : '📁' }}
                    </span>
                    <span v-else>📄</span>
                  </button>
                  <div class="node-icon">🏬</div>
                  <div class="node-details">
                    <div class="node-title">{{ floor.name }}</div>
                    <div class="node-subtitle">
                      {{ floor.code }} • 第{{ floor.floor_number }}层
                      <span class="stats-info">{{ floor.room_count || 0 }}间</span>
                    </div>
                  </div>
                </div>
                <div class="node-actions">
                  <span 
                    :class="`status-tag ${floor.status ? 'active' : 'inactive'}`"
                  >
                    {{ floor.status ? '启用' : '禁用' }}
                  </span>
                  <button @click="addRoom(floor)" class="btn-sm btn-primary">➕ 房间</button>
                  <button @click="editFloor(floor)" class="btn-sm btn-secondary">编辑</button>
                  <button @click="deleteFloor(floor)" class="btn-sm btn-danger">删除</button>
                </div>
              </div>

              <!-- 房间节点 -->
              <div v-if="floor.expanded && floor.rooms" class="children-container">
                <div 
                  v-for="room in floor.rooms" 
                  :key="`room-${room.id}`"
                  class="location-node room-node"
                >
                  <div class="node-content">
                    <div class="node-info">
                      <div class="expand-btn"></div>
                      <div class="node-icon">🚪</div>
                      <div class="node-details">
                        <div class="node-title">{{ room.name }}</div>
                        <div class="node-subtitle">
                          {{ room.code }}
                          <span v-if="room.room_type">• {{ room.room_type }}</span>
                          <span v-if="room.area">• {{ room.area }}㎡</span>
                          <span v-if="room.capacity">• 容纳{{ room.capacity }}人</span>
                        </div>
                      </div>
                    </div>
                    <div class="node-actions">
                      <span 
                        :class="`status-tag ${room.status ? 'active' : 'inactive'}`"
                      >
                        {{ room.status ? '启用' : '禁用' }}
                      </span>
                      <button @click="viewRoom(room)" class="btn-sm btn-info">查看</button>
                      <button @click="editRoom(room)" class="btn-sm btn-secondary">编辑</button>
                      <button @click="deleteRoom(room)" class="btn-sm btn-danger">删除</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <div class="empty-icon">🏢</div>
        <p>暂无位置数据</p>
        <button @click="createBuilding" class="btn btn-primary">创建第一个建筑</button>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <div v-if="showDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ dialogTitle }}</h3>
          <button @click="closeDialog" class="close-btn">✕</button>
        </div>
        
        <form @submit.prevent="saveLocation" class="modal-body">
          <!-- 建筑表单 -->
          <div v-if="dialogType === 'building'" class="form-fields">
            <div class="form-group">
              <label>建筑名称 <span class="required">*</span></label>
              <input 
                v-model="formData.name" 
                type="text" 
                placeholder="请输入建筑名称"
                :class="{ error: errors.name }"
                @blur="validateField('name')"
              />
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>
            
            <div class="form-group">
              <label>建筑编码 <span class="required">*</span></label>
              <input 
                v-model="formData.code" 
                type="text" 
                placeholder="请输入建筑编码"
                :class="{ error: errors.code }"
                @blur="validateField('code')"
              />
              <span v-if="errors.code" class="error-text">{{ errors.code }}</span>
            </div>
            
            <div class="form-group">
              <label>建筑地址</label>
              <input 
                v-model="formData.address" 
                type="text" 
                placeholder="请输入建筑地址"
              />
            </div>
            
            <div class="form-group full-width">
              <label>建筑描述</label>
              <textarea 
                v-model="formData.description" 
                rows="3" 
                placeholder="请输入建筑描述"
              ></textarea>
            </div>
          </div>

          <!-- 楼层表单 -->
          <div v-else-if="dialogType === 'floor'" class="form-fields">
            <div class="form-group">
              <label>楼层名称 <span class="required">*</span></label>
              <input 
                v-model="formData.name" 
                type="text" 
                placeholder="请输入楼层名称"
                :class="{ error: errors.name }"
                @blur="validateField('name')"
              />
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>
            
            <div class="form-group">
              <label>楼层编码 <span class="required">*</span></label>
              <input 
                v-model="formData.code" 
                type="text" 
                placeholder="请输入楼层编码"
                :class="{ error: errors.code }"
                @blur="validateField('code')"
              />
              <span v-if="errors.code" class="error-text">{{ errors.code }}</span>
            </div>
            
            <div class="form-group">
              <label>楼层号 <span class="required">*</span></label>
              <input 
                v-model.number="formData.floor_number" 
                type="number" 
                placeholder="请输入楼层号"
                :class="{ error: errors.floor_number }"
                @blur="validateField('floor_number')"
              />
              <span v-if="errors.floor_number" class="error-text">{{ errors.floor_number }}</span>
            </div>
            
            <div class="form-group full-width">
              <label>楼层描述</label>
              <textarea 
                v-model="formData.description" 
                rows="3" 
                placeholder="请输入楼层描述"
              ></textarea>
            </div>
          </div>

          <!-- 房间表单 -->
          <div v-else-if="dialogType === 'room'" class="form-fields">
            <div class="form-group">
              <label>房间名称 <span class="required">*</span></label>
              <input 
                v-model="formData.name" 
                type="text" 
                placeholder="请输入房间名称"
                :class="{ error: errors.name }"
                @blur="validateField('name')"
              />
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>
            
            <div class="form-group">
              <label>房间编码 <span class="required">*</span></label>
              <input 
                v-model="formData.code" 
                type="text" 
                placeholder="请输入房间编码"
                :class="{ error: errors.code }"
                @blur="validateField('code')"
              />
              <span v-if="errors.code" class="error-text">{{ errors.code }}</span>
            </div>
            
            <div class="form-group">
              <label>房间类型</label>
              <select v-model="formData.room_type">
                <option value="">请选择房间类型</option>
                <option value="办公室">办公室</option>
                <option value="会议室">会议室</option>
                <option value="机房">机房</option>
                <option value="仓库">仓库</option>
                <option value="实验室">实验室</option>
                <option value="其他">其他</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>面积(㎡)</label>
              <input 
                v-model.number="formData.area" 
                type="number" 
                placeholder="请输入房间面积"
                min="0"
                step="0.1"
              />
            </div>
            
            <div class="form-group">
              <label>容纳人数</label>
              <input 
                v-model.number="formData.capacity" 
                type="number" 
                placeholder="请输入容纳人数"
                min="0"
              />
            </div>
            
            <div class="form-group full-width">
              <label>房间描述</label>
              <textarea 
                v-model="formData.description" 
                rows="3" 
                placeholder="请输入房间描述"
              ></textarea>
            </div>
          </div>

          <!-- 状态选择 -->
          <div class="form-group">
            <label>状态</label>
            <div class="radio-group">
              <label class="radio-label">
                <input v-model="formData.status" type="radio" :value="1" />
                <span class="radio-mark"></span>
                启用
              </label>
              <label class="radio-label">
                <input v-model="formData.status" type="radio" :value="0" />
                <span class="radio-mark"></span>
                禁用
              </label>
            </div>
          </div>
        </form>
        
        <div class="modal-footer">
          <button @click="closeDialog" type="button" class="btn btn-secondary">取消</button>
          <button @click="saveLocation" :disabled="saving" class="btn btn-primary">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { locationApi } from '@/api/location'

// 接口定义
interface Building {
  id: number
  name: string
  code: string
  address?: string
  description?: string
  status: number
  floor_count?: number
  total_rooms?: number
  floors?: Floor[]
  expanded?: boolean
}

interface Floor {
  id: number
  building_id: number
  name: string
  code: string
  floor_number: number
  description?: string
  status: number
  building_name?: string
  room_count?: number
  rooms?: Room[]
  expanded?: boolean
}

interface Room {
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

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const dialogType = ref<'building' | 'floor' | 'room'>('building')
const editingItem = ref<any>(null)

const locations = ref<Building[]>([])
const searchParams = reactive({
  keyword: '',
  type: '',
  status: ''
})

const formData = reactive<any>({
  name: '',
  code: '',
  description: '',
  status: 1
})

const errors = reactive<Record<string, string>>({})

const stats = reactive({
  buildings: 0,
  floors: 0,
  rooms: 0,
  assets: 0
})

// 计算属性
const dialogTitle = computed(() => {
  const action = editingItem.value ? '编辑' : '新建'
  const type = {
    building: '建筑',
    floor: '楼层',
    room: '房间'
  }[dialogType.value]
  return `${action}${type}`
})

const filteredLocations = computed(() => {
  let result = [...locations.value]
  
  if (searchParams.keyword) {
    const keyword = searchParams.keyword.toLowerCase()
    result = result.filter(building => {
      // 搜索建筑
      if (building.name.toLowerCase().includes(keyword) || 
          building.code.toLowerCase().includes(keyword)) {
        return true
      }
      
      // 搜索楼层
      if (building.floors) {
        const matchedFloors = building.floors.filter(floor => 
          floor.name.toLowerCase().includes(keyword) || 
          floor.code.toLowerCase().includes(keyword)
        )
        if (matchedFloors.length > 0) {
          building.expanded = true
          return true
        }
        
        // 搜索房间
        for (const floor of building.floors) {
          if (floor.rooms) {
            const matchedRooms = floor.rooms.filter(room =>
              room.name.toLowerCase().includes(keyword) || 
              room.code.toLowerCase().includes(keyword)
            )
            if (matchedRooms.length > 0) {
              building.expanded = true
              floor.expanded = true
              return true
            }
          }
        }
      }
      
      return false
    })
  }
  
  if (searchParams.status !== '') {
    const status = parseInt(searchParams.status)
    result = result.filter(building => building.status === status)
  }
  
  return result
})

// 数据加载
const loadLocations = async () => {
  loading.value = true
  try {
    const response = await locationApi.getLocationTree()
    if (response.success) {
      locations.value = response.data.map((building: Building) => ({
        ...building,
        expanded: false,
        floors: building.floors?.map(floor => ({
          ...floor,
          expanded: false
        }))
      }))
      
      // 更新统计
      updateStats()
    }
  } catch (error) {
    console.error('加载位置数据失败:', error)
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  stats.buildings = locations.value.length
  stats.floors = locations.value.reduce((total, building) => total + (building.floor_count || 0), 0)
  stats.rooms = locations.value.reduce((total, building) => total + (building.total_rooms || 0), 0)
  // stats.assets 需要从其他API获取
}

// 树形操作
const toggleExpand = (item: any) => {
  item.expanded = !item.expanded
}

const expandAll = () => {
  locations.value.forEach(building => {
    building.expanded = true
    if (building.floors) {
      building.floors.forEach(floor => {
        floor.expanded = true
      })
    }
  })
}

const collapseAll = () => {
  locations.value.forEach(building => {
    building.expanded = false
    if (building.floors) {
      building.floors.forEach(floor => {
        floor.expanded = false
      })
    }
  })
}

// 搜索功能
const handleSearch = () => {
  // 搜索时自动展开匹配的节点
  // 已在 filteredLocations 计算属性中处理
}

const resetSearch = () => {
  searchParams.keyword = ''
  searchParams.type = ''
  searchParams.status = ''
  collapseAll()
}

// 表单验证
const validateField = (field: string) => {
  errors[field] = ''
  
  switch (field) {
    case 'name':
      if (!formData.name?.trim()) {
        errors[field] = '名称不能为空'
      }
      break
    case 'code':
      if (!formData.code?.trim()) {
        errors[field] = '编码不能为空'
      }
      break
    case 'floor_number':
      if (formData.floor_number === undefined || formData.floor_number === null) {
        errors[field] = '楼层号不能为空'
      }
      break
  }
}

const validateForm = (): boolean => {
  validateField('name')
  validateField('code')
  if (dialogType.value === 'floor') {
    validateField('floor_number')
  }
  
  return Object.values(errors).every(error => !error)
}

// 对话框操作
const openDialog = (type: 'building' | 'floor' | 'room', parent?: any, item?: any) => {
  dialogType.value = type
  editingItem.value = item || null
  
  if (item) {
    Object.assign(formData, item)
  } else {
    Object.keys(formData).forEach(key => {
      if (key === 'status') {
        formData[key] = 1
      } else if (key === 'building_id' && parent) {
        formData[key] = parent.id
      } else if (key === 'floor_id' && parent) {
        formData[key] = parent.id
      } else {
        formData[key] = ''
      }
    })
  }
  
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
  editingItem.value = null
}

const saveLocation = async () => {
  if (!validateForm()) {
    return
  }
  
  saving.value = true
  try {
    let response
    const data = { ...formData }
    
    if (editingItem.value) {
      // 编辑
      switch (dialogType.value) {
        case 'building':
          response = await locationApi.updateBuilding(editingItem.value.id, data)
          break
        case 'floor':
          response = await locationApi.updateFloor(editingItem.value.id, data)
          break
        case 'room':
          response = await locationApi.updateRoom(editingItem.value.id, data)
          break
      }
    } else {
      // 新建
      switch (dialogType.value) {
        case 'building':
          response = await locationApi.createBuilding(data)
          break
        case 'floor':
          response = await locationApi.createFloor(data)
          break
        case 'room':
          response = await locationApi.createRoom(data)
          break
      }
    }
    
    if (response?.success) {
      closeDialog()
      await loadLocations()
      console.log('保存成功')
    }
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

// CRUD操作
const createBuilding = () => openDialog('building')
const addFloor = (building: Building) => openDialog('floor', building)
const addRoom = (floor: Floor) => openDialog('room', floor)

const editBuilding = (building: Building) => openDialog('building', undefined, building)
const editFloor = (floor: Floor) => openDialog('floor', undefined, floor)
const editRoom = (room: Room) => openDialog('room', undefined, room)

const viewRoom = (room: Room) => {
  console.log('查看房间:', room)
  // TODO: 实现房间详情查看
}

const deleteBuilding = async (building: Building) => {
  if (confirm(`确认删除建筑 "${building.name}" 吗？此操作将同时删除所有关联的楼层和房间，且不可恢复！`)) {
    try {
      const response = await locationApi.deleteBuilding(building.id)
      if (response.success) {
        await loadLocations()
        console.log('删除成功')
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

const deleteFloor = async (floor: Floor) => {
  if (confirm(`确认删除楼层 "${floor.name}" 吗？此操作将同时删除所有关联的房间，且不可恢复！`)) {
    try {
      const response = await locationApi.deleteFloor(floor.id)
      if (response.success) {
        await loadLocations()
        console.log('删除成功')
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

const deleteRoom = async (room: Room) => {
  if (confirm(`确认删除房间 "${room.name}" 吗？此操作不可恢复！`)) {
    try {
      const response = await locationApi.deleteRoom(room.id)
      if (response.success) {
        await loadLocations()
        console.log('删除成功')
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

const refreshLocations = () => loadLocations()

// 初始化
onMounted(() => {
  loadLocations()
})
</script>

<style scoped>
.location-management-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px 30px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stats-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  font-size: 32px;
  opacity: 0.8;
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.search-form {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-row {
  display: flex;
  gap: 20px;
  align-items: end;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 150px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #409eff;
}

.location-tree-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.loading-spinner {
  font-size: 24px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.location-tree {
  padding: 20px;
}

.location-node {
  margin-bottom: 8px;
}

.building-node {
  border-left: 4px solid #409eff;
}

.floor-node {
  border-left: 4px solid #67c23a;
  margin-left: 20px;
}

.room-node {
  border-left: 4px solid #e6a23c;
  margin-left: 40px;
}

.node-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.2s;
}

.node-content:hover {
  background: #e3f2fd;
}

.node-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
  min-width: 24px;
}

.expand-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.node-icon {
  font-size: 20px;
}

.node-details {
  flex: 1;
}

.node-title {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
  margin-bottom: 4px;
}

.node-subtitle {
  color: #909399;
  font-size: 14px;
}

.stats-info {
  margin-left: 8px;
  padding: 2px 6px;
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  border-radius: 3px;
  font-size: 12px;
}

.node-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.active {
  background: #f0f9ff;
  color: #67c23a;
}

.status-tag.inactive {
  background: #fef0f0;
  color: #f56c6c;
}

.children-container {
  margin-top: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 16px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-secondary {
  background: #909399;
  color: white;
}

.btn-secondary:hover {
  background: #a6a9ad;
}

.btn-info {
  background: #909399;
  color: white;
}

.btn-info:hover {
  background: #a6a9ad;
}

.btn-danger {
  background: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background: #f78989;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px 30px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #909399;
  padding: 4px;
}

.close-btn:hover {
  color: #f56c6c;
}

.modal-body {
  padding: 30px;
  flex: 1;
  overflow-y: auto;
}

.form-fields {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-fields .form-group.full-width {
  grid-column: 1 / -1;
}

.form-fields .form-group {
  display: flex;
  flex-direction: column;
}

.form-fields .form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.required {
  color: #f56c6c;
}

.form-fields input,
.form-fields select,
.form-fields textarea {
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-fields input:focus,
.form-fields select:focus,
.form-fields textarea:focus {
  outline: none;
  border-color: #409eff;
}

.form-fields input.error,
.form-fields select.error {
  border-color: #f56c6c;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}

.radio-group {
  display: flex;
  gap: 20px;
  margin-top: 8px;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
}

.radio-label input[type="radio"] {
  margin-right: 8px;
  transform: scale(1.2);
}

.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .location-management-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .search-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .node-content {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .node-actions {
    justify-content: center;
  }
  
  .floor-node {
    margin-left: 10px;
  }
  
  .room-node {
    margin-left: 20px;
  }
  
  .form-fields {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .node-subtitle {
    font-size: 12px;
  }
  
  .btn-sm {
    padding: 4px 8px;
    font-size: 11px;
  }
}
</style>