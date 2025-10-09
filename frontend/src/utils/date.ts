/**
 * 日期格式化工具函数
 */

/**
 * 格式化日期
 * @param dateString - 日期字符串
 * @param format - 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 */
export const formatDate = (dateString: string | null | undefined, format = 'YYYY-MM-DD HH:mm:ss'): string => {
  if (!dateString) return '-'
  
  try {
    const date = new Date(dateString)
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return '-'
    }
    
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    
    // 简单的格式替换
    return format
      .replace('YYYY', String(year))
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hours)
      .replace('mm', minutes)
      .replace('ss', seconds)
  } catch (error) {
    console.error('日期格式化失败:', error)
    return '-'
  }
}

/**
 * 格式化为日期（不包含时间）
 * @param dateString - 日期字符串
 */
export const formatDateOnly = (dateString: string | null | undefined): string => {
  return formatDate(dateString, 'YYYY-MM-DD')
}

/**
 * 格式化为时间（不包含日期）
 * @param dateString - 日期字符串
 */
export const formatTimeOnly = (dateString: string | null | undefined): string => {
  return formatDate(dateString, 'HH:mm:ss')
}

/**
 * 格式化为相对时间（如：2天前、3小时前）
 * @param dateString - 日期字符串
 */
export const formatRelativeTime = (dateString: string | null | undefined): string => {
  if (!dateString) return '-'
  
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    // 转换为秒、分钟、小时、天
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    
    if (days > 0) {
      return `${days}天前`
    } else if (hours > 0) {
      return `${hours}小时前`
    } else if (minutes > 0) {
      return `${minutes}分钟前`
    } else if (seconds > 0) {
      return `${seconds}秒前`
    } else {
      return '刚刚'
    }
  } catch (error) {
    console.error('相对时间格式化失败:', error)
    return '-'
  }
}

/**
 * 检查日期是否为今天
 * @param dateString - 日期字符串
 */
export const isToday = (dateString: string | null | undefined): boolean => {
  if (!dateString) return false
  
  try {
    const date = new Date(dateString)
    const today = new Date()
    
    return date.getFullYear() === today.getFullYear() &&
           date.getMonth() === today.getMonth() &&
           date.getDate() === today.getDate()
  } catch (error) {
    return false
  }
}

/**
 * 获取当前日期时间字符串
 * @param format - 格式化模板
 */
export const getCurrentDateTime = (format = 'YYYY-MM-DD HH:mm:ss'): string => {
  return formatDate(new Date().toISOString(), format)
}