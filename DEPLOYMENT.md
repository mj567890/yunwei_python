# IT运维综合管理系统 - 部署指南

## 概述

本文档详细介绍了IT运维综合管理系统的多种部署方式和配置要求，包括传统部署、Docker容器化部署和systemd服务管理。

## 系统要求

### 服务器要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+) 或 Windows Server 2019+
- **CPU**: 4核心或以上
- **内存**: 8GB RAM 或以上
- **硬盘**: 100GB 可用空间或以上
- **网络**: 10Mbps 带宽或以上

### 软件依赖
- **Python**: 3.9+ 
- **Node.js**: 18.0+ 
- **MySQL**: 8.0+
- **Redis**: 6.0+ (可选，用于缓存)
- **Nginx**: 1.18+ (生产环境推荐)

## 部署方式选择

系统支持多种部署方式，请根据您的需求选择：

1. **Docker部署** (推荐) - 适合快速部署和开发环境
2. **传统部署** - 适合生产环境和高定制化需求
3. **systemd服务** - 适合Linux生产环境的系统级管理

## 部署步骤

### 方式一：Docker部署 (推荐)

Docker部署是最简单的部署方式，一键启动完整的服务栈。

#### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM 或以上
- 50GB 可用磁盘空间

#### 部署步骤

1. **准备环境配置**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（重要！）
nano .env
```

2. **配置环境变量**
```env
# 必须配置的环境变量
SECRET_KEY=your-super-secret-production-key-32-chars-minimum
JWT_SECRET_KEY=your-jwt-secret-production-key-32-chars-minimum
MYSQL_PASSWORD=your-strong-database-password
MYSQL_DATABASE=it_ops_system
FLASK_ENV=production
```

3. **启动服务栈**
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

4. **访问应用**
- 前端地址: http://localhost:80
- 后端API: http://localhost:5000/api
- 数据库: localhost:3306
- Redis: localhost:6379

#### Docker管理命令
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec app bash

# 数据备份
docker-compose exec mysql mysqldump -u root -p it_ops_system > backup.sql
```

---

### 方式二：传统部署

### 2. 后端部署

#### 安装Python和依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv

# CentOS/RHEL
sudo yum install python39 python39-pip
```

#### 安装Node.js
```bash
# 使用官方安装脚本
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 安装MySQL
```bash
# Ubuntu/Debian
sudo apt install mysql-server-8.0

# 初始化MySQL
sudo mysql_secure_installation
```

### 2. 后端部署

#### 创建Python虚拟环境
```bash
cd /opt/itops
python3.9 -m venv venv
source venv/bin/activate
```

#### 安装Python依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 配置数据库
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE it_ops_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'itops'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON it_ops_system.* TO 'itops'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 初始化数据库
mysql -u itops -p it_ops_system < ../database/init.sql
```

#### 配置环境变量
```bash
# 创建.env文件
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=itops
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=it_ops_system
REDIS_URL=redis://localhost:6379/0
EOF
```

#### 运行数据库迁移
```bash
flask db upgrade
```

#### 启动后端服务
```bash
# 使用Gunicorn
gunicorn -c gunicorn.conf.py run:app
```

### 3. 前端部署

#### 安装依赖
```bash
cd frontend
npm install
```

#### 构建生产版本
```bash
npm run build
```

#### 配置Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /opt/itops/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API接口代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 文件上传大小限制
    client_max_body_size 50M;
}
```

### 4. 服务配置

#### 创建systemd服务文件
```bash
# 后端服务
sudo cat > /etc/systemd/system/itops-backend.service << EOF
[Unit]
Description=IT Operations Management System Backend
After=network.target

[Service]
Type=exec
User=itops
Group=itops
WorkingDirectory=/opt/itops/backend
Environment=PATH=/opt/itops/venv/bin
ExecStart=/opt/itops/venv/bin/gunicorn -c gunicorn.conf.py run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable itops-backend
sudo systemctl start itops-backend
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

### 方式三：systemd服务部署

使用systemd管理服务，适合Linux生产环境。

#### 部署步骤

1. **复制服务配置文件**
```bash
# 复制systemd服务文件
sudo cp it-ops-system.service /etc/systemd/system/

# 重载配置
sudo systemctl daemon-reload
```

2. **配置服务**
```bash
# 启用服务
sudo systemctl enable it-ops-system

# 启动服务
sudo systemctl start it-ops-system

# 查看服务状态
sudo systemctl status it-ops-system
```

3. **配置Nginx反向代理**
```bash
# 复制Nginx配置
sudo cp nginx.conf /etc/nginx/sites-available/it-ops-system

# 启用配置
sudo ln -s /etc/nginx/sites-available/it-ops-system /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

4. **服务管理命令**
```bash
# 查看服务状态
sudo systemctl status it-ops-system

# 重启服务
sudo systemctl restart it-ops-system

# 停止服务
sudo systemctl stop it-ops-system

# 查看日志
sudo journalctl -u it-ops-system -f
```

---

## 配置文件说明

系统包含多个配置文件，支持不同的部署环境和需求。

### 环境变量配置

#### 后端环境变量 (`.env`)
基于 `.env.example` 模板创建，包含所有必要的配置项。

#### 前端环境变量
- `frontend/.env.development` - 开发环境配置
- `frontend/.env.production` - 生产环境配置

### 服务器配置

#### Gunicorn配置 (`gunicorn.conf.py`)
包含完整的WSGI服务器配置：
- 多进程配置
- 日志配置
- 性能优化
- 开发/生产环境适配
```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
```

### Nginx优化配置
项目包含完整的 `nginx.conf` 配置文件，包括：

```nginx
# gzip压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# 缓存设置
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# HTTPS和安全头配置
# SSL协议配置
# 文件上传优化
# 健康检查支持
```

### systemd服务配置
项目包含 `it-ops-system.service` 文件，支持：
- 自动重启机制
- 资源限制和安全配置
- 环境变量管理
- 日志和监控集成

## 监控和日志

### 日志配置
```bash
# 创建日志目录
sudo mkdir -p /var/log/itops
sudo chown itops:itops /var/log/itops

# 配置logrotate
sudo cat > /etc/logrotate.d/itops << EOF
/var/log/itops/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 itops itops
}
EOF
```

### 系统监控
建议使用以下工具进行系统监控：
- **Prometheus** + **Grafana**: 系统指标监控
- **ELK Stack**: 日志分析
- **Supervisor**: 进程管理

## 备份策略

### 数据库备份
```bash
# 创建备份脚本
cat > /opt/itops/backup.sh << EOF
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u itops -p it_ops_system > /opt/itops/backups/db_backup_$DATE.sql
find /opt/itops/backups -name "db_backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/itops/backup.sh

# 添加到crontab
crontab -e
0 2 * * * /opt/itops/backup.sh
```

## 安全建议

1. **防火墙配置**
```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

2. **SSL证书配置**
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

3. **数据库安全**
- 定期更新密码
- 限制数据库访问IP
- 启用SSL连接

## 故障排除

### 常见问题

1. **端口占用**
```bash
netstat -tulpn | grep :5000
```

2. **权限问题**
```bash
sudo chown -R itops:itops /opt/itops
```

3. **数据库连接失败**
```bash
mysql -u itops -p -h localhost
```

### 日志查看
```bash
# 后端日志 (systemd服务)
sudo journalctl -u it-ops-system -f

# 应用日志
tail -f /var/log/it-ops/gunicorn_error.log

# Nginx日志
sudo tail -f /var/log/nginx/it-ops-access.log
sudo tail -f /var/log/nginx/it-ops-error.log

# Docker日志
docker-compose logs -f app
```

## 性能优化

### 数据库优化
```sql
-- 添加索引
ALTER TABLE it_asset ADD INDEX idx_status (status);
ALTER TABLE maintenance_record ADD INDEX idx_created_at (created_at);
```

### Redis缓存
```python
# 配置Redis缓存
CACHE_TYPE = "redis"
CACHE_REDIS_URL = "redis://localhost:6379/1"
```

## 更新升级

### Docker环境更新
```bash
# 更新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 传统部署更新

#### 后端更新
```bash
cd /opt/itops/backend
source ../venv/bin/activate
git pull origin main
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart it-ops-system
```

#### 前端更新
```bash
cd /opt/itops/frontend
git pull origin main
npm install
npm run build
sudo systemctl reload nginx
```

## 联系支持

如需技术支持，请联系：
- 邮箱: support@itops.com
- 文档: https://docs.itops.com
- GitHub: https://github.com/itops/system