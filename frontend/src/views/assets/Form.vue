<template>
  <div class="asset-form-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>{{ isEdit ? '编辑资产' : '新增资产' }}</h1>
      <div class="header-actions">
        <button @click="goBack" class="btn btn-secondary">
          ← 返回列表
        </button>
        <button @click="saveAsset" :disabled="saving" class="btn btn-primary">
          {{ saving ? '保存中...' : '💾 保存' }}
        </button>
      </div>
    </div>

    <!-- 表单内容 -->
    <div class="form-container">
      <form @submit.prevent="saveAsset">
        <!-- 基本信息 -->
        <div class="form-section">
          <h2>基本信息</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>资产编码 <span class="required">*</span></label>
              <input 
                v-model="formData.asset_code" 
                placeholder="自动生成或手动输入"
                :disabled="isEdit"
                data-field="asset_code"
                @input="clearFieldError('asset_code')"
              />
              <span v-if="validationErrors.asset_code" class="error-text">{{ validationErrors.asset_code }}</span>
            </div>
            
            <div class="form-group">
              <label>资产名称 <span class="required">*</span></label>
              <input 
                v-model="formData.name" 
                placeholder="请输入资产名称"
                required
                data-field="name"
                @input="clearFieldError('name')"
              />
              <span v-if="validationErrors.name" class="error-text">{{ validationErrors.name }}</span>
            </div>
            
            <div class="form-group">
              <label>品牌</label>
              <input 
                v-model="formData.brand" 
                placeholder="请输入品牌"
                data-field="brand"
                @input="clearFieldError('brand')"
              />
            </div>
            
            <div class="form-group">
              <label>型号</label>
              <input 
                v-model="formData.model" 
                placeholder="请输入型号"
                data-field="model"
                @input="clearFieldError('model')"
              />
            </div>
            
            <div class="form-group">
              <label>资产类别 <span class="required">*</span></label>
              <select 
                v-model="formData.category" 
                required
                data-field="category"
                @change="clearFieldError('category')"
              >
                <option value="">请选择类别</option>
                <option v-for="category in categories" :key="category.id" :value="category.name">
                  {{ category.name }}
                </option>
              </select>
              <span v-if="validationErrors.category" class="error-text">{{ validationErrors.category }}</span>
            </div>
            
            <div class="form-group">
              <label>序列号</label>
              <input 
                v-model="formData.serial_number" 
                placeholder="请输入序列号"
                data-field="serial_number"
                @input="clearFieldError('serial_number')"
              />
            </div>
          </div>
          
          <div class="form-group full-width">
            <label>规格参数</label>
            <textarea 
              v-model="formData.specification" 
              placeholder="请输入规格参数"
              rows="3"
            ></textarea>
          </div>
        </div>

        <!-- 位置信息 -->
        <div class="form-section">
          <h2>位置信息</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>楼宇</label>
              <select v-model="formData.building_id" @change="onBuildingChange">
                <option value="">请选择楼宇</option>
                <option v-for="building in buildings" :key="building.id" :value="building.id">
                  {{ building.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>楼层</label>
              <select v-model="formData.floor_id" @change="onFloorChange" :disabled="!formData.building_id">
                <option value="">请选择楼层</option>
                <option v-for="floor in floors" :key="floor.id" :value="floor.id">
                  {{ floor.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>房间</label>
              <select v-model="formData.room_id" :disabled="!formData.floor_id">
                <option value="">请选择房间</option>
                <option v-for="room in rooms" :key="room.id" :value="room.id">
                  {{ room.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>详细位置</label>
              <input 
                v-model="formData.location_detail" 
                placeholder="如：A机柜第3层"
              />
            </div>
          </div>
        </div>

        <!-- 采购信息 -->
        <div class="form-section">
          <h2>采购信息</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>供应商</label>
              <input 
                v-model="formData.supplier" 
                placeholder="请输入供应商"
              />
            </div>
            
            <div class="form-group">
              <label>采购日期</label>
              <input 
                v-model="formData.purchase_date" 
                type="date"
              />
            </div>
            
            <div class="form-group">
              <label>采购价格</label>
              <input 
                v-model="formData.purchase_price" 
                type="number"
                step="0.01"
                min="0"
                placeholder="请输入采购价格"
                data-field="purchase_price"
                @input="clearFieldError('purchase_price')"
              />
              <span v-if="validationErrors.purchase_price" class="error-text">{{ validationErrors.purchase_price }}</span>
            </div>
            
            <div class="form-group">
              <label>采购订单号</label>
              <input 
                v-model="formData.purchase_order" 
                placeholder="请输入订单号"
              />
            </div>
          </div>
        </div>

        <!-- 保修信息 -->
        <div class="form-section">
          <h2>保修信息</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>保修开始日期</label>
              <input 
                v-model="formData.warranty_start_date" 
                type="date"
                data-field="warranty_start_date"
                @change="clearFieldError('warranty_start_date')"
              />
            </div>
            
            <div class="form-group">
              <label>保修结束日期</label>
              <input 
                v-model="formData.warranty_end_date" 
                type="date"
                data-field="warranty_end_date"
                @change="clearFieldError('warranty_end_date')"
              />
              <span v-if="validationErrors.warranty_end_date" class="error-text">{{ validationErrors.warranty_end_date }}</span>
            </div>
            
            <div class="form-group">
              <label>保修期(月)</label>
              <input 
                v-model="formData.warranty_period" 
                type="number"
                min="0"
                placeholder="请输入保修期"
                data-field="warranty_period"
                @input="clearFieldError('warranty_period')"
              />
              <span v-if="validationErrors.warranty_period" class="error-text">{{ validationErrors.warranty_period }}</span>
            </div>
          </div>
        </div>

        <!-- 使用信息 -->
        <div class="form-section">
          <h2>使用信息</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>使用人</label>
              <input 
                v-model="formData.user_name" 
                placeholder="请输入使用人"
              />
            </div>
            
            <div class="form-group">
              <label>使用部门</label>
              <input 
                v-model="formData.user_department" 
                placeholder="请输入使用部门"
              />
            </div>
            
            <div class="form-group">
              <label>部署日期</label>
              <input 
                v-model="formData.deploy_date" 
                type="date"
                data-field="deploy_date"
                @change="clearFieldError('deploy_date')"
              />
              <span v-if="validationErrors.deploy_date" class="error-text">{{ validationErrors.deploy_date }}</span>
            </div>
            
            <div class="form-group">
              <label>资产状态</label>
              <select v-model="formData.status">
                <option value="在用">在用</option>
                <option value="闲置">闲置</option>
                <option value="维修">维修</option>
                <option value="报废">报废</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 网络信息 -->
        <div class="form-section">
          <h2>网络信息</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>MAC地址</label>
              <input 
                v-model="formData.mac_address" 
                placeholder="如：00:1B:44:11:3A:B7"
                pattern="^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
                data-field="mac_address"
                @input="clearFieldError('mac_address')"
              />
              <span v-if="validationErrors.mac_address" class="error-text">{{ validationErrors.mac_address }}</span>
            </div>
            
            <div class="form-group">
              <label>IP地址</label>
              <input 
                v-model="formData.ip_address" 
                placeholder="如：192.168.1.100"
                pattern="^(\d{1,3}\.){3}\d{1,3}$"
                data-field="ip_address"
                @input="clearFieldError('ip_address')"
              />
              <span v-if="validationErrors.ip_address" class="error-text">{{ validationErrors.ip_address }}</span>
            </div>
            
            <div class="form-group">
              <label>状况评级</label>
              <select v-model="formData.condition_rating">
                <option value="">请选择</option>
                <option value="优">优</option>
                <option value="良">良</option>
                <option value="中">中</option>
                <option value="差">差</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 备注信息 -->
        <div class="form-section">
          <h2>备注信息</h2>
          <div class="form-group full-width">
            <label>备注</label>
            <textarea 
              v-model="formData.remark" 
              placeholder="请输入备注信息"
              rows="4"
            ></textarea>
          </div>
        </div>

        <!-- 二维码生成 -->
        <div class="form-section" v-if="isEdit">
          <h2>二维码标签</h2>
          <div class="qr-code-section">
            <div class="qr-display">
              <canvas 
                ref="qrCodeCanvas" 
                width="200" 
                height="200"
                v-show="qrCodeGenerated"
              ></canvas>
              <div v-show="!qrCodeGenerated" class="qr-placeholder">
                <p>点击“生成二维码”按钮生成资产二维码</p>
              </div>
            </div>
            <div class="qr-actions">
              <button type="button" @click="generateQRCode" class="btn btn-secondary">
                🔄 生成二维码
              </button>
              <button 
                type="button" 
                @click="printQRCode" 
                :disabled="!qrCodeGenerated"
                class="btn btn-secondary"
              >
                🖨️ 打印标签
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { assetApi, type Asset } from '@/api/asset'
import { locationApi } from '@/api/location'
import type { StatusType } from '@/types/common'
import QRCode from 'qrcode'
import { request } from '@/utils/request'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const qrCodeCanvas = ref<HTMLCanvasElement | null>(null)
const qrCodeGenerated = ref(false)

// 计算属性
const isEdit = computed(() => !!route.params.id)
const assetId = computed(() => route.params.id ? parseInt(route.params.id as string) : null)

// 表单数据
interface AssetFormData {
  asset_code: string
  name: string
  brand: string
  model: string
  category: string
  specification: string
  building_id: number | null
  floor_id: number | null
  room_id: number | null
  location_detail: string
  supplier: string
  purchase_date: string
  purchase_price: number | null
  purchase_order: string
  warranty_start_date: string
  warranty_end_date: string
  warranty_period: number | null
  user_name: string
  user_department: string
  deploy_date: string
  status: string
  condition_rating: string
  serial_number: string
  mac_address: string
  ip_address: string
  remark: string
}

const formData = reactive<AssetFormData>({
  asset_code: '',
  name: '',
  brand: '',
  model: '',
  category: '',
  specification: '',
  building_id: null,
  floor_id: null,
  room_id: null,
  location_detail: '',
  supplier: '',
  purchase_date: '',
  purchase_price: null,
  purchase_order: '',
  warranty_start_date: '',
  warranty_end_date: '',
  warranty_period: null,
  user_name: '',
  user_department: '',
  deploy_date: '',
  status: '在用',
  condition_rating: '',
  serial_number: '',
  mac_address: '',
  ip_address: '',
  remark: ''
})

// 选择器数据
const categories = ref<any[]>([])
const buildings = ref<any[]>([])
const floors = ref<any[]>([])
const rooms = ref<any[]>([])



// 加载资产数据
const loadAsset = async () => {
  if (!assetId.value) return
  
  loading.value = true
  try {
    const response = await assetApi.getAsset(assetId.value)
    if (response.success) {
      Object.assign(formData, response.data)
      
      // 加载位置级联数据
      if (formData.building_id) {
        await loadFloors(formData.building_id)
        if (formData.floor_id) {
          await loadRooms(formData.floor_id)
        }
      }
    }
  } catch (error) {
    console.error('加载资产失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载基础数据
const loadCategories = async () => {
  try {
    const response = await request.get('/api/categories')  // 统一使用完整API路径
    if (response.success) {
      categories.value = response.data
    }
  } catch (error) {
    console.error('加载类别失败:', error)
  }
}

const loadBuildings = async () => {
  try {
    const response = await locationApi.getBuildings()
    if (response.success) {
      buildings.value = response.data
    }
  } catch (error) {
    console.error('加载楼宇失败:', error)
  }
}

const loadFloors = async (buildingId: number) => {
  try {
    const response = await locationApi.getFloors(buildingId)
    if (response.success) {
      floors.value = response.data
    }
  } catch (error) {
    console.error('加载楼层失败:', error)
  }
}

const loadRooms = async (floorId: number) => {
  try {
    const response = await locationApi.getRooms(floorId)
    if (response.success) {
      rooms.value = response.data
    }
  } catch (error) {
    console.error('加载房间失败:', error)
  }
}

// 位置级联处理
const onBuildingChange = () => {
  formData.floor_id = null
  formData.room_id = null
  floors.value = []
  rooms.value = []
  
  if (formData.building_id) {
    loadFloors(formData.building_id)
  }
}

const onFloorChange = () => {
  formData.room_id = null
  rooms.value = []
  
  if (formData.floor_id) {
    loadRooms(formData.floor_id)
  }
}

// 表单验证状态
const validationErrors = ref<Record<string, string>>({})

// 表单验证函数
const validateForm = (): boolean => {
  const errors: Record<string, string> = {}
  
  // 必填字段验证
  if (!formData.name?.trim()) {
    errors.name = '资产名称不能为空'
  }
  
  if (!formData.category?.trim()) {
    errors.category = '资产类别不能为空'
  }
  
  // IP地址格式验证
  if (formData.ip_address && !/^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(formData.ip_address)) {
    errors.ip_address = 'IP地址格式不正确'
  }
  
  // MAC地址格式验证
  if (formData.mac_address && !/^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/.test(formData.mac_address)) {
    errors.mac_address = 'MAC地址格式不正确，例如：00:1B:44:11:3A:B7'
  }
  
  // 数字字段验证
  if (formData.purchase_price && formData.purchase_price < 0) {
    errors.purchase_price = '采购价格不能为负数'
  }
  
  if (formData.warranty_period && formData.warranty_period < 0) {
    errors.warranty_period = '保修期不能为负数'
  }
  
  // 日期逻辑验证
  if (formData.warranty_start_date && formData.warranty_end_date) {
    const startDate = new Date(formData.warranty_start_date)
    const endDate = new Date(formData.warranty_end_date)
    if (startDate >= endDate) {
      errors.warranty_end_date = '保修结束日期必须晚于开始日期'
    }
  }
  
  if (formData.purchase_date && formData.deploy_date) {
    const purchaseDate = new Date(formData.purchase_date)
    const deployDate = new Date(formData.deploy_date)
    if (deployDate < purchaseDate) {
      errors.deploy_date = '部署日期不能早于采购日期'
    }
  }
  
  validationErrors.value = errors
  return Object.keys(errors).length === 0
}

// 清除特定字段的验证错误
const clearFieldError = (field: string) => {
  if (validationErrors.value[field]) {
    delete validationErrors.value[field]
  }
}

// 显示成功消息
const showSuccessMessage = (message: string) => {
  // 创建临时提示元素
  const toast = document.createElement('div')
  toast.className = 'success-toast'
  toast.textContent = message
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #67c23a;
    color: white;
    padding: 12px 20px;
    border-radius: 6px;
    z-index: 10000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    animation: slideIn 0.3s ease;
  `
  
  // 添加样式
  if (!document.querySelector('#toast-styles')) {
    const styles = document.createElement('style')
    styles.id = 'toast-styles'
    styles.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `
    document.head.appendChild(styles)
  }
  
  document.body.appendChild(toast)
  
  // 3秒后自动移除
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast)
    }
  }, 3000)
}

// 显示错误消息
const showErrorMessage = (message: string) => {
  // 创建临时提示元素
  const toast = document.createElement('div')
  toast.className = 'error-toast'
  toast.textContent = message
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #f56c6c;
    color: white;
    padding: 12px 20px;
    border-radius: 6px;
    z-index: 10000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    animation: slideIn 0.3s ease;
  `
  
  document.body.appendChild(toast)
  
  // 5秒后自动移除
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast)
    }
  }, 5000)
}

// 保存资产
const saveAsset = async () => {
  // 表单验证
  if (!validateForm()) {
    showErrorMessage('请检查表单填写，修正错误后再提交')
    // 滚动到第一个错误字段
    const firstErrorField = Object.keys(validationErrors.value)[0]
    if (firstErrorField) {
      const errorElement = document.querySelector(`[data-field="${firstErrorField}"]`) as HTMLElement
      if (errorElement) {
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        errorElement.focus()
      }
    }
    return
  }
  
  saving.value = true
  try {
    // 准备提交数据
    const submitData = {
      ...formData,
      // 确保数字字段正确转换
      purchase_price: formData.purchase_price ? Number(formData.purchase_price) : undefined,
      warranty_period: formData.warranty_period ? Number(formData.warranty_period) : undefined,
      building_id: formData.building_id || undefined,
      floor_id: formData.floor_id || undefined,
      room_id: formData.room_id || undefined,
      // 清理空字符串
      asset_code: formData.asset_code?.trim() || undefined,
      name: formData.name?.trim(),
      brand: formData.brand?.trim() || undefined,
      model: formData.model?.trim() || undefined,
      category: formData.category?.trim(),
      specification: formData.specification?.trim() || undefined,
      serial_number: formData.serial_number?.trim() || undefined,
      supplier: formData.supplier?.trim() || undefined,
      purchase_order: formData.purchase_order?.trim() || undefined,
      user_name: formData.user_name?.trim() || undefined,
      user_department: formData.user_department?.trim() || undefined,
      location_detail: formData.location_detail?.trim() || undefined,
      mac_address: formData.mac_address?.trim() || undefined,
      ip_address: formData.ip_address?.trim() || undefined,
      condition_rating: formData.condition_rating?.trim() || undefined,
      remark: formData.remark?.trim() || undefined,
      // 确保状态类型正确
      status: formData.status as StatusType
    }
    
    console.log('准备提交的数据:', submitData)
    
    let response
    if (isEdit.value && assetId.value) {
      response = await assetApi.updateAsset(assetId.value, submitData)
    } else {
      response = await assetApi.createAsset(submitData)
    }
    
    if (response.success) {
      const message = isEdit.value ? '资产更新成功！' : '资产创建成功！'
      showSuccessMessage(message)
      console.log('保存成功，响应数据:', response.data)
      
      // 延迟返回以显示成功消息
      setTimeout(() => {
        goBack()
      }, 1500)
    } else {
      throw new Error(response.message || '保存失败')
    }
  } catch (error: any) {
    console.error('保存失败:', error)
    let errorMessage = '保存失败，请稍后重试'
    
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.message) {
      errorMessage = error.message
    }
    
    showErrorMessage(errorMessage)
  } finally {
    saving.value = false
  }
}

// 返回列表
const goBack = () => {
  router.push('/app/assets/list')
}

// 二维码功能
const generateQRCode = async () => {
  if (!formData.asset_code) {
    alert('请先保存资产信息后再生成二维码')
    return
  }
  
  try {
    // 生成二维码数据（包含资产基本信息）
    const qrData = {
      asset_code: formData.asset_code,
      name: formData.name,
      category: formData.category,
      location: `${formData.building_id || ''}-${formData.floor_id || ''}-${formData.room_id || ''}`,
      url: `${window.location.origin}/#/app/assets/${assetId.value || ''}`
    }
    
    const qrText = JSON.stringify(qrData)
    
    if (qrCodeCanvas.value) {
      // 清除画布
      const ctx = qrCodeCanvas.value.getContext('2d')
      if (ctx) {
        ctx.clearRect(0, 0, qrCodeCanvas.value.width, qrCodeCanvas.value.height)
      }
      
      // 生成二维码
      await QRCode.toCanvas(qrCodeCanvas.value, qrText, {
        width: 200,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      })
      
      qrCodeGenerated.value = true
      console.log('二维码生成成功')
    }
  } catch (error) {
    console.error('生成二维码失败:', error)
    alert('生成二维码失败，请稍后重试')
  }
}

const printQRCode = () => {
  if (!qrCodeGenerated.value || !qrCodeCanvas.value) {
    alert('请先生成二维码')
    return
  }
  
  try {
    // 创建打印窗口
    const printWindow = window.open('', '_blank')
    if (!printWindow) {
      alert('无法打开打印窗口，请检查浏览器设置')
      return
    }
    
    // 获取二维码图像数据
    const imageData = qrCodeCanvas.value.toDataURL('image/png')
    
    // 构建打印内容
    const printContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>资产二维码 - ${formData.asset_code}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 20px;
          }
          .qr-container {
            border: 2px solid #000;
            padding: 20px;
            display: inline-block;
            margin: 20px auto;
          }
          .asset-info {
            margin: 10px 0;
            font-size: 14px;
          }
          .asset-code {
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
          }
          @media print {
            body { margin: 0; }
            .qr-container { border: 1px solid #000; }
          }
        </style>
      </head>
      <body>
        <div class="qr-container">
          <div class="asset-info">资产名称：${formData.name || '-'}</div>
          <div class="asset-code">资产编码：${formData.asset_code}</div>
          <img src="${imageData}" alt="资产二维码" />
          <div class="asset-info">类别：${formData.category || '-'}</div>
          <div class="asset-info">生成时间：${new Date().toLocaleString('zh-CN')}</div>
        </div>
      </body>
      </html>
    `
    
    // 写入打印内容并打印
    printWindow.document.write(printContent)
    printWindow.document.close()
    
    // 等待图片加载后打印
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print()
        printWindow.close()
      }, 500)
    }
    
    console.log('打印二维码')
  } catch (error) {
    console.error('打印失败:', error)
    alert('打印失败，请稍后重试')
  }
}

// 初始化
onMounted(() => {
  if (isEdit.value) {
    loadAsset()
  }
  loadCategories()
  loadBuildings()
})
</script>

<style scoped>
.asset-form-container {
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
}

.form-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.form-section {
  padding: 30px;
  border-bottom: 1px solid #ebeef5;
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h2 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.required {
  color: #f56c6c;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #409eff;
}

.form-group input:disabled {
  background: #f5f7fa;
  color: #c0c4cc;
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #f56c6c;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.btn {
  padding: 10px 20px;
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

.btn:hover {
  opacity: 0.8;
}

.btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.qr-code-section {
  display: flex;
  gap: 30px;
  align-items: center;
}

.qr-display {
  text-align: center;
}

.qr-placeholder {
  width: 200px;
  height: 200px;
  border: 2px dashed #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
  border-radius: 6px;
}

.qr-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

canvas {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .qr-code-section {
    flex-direction: column;
    text-align: center;
  }
}
</style>