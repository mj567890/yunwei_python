// 资产导出专用工具
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import type { Asset } from '@/types/common'

// 导出选项
export interface AssetExportOptions {
  filename?: string
  format?: 'excel' | 'csv'
  includeFields?: string[]
  customHeaders?: Record<string, string>
}

// 默认导出字段配置
export const DEFAULT_EXPORT_FIELDS: Record<string, string> = {
  asset_code: '资产编码',
  name: '资产名称', 
  brand: '品牌',
  model: '型号',
  category: '类别',
  status: '状态',
  user_name: '使用人',
  user_department: '使用部门',
  full_location: '位置',
  warranty_status: '保修状态',
  warranty_days_left: '保修剩余天数',
  created_at: '创建时间'
}

// 数据格式化函数
const formatValue = (value: any, field: string): string => {
  if (value === null || value === undefined) return ''
  
  switch (field) {
    case 'created_at':
      if (value) {
        try {
          return new Date(value).toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          })
        } catch {
          return String(value)
        }
      }
      return ''
    
    case 'status':
      const statusMap: Record<string, string> = {
        'active': '在用',
        'inactive': '闲置', 
        'maintenance': '维修',
        'disposed': '报废'
      }
      return statusMap[value] || String(value)
    
    case 'warranty_status':
      const warrantyMap: Record<string, string> = {
        'valid': '保修中',
        'expired': '已过保',
        'expiring': '即将到期'
      }
      return warrantyMap[value] || String(value)
    
    case 'warranty_days_left':
      if (typeof value === 'number') {
        return value >= 0 ? `${value}天` : '已过期'
      }
      return String(value)
    
    default:
      return String(value)
  }
}

// 导出Excel
export const exportAssetsToExcel = (
  assets: Asset[], 
  options: AssetExportOptions = {}
): void => {
  const {
    filename = `资产列表_${new Date().toISOString().slice(0, 10)}`,
    includeFields = Object.keys(DEFAULT_EXPORT_FIELDS),
    customHeaders = DEFAULT_EXPORT_FIELDS
  } = options

  try {
    // 准备数据
    const exportData = assets.map(asset => {
      const row: Record<string, any> = {}
      
      includeFields.forEach(field => {
        const header = customHeaders[field] || field
        const value = (asset as any)[field]
        row[header] = formatValue(value, field)
      })
      
      return row
    })

    // 创建工作簿
    const worksheet = XLSX.utils.json_to_sheet(exportData)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '资产列表')

    // 设置列宽
    const colWidths = includeFields.map(field => {
      const header = customHeaders[field] || field
      const maxLength = Math.max(
        header.length,
        ...exportData.map(row => String(row[header] || '').length)
      )
      return { wch: Math.min(Math.max(maxLength + 2, 10), 30) }
    })
    worksheet['!cols'] = colWidths

    // 导出文件
    XLSX.writeFile(workbook, `${filename}.xlsx`)
    
    console.log(`Excel文件导出成功: ${filename}.xlsx`)

  } catch (error) {
    console.error('Excel导出失败:', error)
    throw new Error('Excel导出失败')
  }
}

// 导出CSV
export const exportAssetsToCSV = (
  assets: Asset[], 
  options: AssetExportOptions = {}
): void => {
  const {
    filename = `资产列表_${new Date().toISOString().slice(0, 10)}`,
    includeFields = Object.keys(DEFAULT_EXPORT_FIELDS),
    customHeaders = DEFAULT_EXPORT_FIELDS
  } = options

  try {
    // 准备表头
    const headers = includeFields.map(field => customHeaders[field] || field)
    
    // 准备数据
    const rows = assets.map(asset => {
      return includeFields.map(field => {
        const value = (asset as any)[field]
        return formatValue(value, field)
      })
    })

    // 创建CSV内容
    const csvContent = [
      headers.join(','),
      ...rows.map(row => 
        row.map(cell => {
          // 处理包含逗号或引号的内容
          const cellStr = String(cell)
          if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
            return `"${cellStr.replace(/"/g, '""')}"`
          }
          return cellStr
        }).join(',')
      )
    ].join('\n')

    // 添加BOM以支持中文
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { 
      type: 'text/csv;charset=utf-8;' 
    })
    
    saveAs(blob, `${filename}.csv`)
    
    console.log(`CSV文件导出成功: ${filename}.csv`)

  } catch (error) {
    console.error('CSV导出失败:', error)
    throw new Error('CSV导出失败')
  }
}

// 统一导出函数
export const exportAssets = (
  assets: Asset[], 
  options: AssetExportOptions = {}
): void => {
  const { format = 'excel' } = options

  if (format === 'excel') {
    exportAssetsToExcel(assets, options)
  } else if (format === 'csv') {
    exportAssetsToCSV(assets, options)
  } else {
    throw new Error(`不支持的导出格式: ${format}`)
  }
}

// 预设导出配置
export const EXPORT_PRESETS = {
  // 基本信息导出
  basic: {
    includeFields: ['asset_code', 'name', 'brand', 'model', 'category', 'status'],
    customHeaders: {
      asset_code: '资产编码',
      name: '资产名称',
      brand: '品牌',
      model: '型号', 
      category: '类别',
      status: '状态'
    }
  },
  
  // 完整信息导出
  full: {
    includeFields: Object.keys(DEFAULT_EXPORT_FIELDS),
    customHeaders: DEFAULT_EXPORT_FIELDS
  },
  
  // 保修信息导出
  warranty: {
    includeFields: ['asset_code', 'name', 'warranty_status', 'warranty_days_left'],
    customHeaders: {
      asset_code: '资产编码',
      name: '资产名称',
      warranty_status: '保修状态',
      warranty_days_left: '保修剩余天数'
    }
  },
  
  // 使用情况导出
  usage: {
    includeFields: ['asset_code', 'name', 'user_name', 'user_department', 'full_location', 'status'],
    customHeaders: {
      asset_code: '资产编码',
      name: '资产名称',
      user_name: '使用人',
      user_department: '使用部门',
      full_location: '位置',
      status: '状态'
    }
  }
}

// 导出预设快捷函数
export const exportWithPreset = (
  assets: Asset[], 
  presetName: keyof typeof EXPORT_PRESETS,
  format: 'excel' | 'csv' = 'excel',
  filename?: string
): void => {
  const preset = EXPORT_PRESETS[presetName]
  if (!preset) {
    throw new Error(`未找到预设配置: ${presetName}`)
  }
  
  exportAssets(assets, {
    ...preset,
    format,
    filename: filename || `资产${presetName === 'basic' ? '基本信息' : 
                              presetName === 'warranty' ? '保修信息' :
                              presetName === 'usage' ? '使用情况' : '完整信息'}_${new Date().toISOString().slice(0, 10)}`
  })
}