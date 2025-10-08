// 数据导出工具
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

// 导出格式类型
export type ExportFormat = 'excel' | 'csv' | 'json'

// 导出选项
export interface ExportOptions {
  filename?: string
  sheetName?: string
  format?: ExportFormat
  headers?: string[]
}

// 通用导出函数
export const exportData = (
  data: any[], 
  options: ExportOptions = {}
) => {
  const {
    filename = `导出数据_${new Date().toISOString().slice(0, 19).replace(/[T:]/g, '_')}`,
    sheetName = 'Sheet1',
    format = 'excel',
    headers
  } = options

  try {
    switch (format) {
      case 'excel':
        exportToExcel(data, filename, sheetName, headers)
        break
      case 'csv':
        exportToCSV(data, filename, headers)
        break
      case 'json':
        exportToJSON(data, filename)
        break
      default:
        throw new Error(`不支持的导出格式: ${format}`)
    }
  } catch (error) {
    console.error('导出失败:', error)
    throw error
  }
}

// 导出Excel
const exportToExcel = (
  data: any[], 
  filename: string, 
  sheetName: string,
  headers?: string[]
) => {
  // 创建工作簿
  const workbook = XLSX.utils.book_new()
  
  // 处理数据
  let processedData = data
  if (headers && data.length > 0) {
    // 如果指定了表头，重新组织数据
    processedData = data.map(item => {
      const row: any = {}
      headers.forEach(header => {
        row[header] = item[header] ?? ''
      })
      return row
    })
  }
  
  // 创建工作表
  const worksheet = XLSX.utils.json_to_sheet(processedData)
  
  // 设置列宽
  const colWidths = Object.keys(processedData[0] || {}).map(() => ({ wch: 15 }))
  worksheet['!cols'] = colWidths
  
  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)
  
  // 导出文件
  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  saveAs(blob, `${filename}.xlsx`)
}

// 导出CSV
const exportToCSV = (
  data: any[], 
  filename: string,
  headers?: string[]
) => {
  let csvContent = ''
  
  if (data.length === 0) {
    throw new Error('没有数据可导出')
  }
  
  // 处理表头
  const keys = headers || Object.keys(data[0])
  csvContent += keys.join(',') + '\n'
  
  // 处理数据行
  data.forEach(item => {
    const row = keys.map(key => {
      const value = item[key] ?? ''
      // 处理包含逗号或引号的值
      if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
        return `"${value.replace(/"/g, '""')}"`
      }
      return value
    })
    csvContent += row.join(',') + '\n'
  })
  
  // 添加BOM以支持中文
  const BOM = '\uFEFF'
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
  saveAs(blob, `${filename}.csv`)
}

// 导出JSON
const exportToJSON = (data: any[], filename: string) => {
  const jsonContent = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
  saveAs(blob, `${filename}.json`)
}

// 资产数据导出
export const exportAssets = (assets: any[]) => {
  const headers = [
    'asset_code', 'name', 'category', 'brand', 'model', 
    'status', 'location', 'user_name', 'purchase_date', 
    'warranty_date', 'price', 'created_at'
  ]
  
  const processedData = assets.map(asset => ({
    asset_code: asset.asset_code || '',
    name: asset.name || '',
    category: asset.category || '',
    brand: asset.brand || '',
    model: asset.model || '',
    status: asset.status || '',
    location: asset.full_location || asset.location || '',
    user_name: asset.user_name || '',
    purchase_date: asset.purchase_date || '',
    warranty_date: asset.warranty_date || '',
    price: asset.price || '',
    created_at: asset.created_at || ''
  }))
  
  exportData(processedData, {
    filename: '资产列表',
    sheetName: '资产数据',
    headers: [
      '资产编码', '资产名称', '类别', '品牌', '型号',
      '状态', '位置', '使用人', '采购日期', 
      '保修期', '价格', '创建时间'
    ]
  })
}

// 用户数据导出
export const exportUsers = (users: any[]) => {
  const processedData = users.map(user => ({
    username: user.username || '',
    real_name: user.real_name || '',
    email: user.email || '',
    phone: user.phone || '',
    department: user.department || '',
    status: user.status === 1 ? '启用' : '禁用',
    roles: user.roles?.map((r: any) => r.name).join(', ') || '',
    last_login_time: user.last_login_time || '',
    created_at: user.created_at || ''
  }))
  
  exportData(processedData, {
    filename: '用户列表',
    sheetName: '用户数据',
    headers: [
      '用户名', '真实姓名', '邮箱', '电话', '部门',
      '状态', '角色', '最后登录', '创建时间'
    ]
  })
}

// 故障数据导出
export const exportFaults = (faults: any[]) => {
  const processedData = faults.map(fault => ({
    fault_code: fault.fault_code || '',
    title: fault.title || '',
    fault_type: fault.fault_type || '',
    severity: fault.severity || '',
    priority: fault.priority || '',
    status: fault.status || '',
    reporter_name: fault.reporter_name || '',
    report_time: fault.report_time || '',
    assignee_name: fault.assignee_name || '',
    response_time: fault.response_time || '',
    created_at: fault.created_at || ''
  }))
  
  exportData(processedData, {
    filename: '故障列表',
    sheetName: '故障数据',
    headers: [
      '故障编码', '故障标题', '故障类型', '严重程度', '优先级',
      '状态', '报告人', '报告时间', '分配人', '响应时间', '创建时间'
    ]
  })
}

// 运维记录导出
export const exportMaintenanceRecords = (records: any[]) => {
  const processedData = records.map(record => ({
    record_code: record.record_code || '',
    title: record.title || '',
    record_type: record.record_type || '',
    category: record.category || '',
    responsible_person: record.responsible_person || '',
    department: record.department || '',
    status: record.status || '',
    priority: record.priority || '',
    progress: `${record.progress || 0}%`,
    start_time: record.start_time || '',
    created_at: record.created_at || ''
  }))
  
  exportData(processedData, {
    filename: '运维记录',
    sheetName: '运维数据',
    headers: [
      '记录编码', '标题', '记录类型', '分类', '负责人',
      '部门', '状态', '优先级', '进度', '开始时间', '创建时间'
    ]
  })
}