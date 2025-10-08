# IT运维系统 - 安装部署手册

## 📋 系统概述

IT运维系统是一套基于Vue 3 + Flask的现代化企业资产管理和网络拓扑管理平台，支持资产全生命周期管理、网络设备拓扑可视化、端口连接管理等功能。

## 🔧 系统要求

### 服务器要求
- **操作系统**: Windows 10/11, Windows Server 2016+, Ubuntu 18.04+, CentOS 7+
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 10GB 可用空间
- **网络**: 支持HTTP/HTTPS访问

### 软件依赖
- **Python**: 3.8+ (推荐 3.9+)
- **Node.js**: 16.0+ (推荐 18.0+)
- **npm**: 8.0+
- **Git**: 2.20+ (可选，用于代码管理)

## 📦 安装步骤

### 1. 获取源码

#### 方式一：Git克隆（推荐）
```bash
git clone https://github.com/mj567890/yunwei_python.git
cd yunwei_python
```

#### 方式二：下载压缩包
1. 下载项目压缩包
2. 解压到目标目录
3. 进入项目根目录

### 2. 后端安装

#### 2.1 创建Python虚拟环境
```bash
# Windows
cd backend
python -m venv venv
venv\Scripts\activate

# Linux/macOS
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 安装Python依赖
```bash
pip install -r requirements.txt
```

#### 2.3 初始化数据库
```bash
# 执行数据库初始化
python sqlite_init.py

# 配置资产类别（支持拓扑显示）
python setup_topology_categories.py
```

#### 2.4 配置环境变量
创建 `.env` 文件：
```bash
# 数据库配置
DATABASE_URL=sqlite:///it_ops_system.db

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# 服务配置
FLASK_ENV=development
DEBUG=True

# CORS配置
CORS_ORIGINS=http://localhost:3000
```

### 3. 前端安装

#### 3.1 安装Node.js依赖
```bash
cd frontend
npm install
```

#### 3.2 配置环境变量
创建 `.env.development` 文件：
```bash
# API配置
VITE_API_BASE_URL=http://localhost:5000/api
VITE_BASE_URL=http://localhost:5000

# 应用配置
VITE_APP_TITLE=IT运维系统
VITE_APP_VERSION=1.0.0
```

创建 `.env.production` 文件：
```bash
# 生产环境API配置
VITE_API_BASE_URL=http://your-domain.com:5000/api
VITE_BASE_URL=http://your-domain.com:5000

# 应用配置
VITE_APP_TITLE=IT运维系统
VITE_APP_VERSION=1.0.0
```

## 🚀 启动服务

### 开发环境启动

#### 1. 启动后端服务
```bash
cd backend
# 激活虚拟环境（如果未激活）
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 启动服务（必须使用5000端口）
python full_server.py
```

后端服务将在 `http://localhost:5000` 启动

#### 2. 启动前端服务
```bash
cd frontend
# 启动开发服务器（必须使用3000端口）
npm run dev
```

前端服务将在 `http://localhost:3000` 启动

### 生产环境部署

#### 1. 前端构建
```bash
cd frontend
npm run build
```

构建产物在 `dist/` 目录下

#### 2. 后端生产配置
创建 `gunicorn.conf.py` 配置文件：
```python
# Gunicorn配置
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 3. 使用Gunicorn启动
```bash
cd backend
gunicorn -c gunicorn.conf.py full_server:app
```

#### 4. Nginx代理配置（可选）
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔐 安全配置

### 1. 数据库安全
- 定期备份数据库文件
- 设置适当的文件权限
- 考虑数据加密存储

### 2. 网络安全
- 配置防火墙规则
- 使用HTTPS协议
- 限制API访问频率

### 3. 访问控制
- 修改默认管理员密码
- 设置强密码策略
- 定期更新系统密钥

## ⚙️ 系统配置

### 1. 默认账户
- **用户名**: admin
- **密码**: admin123
- **注意**: 首次登录后请立即修改密码

### 2. 端口配置
- **前端端口**: 3000 （不可更改）
- **后端端口**: 5000 （不可更改）
- **数据库**: SQLite本地文件

### 3. 功能模块
- ✅ 资产管理
- ✅ 网络拓扑
- ✅ 端口管理
- ✅ 故障管理
- ✅ 维护管理
- ✅ 统计报表

## 🔧 故障排除

### 常见问题

#### 1. 端口占用
```bash
# 检查端口占用
netstat -ano | findstr :5000  # Windows
netstat -tulpn | grep :5000   # Linux

# 停止占用进程
taskkill /PID <PID> /F         # Windows
kill -9 <PID>                  # Linux
```

#### 2. Python依赖问题
```bash
# 清理并重新安装
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### 3. 前端构建失败
```bash
# 清理缓存并重新安装
rm -rf node_modules package-lock.json
npm install
```

#### 4. 数据库初始化失败
```bash
# 删除现有数据库重新初始化
rm it_ops_system.db
python sqlite_init.py
python setup_topology_categories.py
```

### 日志查看

#### 后端日志
- 控制台输出：实时查看运行状态
- 错误日志：检查Python错误和异常

#### 前端日志
- 浏览器控制台：F12开发者工具
- 网络请求：查看API调用状态

## 📊 性能优化

### 1. 数据库优化
- 定期清理过期数据
- 建立适当的索引
- 监控数据库大小

### 2. 前端优化
- 启用Gzip压缩
- 配置CDN加速
- 优化图片资源

### 3. 后端优化
- 增加Worker进程
- 配置缓存策略
- 监控内存使用

## 🔄 系统维护

### 1. 定期备份
```bash
# 数据库备份
cp backend/it_ops_system.db backup/it_ops_system_$(date +%Y%m%d).db

# 完整系统备份
tar -czf it_ops_backup_$(date +%Y%m%d).tar.gz yunwei_python/
```

### 2. 系统更新
```bash
# 更新代码
git pull origin main

# 更新依赖
cd backend && pip install -r requirements.txt
cd frontend && npm install

# 重启服务
```

### 3. 监控检查
- 服务运行状态
- 磁盘空间使用
- 内存使用情况
- API响应时间

## 📞 技术支持

如遇到安装部署问题，请提供以下信息：
- 操作系统版本
- Python/Node.js版本
- 错误信息截图
- 系统日志内容

---

**版本**: v1.0.0  
**更新时间**: 2024年12月  
**维护者**: IT运维系统开发团队