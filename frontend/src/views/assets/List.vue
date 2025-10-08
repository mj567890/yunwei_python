<template>
  <div class="asset-list-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>{{ viewMode === 'network' ? '网络设备管理' : '资产管理' }}</h1>
      <div class="header-actions">
        <!-- 视图模式切换 -->
        <div class="view-mode-toggle">
          <button 
            @click="switchViewMode('asset')" 
            :class="['btn', viewMode === 'asset' ? 'btn-primary' : 'btn-secondary']"
          >
            📦 所有资产
          </button>
          <button 
            @click="switchViewMode('network')" 
            :class="['btn', viewMode === 'network' ? 'btn-primary' : 'btn-secondary']"
          >
            🌐 网络设备
          </button>
        </div>
        
        <ColumnSettings 
          v-model:columns="columnConfig" 
          @apply-settings="onColumnSettingsApply"
        />
        <button @click="handleImportClick" class="btn btn-success">
          📥 导入资产
        </button>
        <button @click="handleExportClick" class="btn btn-warning">
          📄 导出资产
        </button>
        <button @click="navigateToCreate" class="btn btn-primary">
          ➕ {{ viewMode === 'network' ? '新增设备' : '新增资产' }}
        </button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <div class="search-form">
      <div class="search-row">
        <div class="form-group">
          <label>资产名称</label>
          <input 
            v-model="searchParams.name" 
            placeholder="请输入资产名称" 
            @keyup.enter="searchAssets"
            @input="onSearchInput"
          />
        </div>
        <div class="form-group">
          <label>品牌</label>
          <input 
            v-model="searchParams.brand" 
            placeholder="请输入品牌" 
            @keyup.enter="searchAssets"
            @input="onSearchInput"
          />
        </div>
        <div class="form-group">
          <label>型号</label>
          <input 
            v-model="searchParams.model" 
            placeholder="请输入型号" 
            @keyup.enter="searchAssets"
            @input="onSearchInput"
          />
        </div>
        <div class="form-group">
          <label>类别</label>
          <select v-model="searchParams.category" @change="searchAssets">
            <option value="">全部类别</option>
            <option v-for="category in categories" :key="category.id" :value="category.name">
              {{ category.name }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="search-row">
        <div class="form-group">
          <label>状态</label>
          <select v-model="searchParams.status" @change="searchAssets">
            <option value="">全部状态</option>
            <option value="在用">在用</option>
            <option value="闲置">闲置</option>
            <option value="维修">维修</option>
            <option value="报废">报废</option>
          </select>
        </div>
        <div class="form-group">
          <label>使用人</label>
          <input 
            v-model="searchParams.user_name" 
            placeholder="请输入使用人" 
            @keyup.enter="searchAssets"
            @input="onSearchInput"
          />
        </div>
        <div class="form-group">
          <label>保修状态</label>
          <select v-model="searchParams.warranty_status" @change="searchAssets">
            <option value="">全部</option>
            <option value="valid">保修中</option>
            <option value="expired">已过保</option>
            <option value="expiring">即将到期</option>
          </select>
        </div>
        <div class="form-group button-group">
          <button @click="searchAssets" class="btn btn-primary">🔍 搜索</button>
          <button @click="resetSearch" class="btn btn-info">🔄 重置</button>
        </div>
      </div>
    </div>

    <!-- 资产表格 -->
    <div class="table-container">
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>数据加载中...</p>
      </div>
      
      <table v-else class="asset-table">
        <thead>
          <tr>
            <th v-if="isColumnVisible('row_number')" width="60">序号</th>
            <th v-for="column in visibleColumns" :key="column.key" :width="column.width">
              {{ column.title }}
            </th>
            <th v-if="isColumnVisible('actions')">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(asset, index) in assetList" :key="asset.id">
            <td v-if="isColumnVisible('row_number')" class="row-number">
              {{ (pagination.page - 1) * pagination.pageSize + index + 1 }}
            </td>
            
            <!-- 动态渲染列内容 -->
            <td v-for="column in visibleColumns" :key="column.key">
              <template v-if="column.key === 'asset_code'">
                {{ asset.asset_code }}
              </template>
              <template v-else-if="column.key === 'name'">
                {{ asset.name }}
              </template>
              <template v-else-if="column.key === 'brand_model'">
                {{ asset.brand }} {{ asset.model }}
              </template>
              <template v-else-if="column.key === 'brand'">
                {{ asset.brand || '-' }}
              </template>
              <template v-else-if="column.key === 'model'">
                {{ asset.model || '-' }}
              </template>
              <template v-else-if="column.key === 'category'">
                {{ asset.category }}
              </template>
              <template v-else-if="column.key === 'specification'">
                {{ asset.specification || '-' }}
              </template>
              <template v-else-if="column.key === 'serial_number'">
                {{ asset.serial_number || '-' }}
              </template>
              <template v-else-if="column.key === 'location'">
                {{ asset.full_location || getLocationText(asset) }}
              </template>
              <template v-else-if="column.key === 'building_id'">
                {{ asset.building_id || '-' }}
              </template>
              <template v-else-if="column.key === 'floor_id'">
                {{ asset.floor_id || '-' }}
              </template>
              <template v-else-if="column.key === 'room_id'">
                {{ asset.room_id || '-' }}
              </template>
              <template v-else-if="column.key === 'location_detail'">
                {{ asset.location_detail || '-' }}
              </template>
              <template v-else-if="column.key === 'supplier'">
                {{ asset.supplier || '-' }}
              </template>
              <template v-else-if="column.key === 'purchase_date'">
                {{ formatDate(asset.purchase_date) }}
              </template>
              <template v-else-if="column.key === 'purchase_price'">
                {{ formatPrice(asset.purchase_price) }}
              </template>
              <template v-else-if="column.key === 'purchase_order'">
                {{ asset.purchase_order || '-' }}
              </template>
              <template v-else-if="column.key === 'warranty_start_date'">
                {{ formatDate(asset.warranty_start_date) }}
              </template>
              <template v-else-if="column.key === 'warranty_end_date'">
                {{ formatDate(asset.warranty_end_date) }}
              </template>
              <template v-else-if="column.key === 'warranty_period'">
                {{ asset.warranty_period ? asset.warranty_period + '个月' : '-' }}
              </template>
              <template v-else-if="column.key === 'warranty_status'">
                <span :class="`status-tag status-${getWarrantyClass(translateWarrantyStatus(asset.warranty_status))}`">
                  {{ translateWarrantyStatus(asset.warranty_status) }}
                  <span v-if="asset.warranty_days_left !== undefined">
                    ({{ asset.warranty_days_left }}天)
                  </span>
                </span>
              </template>
              <template v-else-if="column.key === 'user_name'">
                {{ asset.user_name || '-' }}
              </template>
              <template v-else-if="column.key === 'user_department'">
                {{ asset.user_department || '-' }}
              </template>
              <template v-else-if="column.key === 'deploy_date'">
                {{ formatDate(asset.deploy_date) }}
              </template>
              <template v-else-if="column.key === 'status'">
                <span :class="`status-tag status-${getStatusClass(asset.status)}`">
                  {{ asset.status }}
                </span>
              </template>
              <template v-else-if="column.key === 'condition_rating'">
                {{ asset.condition_rating || '-' }}
              </template>
              <template v-else-if="column.key === 'ip_address'">
                {{ asset.ip_address || '-' }}
              </template>
              <template v-else-if="column.key === 'mac_address'">
                {{ asset.mac_address || '-' }}
              </template>
              <template v-else-if="column.key === 'device_type'">
                {{ asset.device_type || '-' }}
              </template>
              <template v-else-if="column.key === 'subnet_mask'">
                {{ asset.subnet_mask || '-' }}
              </template>
              <template v-else-if="column.key === 'gateway'">
                {{ asset.gateway || '-' }}
              </template>
              <template v-else-if="column.key === 'dns_servers'">
                {{ asset.dns_servers || '-' }}
              </template>
              <template v-else-if="column.key === 'firmware_version'">
                {{ asset.firmware_version || '-' }}
              </template>
              <template v-else-if="column.key === 'port_count'">
                {{ asset.port_count || '-' }}
              </template>
              <template v-else-if="column.key === 'is_managed'">
                <span :class="`status-tag status-${asset.is_managed ? 'success' : 'info'}`">
                  {{ asset.is_managed ? '已纳管' : '未纳管' }}
                </span>
              </template>
              <template v-else-if="column.key === 'remark'">
                <span :title="asset.remark">
                  {{ asset.remark ? (asset.remark.length > 20 ? asset.remark.substring(0, 20) + '...' : asset.remark) : '-' }}
                </span>
              </template>
              <template v-else-if="column.key === 'created_at'">
                {{ formatDate(asset.created_at) }}
              </template>
            </td>
            
            <td v-if="isColumnVisible('actions')" class="actions">
              <button @click="viewAsset(asset)" class="btn-sm btn-info">查看</button>
              <button @click="editAsset(asset)" class="btn-sm btn-primary">编辑</button>
              <button @click="changeStatus(asset)" class="btn-sm btn-warning">状态</button>
              <button @click="deleteAsset(asset)" class="btn-sm btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 空状态 -->
      <div v-if="!loading && assetList.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <p>暂无资产数据</p>
        <button @click="navigateToCreate" class="btn btn-primary">添加第一个资产</button>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total > 0" class="pagination">
      <div class="pagination-left">
        <span class="page-size-label">每页显示</span>
        <select v-model="pagination.pageSize" @change="changePageSize" class="page-size-select">
          <option value="10">10条</option>
          <option value="20">20条</option>
          <option value="50">50条</option>
          <option value="100">100条</option>
        </select>
      </div>
      <div class="pagination-center">
        <button 
          @click="changePage(pagination.page - 1)" 
          :disabled="pagination.page <= 1"
          class="btn btn-secondary"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ pagination.page }} / {{ pagination.total_pages }} 页，
          共 {{ pagination.total }} 条记录
        </span>
        <button 
          @click="changePage(pagination.page + 1)" 
          :disabled="pagination.page >= pagination.total_pages"
          class="btn btn-secondary"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 导出对话框 -->
    <div v-if="showExportDialog" class="modal-overlay" @click="showExportDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>导出资产数据</h3>
          <button @click="showExportDialog = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="export-options">
            <h4>导出范围</h4>
            <div class="option-group">
              <label class="radio-option">
                <input type="radio" name="exportScope" value="current" checked>
                <span>当前搜索结果 ({{ pagination.total }} 条记录)</span>
              </label>
              <label class="radio-option">
                <input type="radio" name="exportScope" value="all">
                <span>所有资产数据</span>
              </label>
            </div>
            
            <h4>导出格式</h4>
            <div class="option-group">
              <label class="radio-option">
                <input type="radio" v-model="exportFormat" value="excel">
                <span>📄 Excel格式 (.xlsx)</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="exportFormat" value="csv">
                <span>📅 CSV格式 (.csv)</span>
              </label>
            </div>
            
            <div class="export-tips">
              <p>📍 导出说明：</p>
              <ul>
                <li>Excel格式支持完整的格式化和中文显示</li>
                <li>CSV格式适合导入到其他系统</li>
                <li>导出文件将自动下载到您的设备</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showExportDialog = false" class="btn btn-secondary">取消</button>
          <button @click="confirmExport" :disabled="exporting" class="btn btn-primary">
            {{ exporting ? '导出中...' : '确认导出' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 导入对话框 -->
    <div v-if="showImportDialog" class="modal-overlay" @click="showImportDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>导入资产</h3>
          <button @click="showImportDialog = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <p>请选择要导入的Excel文件：</p>
          <input 
            type="file" 
            @change="handleFileSelect" 
            accept=".xlsx,.xls"
            class="file-input"
          />
          <div class="import-tips">
            <p>📋 导入说明：</p>
            <ul>
              <li>支持 .xlsx 和 .xls 格式</li>
              <li>文件大小不超过 10MB</li>
              <li><a @click="downloadTemplate" class="link">下载导入模板</a></li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showImportDialog = false" class="btn btn-secondary">取消</button>
          <button @click="importAssets" :disabled="!selectedFile || importing" class="btn btn-primary">
            {{ importing ? '导入中...' : '确认导入' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { useRouter, useRoute, onBeforeRouteUpdate } from 'vue-router'
import { assetApi, type Asset, type AssetSearchParams } from '@/api/asset'
import type { PaginationInfo } from '@/types/common'
import { getStatusClass as getCommonStatusClass, getWarrantyStatusClass } from '@/types/common'
import ColumnSettings, { type ColumnConfig } from '@/components/assets/ColumnSettings.vue'
import { request } from '@/utils/request'

const router = useRouter()
const route = useRoute()

// 列配置数据
const columnConfig = ref<ColumnConfig[]>([
  // 基本信息
  { key: 'asset_code', title: '资产编码', visible: true, required: true, category: 'basic', width: 120 },
  { key: 'name', title: '资产名称', visible: true, required: true, category: 'basic', width: 150 },
  { key: 'brand_model', title: '品牌型号', visible: true, category: 'basic', width: 120 },
  { key: 'brand', title: '品牌', visible: false, category: 'basic', width: 100 },
  { key: 'model', title: '型号', visible: false, category: 'basic', width: 100 },
  { key: 'category', title: '类别', visible: true, required: true, category: 'basic', width: 100 },
  { key: 'specification', title: '规格', visible: false, category: 'basic', width: 150 },
  { key: 'serial_number', title: '序列号', visible: false, category: 'basic', width: 120 },
  
  // 位置信息
  { key: 'location', title: '位置', visible: true, category: 'location', width: 150 },
  { key: 'building_id', title: '楼宇ID', visible: false, category: 'location', width: 80 },
  { key: 'floor_id', title: '楼层ID', visible: false, category: 'location', width: 80 },
  { key: 'room_id', title: '房间ID', visible: false, category: 'location', width: 80 },
  { key: 'location_detail', title: '详细位置', visible: false, category: 'location', width: 150 },
  
  // 采购信息
  { key: 'supplier', title: '供应商', visible: false, category: 'purchase', width: 120 },
  { key: 'purchase_date', title: '采购日期', visible: false, category: 'purchase', width: 100 },
  { key: 'purchase_price', title: '采购价格', visible: false, category: 'purchase', width: 100 },
  { key: 'purchase_order', title: '采购订单', visible: false, category: 'purchase', width: 120 },
  
  // 保修信息
  { key: 'warranty_start_date', title: '保修开始', visible: false, category: 'warranty', width: 100 },
  { key: 'warranty_end_date', title: '保修结束', visible: false, category: 'warranty', width: 100 },
  { key: 'warranty_period', title: '保修期', visible: false, category: 'warranty', width: 80 },
  { key: 'warranty_status', title: '保修状态', visible: true, category: 'warranty', width: 120 },
  
  // 使用信息
  { key: 'user_name', title: '使用人', visible: true, category: 'user', width: 100 },
  { key: 'user_department', title: '使用部门', visible: false, category: 'user', width: 120 },
  { key: 'deploy_date', title: '部署日期', visible: false, category: 'user', width: 100 },
  { key: 'status', title: '状态', visible: true, required: true, category: 'user', width: 80 },
  { key: 'condition_rating', title: '状态评级', visible: false, category: 'user', width: 100 },
  
  // 网络信息
  { key: 'ip_address', title: 'IP地址', visible: false, category: 'network', width: 120 },
  { key: 'mac_address', title: 'MAC地址', visible: false, category: 'network', width: 140 },
  { key: 'device_type', title: '设备类型', visible: false, category: 'network', width: 100 },
  { key: 'subnet_mask', title: '子网掩码', visible: false, category: 'network', width: 120 },
  { key: 'gateway', title: '网关', visible: false, category: 'network', width: 120 },
  { key: 'dns_servers', title: 'DNS服务器', visible: false, category: 'network', width: 150 },
  { key: 'firmware_version', title: '固件版本', visible: false, category: 'network', width: 120 },
  { key: 'port_count', title: '端口数量', visible: false, category: 'network', width: 100 },
  { key: 'is_managed', title: '是否纳管', visible: false, category: 'network', width: 100 },
  
  // 其他信息
  { key: 'remark', title: '备注', visible: false, category: 'other', width: 150 },
  { key: 'created_at', title: '创建时间', visible: false, category: 'other', width: 140 },
])

// 计算可见列
const visibleColumns = computed(() => 
  columnConfig.value.filter(col => col.visible && !['row_number', 'actions'].includes(col.key))
)

// 检查列是否可见
const isColumnVisible = (key: string): boolean => {
  if (key === 'row_number' || key === 'actions') {
    return true // 序号和操作列总是可见
  }
  const column = columnConfig.value.find(col => col.key === key)
  return column?.visible ?? false
}

// 列配置应用处理
const onColumnSettingsApply = (columns: ColumnConfig[]) => {
  console.log('应用列配置:', columns)
  // 这里可以添加其他逻辑，如保存到后端等
}

// 获取位置文本
const getLocationText = (asset: Asset): string => {
  const parts = []
  if ((asset as any).building_id) parts.push(`楼宇${(asset as any).building_id}`)
  if ((asset as any).floor_id) parts.push(`${(asset as any).floor_id}楼`)
  if ((asset as any).room_id) parts.push(`${(asset as any).room_id}室`)
  if ((asset as any).location_detail) parts.push((asset as any).location_detail)
  return parts.length > 0 ? parts.join(' ') : '-'
}

// 格式化日期
const formatDate = (date: string | null | undefined): string => {
  if (!date) return '-'
  try {
    return new Date(date).toLocaleDateString('zh-CN')
  } catch {
    return '-'
  }
}

// 格式化价格
const formatPrice = (price: number | string | null | undefined): string => {
  if (!price) return '-'
  const numPrice = typeof price === 'string' ? parseFloat(price) : price
  if (isNaN(numPrice)) return '-'
  return `¥${numPrice.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
}

// 从本地存储加载列配置
const loadColumnConfig = () => {
  try {
    const savedConfig = localStorage.getItem('asset-columns-config')
    if (savedConfig) {
      const savedColumns = JSON.parse(savedConfig)
      // 应用保存的配置
      savedColumns.forEach((saved: any) => {
        const column = columnConfig.value.find(col => col.key === saved.key)
        if (column) {
          column.visible = saved.visible
          if (saved.width) column.width = saved.width
        }
      })
      console.log('列配置已从本地存储加载')
    }
  } catch (error) {
    console.error('加载列配置失败:', error)
  }
}

// 响应式数据
const loading = ref(false)
const assetList = ref<Asset[]>([])
const categories = ref<any[]>([])
const showImportDialog = ref(false)
const showExportDialog = ref(false)  // 新增导出对话框
const importing = ref(false)
const exporting = ref(false)  // 新增导出状态
const selectedFile = ref<File | null>(null)
const exportFormat = ref('excel')  // 导出格式：excel/csv

// 视图模式：asset(所有资产) / network(网络设备)
const viewMode = ref<'asset' | 'network'>('asset')

// 搜索参数
const searchParams = reactive<AssetSearchParams & { network_devices?: string }>({
  page: 1,
  pageSize: 20,  // 恢复原始命名
  name: '',
  brand: '',
  model: '',
  category: '',
  status: '',
  user_name: '',
  warranty_status: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  pageSize: 20,  // 保持用于Pagination组件显示
  total: 0,
  total_pages: 0
})

// 加载资产列表
const loadAssets = async () => {
  loading.value = true
  try {
    const response = await assetApi.getAssets(searchParams)
    
    if (response.success && response.data) {
      const data = response.data as any
      assetList.value = data.list || []
      pagination.page = data.page || 1
      pagination.pageSize = data.page_size || 20
      pagination.total = data.total || 0
      pagination.total_pages = data.total_pages || 1
    } else {
      console.error('加载资产列表失败:', response)
      assetList.value = []
    }
  } catch (error) {
    console.error('加载资产列表异常:', error)
    assetList.value = []
  } finally {
    loading.value = false
  }
}

// 加载资产类别
const loadCategories = async () => {
  try {
    const response = await request.get('/api/categories')  // 修复：使用完整的API路径
    if (response.success) {
      categories.value = response.data
    }
  } catch (error) {
    console.error('加载资产类别失败:', error)
  }
}

// 搜索资产
const searchAssets = () => {
  // 重置到第一页
  searchParams.page = 1
  pagination.page = 1
  // 执行搜索
  loadAssets()
}

// 输入搜索（可以在这里添加防抖逻辑）
const onSearchInput = () => {
  // 这里可以添加防抖逻辑，现在先简单处理
  console.log('输入变化，可以按回车或点击搜索按钮进行搜索')
}

// 重置搜索
const resetSearch = () => {
  // 清空所有搜索条件
  Object.assign(searchParams, {
    page: 1,
    pageSize: 20,
    name: '',
    brand: '',
    model: '',
    category: '',
    status: '',
    user_name: '',
    warranty_status: ''
  })
  
  // 重置分页
  pagination.page = 1
  
  // 重新加载数据
  loadAssets()
}

// 分页
const changePage = (page: number) => {
  searchParams.page = page
  loadAssets()
}

// 改变每页条数
const changePageSize = () => {
  searchParams.pageSize = pagination.pageSize  // 前端保持pageSize，API层会转换
  searchParams.page = 1  // 重置到第一页
  pagination.page = 1
  console.log('🔍 changePageSize调用，参数:', searchParams)
  loadAssets()
}

// 状态样式类
const getStatusClass = (status: string) => {
  return getCommonStatusClass(status)
}

// 保修状态样式类
const getWarrantyClass = (status: string) => {
  return getWarrantyStatusClass(status)
}

// 保修状态翻译函数
const translateWarrantyStatus = (status: string | undefined): string => {
  if (!status) return '未设置'
  
  const statusMap: Record<string, string> = {
    'valid': '保修中',
    'expired': '已过保',
    'expiring': '即将到期',
    'unknown': '未设置'
  }
  
  return statusMap[status] || status
}

// 导航功能
const navigateToCreate = () => {
  console.log('点击新增资产按钮')
  router.push('/app/assets/create')
}

const viewAsset = (asset: Asset) => {
  console.log('查看资产:', asset)
  // TODO: 打开资产详情页
}

const editAsset = (asset: Asset) => {
  router.push(`/app/assets/edit/${asset.id}`)
}

const changeStatus = (asset: Asset) => {
  console.log('变更状态:', asset)
  // TODO: 打开状态变更对话框
}

const deleteAsset = async (asset: Asset) => {
  if (confirm(`确认删除资产 "${asset.name}" 吗？`)) {
    try {
      await assetApi.deleteAsset(asset.id)
      await loadAssets()
      console.log('删除成功')
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

// 导入导出功能
const exportAssets = async () => {
  try {
    console.log('开始导出资产...', searchParams)
    
    // 显示加载提示
    const loadingMessage = '正在导出资产数据...'
    console.log(loadingMessage)
    
    // 调用导出接口
    assetApi.exportAssets(searchParams)
    
    // 显示成功提示
    setTimeout(() => {
      console.log('资产数据导出成功')
    }, 1000)
    
  } catch (error) {
    console.error('导出失败:', error)
  }
}

// 确认导出
const confirmExport = async () => {
  try {
    exporting.value = true
    console.log('开始导出资产...', { format: exportFormat.value, params: searchParams })
    
    // 调用导出接口（根据选择的格式）
    if (exportFormat.value === 'excel') {
      assetApi.exportAssets(searchParams)
    } else {
      // CSV导出（可以后续扩展）
      assetApi.exportAssets(searchParams)
    }
    
    // 关闭对话框
    showExportDialog.value = false
    
    // 显示成功提示
    setTimeout(() => {
      console.log('资产数据导出成功')
    }, 1000)
    
  } catch (error) {
    console.error('导出失败:', error)
  } finally {
    exporting.value = false
  }
}

const downloadTemplate = async () => {
  try {
    console.log('正在下载导入模板...')
    assetApi.downloadTemplate()
    setTimeout(() => {
      console.log('模板下载成功')
    }, 1000)
  } catch (error) {
    console.error('模板下载失败:', error)
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  selectedFile.value = target.files?.[0] || null
}

const importAssets = async () => {
  if (!selectedFile.value) return
  
  importing.value = true
  try {
    const response = await assetApi.importAssets(selectedFile.value)
    console.log('导入结果:', response)
    showImportDialog.value = false
    await loadAssets()
  } catch (error) {
    console.error('导入失败:', error)
  } finally {
    importing.value = false
  }
}

// 按钮点击事件处理函数
const handleImportClick = () => {
  console.log('点击导入资产按钮')
  showImportDialog.value = true
}

const handleExportClick = () => {
  console.log('点击导出资产按钮')
  showExportDialog.value = true
}

// 视图模式切换 - 简化可靠版本
const switchViewMode = (mode: 'asset' | 'network') => {
  console.log('🔄 切换视图模式:', mode)
  
  viewMode.value = mode
  
  // 设置参数
  if (mode === 'network') {
    searchParams.network_devices = 'true'
  } else {
    searchParams.network_devices = ''
  }
  
  // 重置分页
  searchParams.page = 1
  pagination.page = 1
  
  console.log('🔄 参数设置:', searchParams)
  
  // 直接调用API
  loadAssets()
  
  // 更新路由（只在必要时）
  const targetQuery = mode === 'network' ? { view: 'network' } : {}
  if (JSON.stringify(route.query) !== JSON.stringify(targetQuery)) {
    router.replace({ path: route.path, query: targetQuery })
  }
}


// 初始化数据 - 恢复简单版本
onMounted(() => {
  console.log('🚀 onMounted 开始初始化...')
  console.log('🚀 当前路由参数:', route.query)
  
  // 初始化视图模式
  if (route.query.view === 'network') {
    console.log('🚀 初始化为网络设备模式')
    viewMode.value = 'network'
    searchParams.network_devices = 'true'
  } else {
    console.log('🚀 初始化为所有资产模式')
    viewMode.value = 'asset'
    searchParams.network_devices = ''
  }
  
  // 加载数据
  loadAssets()
  loadCategories()
  loadColumnConfig()
})

// 监听路由变化 - 恢复简单版本
watch(() => route.query.view, (newView, oldView) => {
  console.log('🔄 路由参数变化，newView:', newView, 'oldView:', oldView)
  
  // 只在非初始加载时处理
  if (oldView !== undefined) {
    if (newView === 'network') {
      console.log('🔄 切换到网络设备模式')
      switchViewMode('network')
    } else {
      console.log('🔄 切换到所有资产模式')
      switchViewMode('asset')
    }
  }
}, { immediate: false })

// 添加简单的路由守卫，处理组件复用情况
onBeforeRouteUpdate((to, from, next) => {
  console.log('🛡️ 路由守卫：', { from: from.query, to: to.query })
  next()
  
  // 延迟处理确保路由更新完成
  setTimeout(() => {
    if (to.query.view === 'network') {
      console.log('🛡️ 路由守卫：切换到网络模式')
      viewMode.value = 'network'
      searchParams.network_devices = 'true'
    } else {
      console.log('🛡️ 路由守卫：切换到资产模式')
      viewMode.value = 'asset'
      searchParams.network_devices = ''
    }
    loadAssets()
  }, 50)
})


</script>

<style scoped>
.asset-list-container {
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
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.view-mode-toggle {
  display: flex;
  gap: 4px;
  margin-right: 8px;
  padding: 4px;
  background: #f5f7fa;
  border-radius: 8px;
}

.view-mode-toggle .btn {
  padding: 6px 12px;
  font-size: 13px;
  border-radius: 4px;
  transition: all 0.2s;
}

.view-mode-toggle .btn-secondary {
  background: transparent;
  color: #606266;
}

.view-mode-toggle .btn-primary {
  background: #409eff;
  color: white;
  box-shadow: 0 1px 3px rgba(64, 158, 255, 0.3);
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
  margin-bottom: 16px;
  align-items: end;
}

.search-row:last-child {
  margin-bottom: 0;
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
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
}

/* 按钮组样式 */
.button-group {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.button-group .btn {
  min-width: 80px;
  white-space: nowrap;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.asset-table {
  width: 100%;
  border-collapse: collapse;
}

.asset-table th,
.asset-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.asset-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.asset-table tbody tr:hover {
  background: #f8f9fa;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-success {
  background: #f0f9ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.status-info {
  background: #f6f7f9;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.status-warning {
  background: #fffbf0;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.status-danger {
  background: #fff2f0;
  color: #f5222d;
  border: 1px solid #ffccc7;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-info { background: #409eff; color: white; }
.btn-warning { background: #e6a23c; color: white; }
.btn-danger { background: #f56c6c; color: white; }

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-secondary {
  background: #909399;
  color: white;
}

.btn-success {
  background: #67c23a;
  color: white;
}

.btn-warning {
  background: #e6a23c;
  color: white;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

.btn:disabled {
  background: #c0c4cc !important;
  cursor: not-allowed !important;
  opacity: 0.6 !important;
}

.row-number {
  text-align: center;
  font-weight: 500;
  color: #909399;
  font-size: 13px;
  width: 60px;
}

.loading {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size-label {
  color: #606266;
  font-size: 14px;
}

.page-size-select {
  padding: 4px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.pagination-center {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-info {
  color: #606266;
  font-size: 14px;
}

/* 模态框样式 */
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
  width: 500px;
  max-width: 90vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
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
}

.modal-body {
  padding: 24px;
}

.file-input {
  width: 100%;
  padding: 8px;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  margin: 16px 0;
}

.import-tips {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  margin-top: 16px;
}

.import-tips ul {
  margin: 8px 0 0 20px;
  color: #606266;
}

.link {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
}

/* 导出选项样式 */
.export-options h4 {
  margin: 16px 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.export-options h4:first-child {
  margin-top: 0;
}

.option-group {
  margin-bottom: 20px;
}

.radio-option {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.radio-option:hover {
  background: #f5f7fa;
}

.radio-option input[type="radio"] {
  margin-right: 8px;
}

.radio-option span {
  font-size: 14px;
  color: #606266;
}

.export-tips {
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
  padding: 16px;
  margin-top: 20px;
}

.export-tips p {
  margin: 0 0 8px 0;
  font-weight: 600;
  color: #409eff;
}

.export-tips ul {
  margin: 8px 0 0 20px;
  color: #606266;
}

.export-tips li {
  font-size: 13px;
  margin-bottom: 4px;
}

@media (max-width: 768px) {
  .search-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .asset-table {
    font-size: 12px;
  }
  
  .asset-table th,
  .asset-table td {
    padding: 8px;
  }
}
</style>