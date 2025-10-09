/**
 * 前端加密工具
 * 用于安全存储敏感信息如Token
 */
import CryptoJS from 'crypto-js'

// 密钥生成（从环境变量获取，增强安全性）
// @ts-ignore
const SECRET_KEY = import.meta.env.VITE_CRYPTO_SECRET || 'fallback-key-change-in-production'

// 验证环境变量是否正确设置
// @ts-ignore
if (import.meta.env.PROD && import.meta.env.VITE_CRYPTO_SECRET === undefined) {
  console.error('生产环境必须设置VITE_CRYPTO_SECRET环境变量')
}

/**
 * 加密数据
 * @param data 要加密的数据
 * @returns 加密后的字符串
 */
export function encrypt(data: string): string {
  try {
    return CryptoJS.AES.encrypt(data, SECRET_KEY).toString()
  } catch (error) {
    console.error('加密失败:', error)
    return data
  }
}

/**
 * 解密数据
 * @param encryptedData 加密的数据
 * @returns 解密后的字符串
 */
export function decrypt(encryptedData: string): string {
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedData, SECRET_KEY)
    return bytes.toString(CryptoJS.enc.Utf8)
  } catch (error) {
    console.error('解密失败:', error)
    return encryptedData
  }
}

/**
 * 安全存储Token到localStorage
 * 使用双重加密和时间戳验证
 * @param token Token字符串
 */
export function setSecureToken(token: string): void {
  try {
    // 生成时间戳和随机盐
    const timestamp = Date.now()
    const salt = CryptoJS.lib.WordArray.random(16).toString()
    
    // 创建包含元数据的Token对象
    const tokenData = {
      token,
      timestamp,
      salt,
      checksum: CryptoJS.SHA256(token + timestamp + salt).toString()
    }
    
    // 第一层加密：使用AES加密
    const firstEncryption = CryptoJS.AES.encrypt(JSON.stringify(tokenData), SECRET_KEY + salt).toString()
    
    // 第二层加密：使用Base64和简单混淆
    const finalToken = btoa(firstEncryption + '::' + salt)
    
    localStorage.setItem('secure_auth_token', finalToken)
    localStorage.setItem('token_version', '2.0') // 版本标识
    localStorage.setItem('token_timestamp', timestamp.toString()) // 单独存储时间戳用于过期检查
    
    // 清理旧的存储
    localStorage.removeItem('encrypted_token')
    localStorage.removeItem('token')
    
  } catch (error) {
    console.error('Token存储失败:', error)
    // 降级到单层加密
    const encryptedToken = encrypt(token)
    localStorage.setItem('encrypted_token', encryptedToken)
    localStorage.setItem('token_timestamp', Date.now().toString())
  }
}

/**
 * 从localStorage安全获取Token
 * @returns Token字符串或null
 */
export function getSecureToken(): string | null {
  try {
    // 检查是否使用新版本存储
    const tokenVersion = localStorage.getItem('token_version')
    
    if (tokenVersion === '2.0') {
      const secureToken = localStorage.getItem('secure_auth_token')
      if (secureToken) {
        // 解析双重加密的Token
        const [encryptedData, salt] = atob(secureToken).split('::')
        
        if (encryptedData && salt) {
          // 第一层解密
          const decryptedData = CryptoJS.AES.decrypt(encryptedData, SECRET_KEY + salt).toString(CryptoJS.enc.Utf8)
          
          if (decryptedData) {
            const tokenData = JSON.parse(decryptedData)
            
            // 验证数据完整性
            const expectedChecksum = CryptoJS.SHA256(tokenData.token + tokenData.timestamp + tokenData.salt).toString()
            
            if (tokenData.checksum === expectedChecksum) {
              // 不检查token时间，因为后端不使用JWT
              return tokenData.token
            } else {
              console.error('Token数据完整性验证失败')
              clearSecureToken()
              return null
            }
          }
        }
      }
    }
    
    // 兼容旧版本存储
    const encryptedToken = localStorage.getItem('encrypted_token')
    if (encryptedToken) {
      const decryptedToken = decrypt(encryptedToken)
      if (decryptedToken) {
        return decryptedToken
      }
    }
    
    // 兼容明文存储（不安全）
    const plainToken = localStorage.getItem('token')
    if (plainToken) {
      return plainToken
    }
    
    return null
    
  } catch (error) {
    console.error('Token获取失败:', error)
    // 发生错误时清理所有存储
    clearSecureToken()
    return null
  }
}

/**
 * 清除存储的Token
 */
export function clearSecureToken(): void {
  localStorage.removeItem('secure_auth_token')
  localStorage.removeItem('token_version')
  localStorage.removeItem('token_timestamp')
  localStorage.removeItem('encrypted_token')
  localStorage.removeItem('token')
}

/**
 * 生成安全的会话ID
 * @returns 会话ID字符串
 */
export function generateSessionId(): string {
  return CryptoJS.lib.WordArray.random(16).toString()
}

/**
 * 验证Token是否过期
 * 注意：当前后端使用简单的token_urlsafe生成token，不是JWT格式
 * 为了安全性，对于非JWT token，基于存储时间进行过期检查
 * @param token Token
 * @returns 是否过期
 */
export function isTokenExpired(token: string): boolean {
  if (!token) {
    return true
  }
  
  // 检查token是否为JWT格式（包含两个点分隔符）
  if (token.includes('.') && token.split('.').length === 3) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      return payload.exp < currentTime
    } catch (error) {
      console.error('JWT Token验证失败:', error)
      return true
    }
  }
  
  // 对于非JWT token，检查存储时间戳进行过期验证
  try {
    const tokenVersion = localStorage.getItem('token_version')
    
    if (tokenVersion === '2.0') {
      const secureToken = localStorage.getItem('secure_auth_token')
      if (secureToken) {
        const [encryptedData, salt] = atob(secureToken).split('::')
        
        if (encryptedData && salt) {
          const decryptedData = CryptoJS.AES.decrypt(encryptedData, SECRET_KEY + salt).toString(CryptoJS.enc.Utf8)
          
          if (decryptedData) {
            const tokenData = JSON.parse(decryptedData)
            
            // 检查token存储时间，如果超过8小时则认为过期
            const now = Date.now()
            const tokenAge = now - tokenData.timestamp
            const maxAge = 8 * 60 * 60 * 1000 // 8小时
            
            if (tokenAge > maxAge) {
              console.log('Token已过期（超过8小时）')
              return true
            }
          }
        }
      }
    }
    
    // 对于旧版本或明文存储，检查localStorage的时间戳
    const tokenTimestamp = localStorage.getItem('token_timestamp')
    if (tokenTimestamp) {
      const timestamp = parseInt(tokenTimestamp)
      const now = Date.now()
      const tokenAge = now - timestamp
      const maxAge = 8 * 60 * 60 * 1000 // 8小时
      
      if (tokenAge > maxAge) {
        console.log('Token已过期（超过8小时）')
        return true
      }
    } else {
      // 没有时间戳记录，认为过期（为了安全）
      console.log('Token没有时间戳记录，认为过期')
      return true
    }
  } catch (error) {
    console.error('Token过期检查失败:', error)
    return true
  }
  
  return false
}

/**
 * 获取Token剩余有效时间（秒）
 * @param token Token
 * @returns 剩余秒数，-1表示已过期或无效
 */
export function getTokenRemainingTime(token: string): number {
  if (!token) {
    return -1
  }
  
  // 检查token是否为JWT格式
  if (token.includes('.') && token.split('.').length === 3) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      return Math.max(0, payload.exp - currentTime)
    } catch (error) {
      console.error('JWT Token时间解析失败:', error)
      return -1
    }
  }
  
  // 对于非JWT token，返回固定值（假设24小时有效）
  return 24 * 60 * 60 // 24小时
}