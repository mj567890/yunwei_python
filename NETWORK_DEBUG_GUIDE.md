# "Failed to fetch" 错误诊断指南

## 🚨 当前问题
您访问 `http://127.0.0.1:3001/login` 仍然提示 "Failed to fetch"

## 🔍 立即诊断步骤

### 第1步：检查浏览器控制台
1. 在浏览器中按 `F12` 打开开发者工具
2. 切换到 **Console（控制台）** 标签
3. 尝试登录，查看具体错误信息
4. 切换到 **Network（网络）** 标签，查看请求详情

### 第2步：测试后端连接
访问这个链接测试后端是否工作：
- **后端健康检查**: http://localhost:5000/api/health
- **API测试页面**: http://localhost:3001/test.html

### 第3步：检查CORS预检请求
在Network标签中查找：
- **OPTIONS请求** - 如果失败，说明CORS配置问题
- **POST请求** - 如果失败，查看具体错误码

## 🛠️ 可能的解决方案

### 方案A：清除浏览器缓存
```bash
# 在浏览器中
1. 按 Ctrl+Shift+Delete
2. 选择"全部时间"
3. 清除缓存和数据
```

### 方案B：重启服务
```bash
# 后端服务（在 backend 目录）
Ctrl+C 停止
python simple_run.py

# 前端服务（在 frontend 目录）
Ctrl+C 停止  
npm run dev
```

### 方案C：检查hosts文件
确保没有DNS劫持：
```
127.0.0.1 localhost
```

### 方案D：使用localhost而不是127.0.0.1
尝试访问：`http://localhost:3001/login`

## 🔧 手动测试API连接

打开浏览器控制台，执行以下代码：

```javascript
fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
    })
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

## 📊 预期结果

### 成功的话应该看到：
```json
{
  "status": "success",
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "...",
    "user": {
      "username": "admin",
      "real_name": "系统管理员"
    }
  }
}
```

### 失败的话可能看到：
- `CORS policy` - CORS配置问题
- `net::ERR_CONNECTION_REFUSED` - 后端服务未启动
- `404 Not Found` - API路径错误
- `OPTIONS method not allowed` - 预检请求被拒绝

## 🎯 根据错误信息的对应解决方案

| 错误信息 | 解决方案 |
|---------|---------|
| CORS policy | 检查后端CORS配置 |
| Connection refused | 启动后端服务 |
| 404 Not Found | 检查API路径 |
| OPTIONS not allowed | 添加OPTIONS方法支持 |
| Network error | 检查防火墙/代理设置 |

## 🚀 快速修复命令

在项目根目录执行：

```bash
# 1. 重启后端
cd backend
python simple_run.py

# 2. 重启前端（新终端）
cd frontend  
npm run dev
```

然后访问：`http://localhost:3001/login`

---

如果以上步骤都无法解决问题，请提供：
1. 浏览器控制台的完整错误信息
2. Network标签中的请求详情
3. 使用的浏览器版本

这样我可以提供更精确的解决方案。