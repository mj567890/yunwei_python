# IT运维综合管理系统

一个基于Python Flask + Vue 3的现代化企业级运维管理平台，集成资产管理、网络设备管理、故障分析、运维记录和统计分析等核心功能。

## ✨ 功能特性

### 🏢 资产管理
- **全生命周期管理**: 从采购到报废的完整资产生命周期跟踪
- **三级联动位置**: 楼宇-楼层-房间的层级位置管理
- **保修预警**: 自动提醒保修到期的资产设备
- **移动端支持**: 支持移动设备扫码录入和查看
- **批量导入导出**: Excel批量导入导出功能
- **二维码标签**: 自动生成资产二维码标签

### 🌐 网络设备管理
- **设备拓扑图**: 可视化网络拓扑结构
- **端口关系管理**: 设备端口连接关系管理
- **实时状态监控**: 网络设备运行状态实时监控
- **配置备份**: 网络设备配置自动备份
- **性能监控**: CPU、内存、带宽等性能指标监控

### 🔧 故障分析
- **智能分析**: AI辅助故障原因分析
- **影响评估**: 故障影响范围和严重程度评估
- **处理建议**: 基于历史数据的处理建议
- **工单流转**: 完整的故障处理工单流程
- **SLA管理**: 故障处理时效管理

### 📝 运维记录
- **全生命周期**: 从计划到完成的完整记录
- **附件管理**: 支持图片、文档等附件上传
- **状态跟踪**: 实时跟踪运维任务执行状态
- **成本统计**: 运维成本统计和分析
- **模板管理**: 常用运维任务模板

### 📊 统计分析
- **多维度统计**: 按时间、类型、位置等多维度统计
- **可视化图表**: 丰富的图表展示
- **趋势分析**: 历史趋势和预测分析
- **报表导出**: 支持Excel、PDF格式报表导出
- **实时仪表盘**: 关键指标实时展示

### 👥 权限管理
- **RBAC模型**: 基于角色的访问控制
- **JWT认证**: 安全的token认证机制
- **操作审计**: 完整的用户操作日志
- **多级权限**: 细粒度的功能权限控制

## 🛠 技术栈

### 后端技术
- **框架**: Flask 2.3.3 + SQLAlchemy 3.0.5
- **数据库**: MySQL 8.0
- **认证**: JWT (Flask-JWT-Extended 4.5.3)
- **API限流**: Flask-Limiter 3.5.0
- **序列化**: Marshmallow 3.20.1
- **跨域**: Flask-CORS 4.0.0
- **文件类型检测**: python-magic 0.4.27
- **任务队列**: Celery + Redis
- **文件处理**: Pillow, openpyxl, qrcode
- **生产服务器**: Gunicorn 21.2.0

### 前端技术
- **框架**: Vue 3.3.8 + TypeScript
- **构建工具**: Vite 4.5.0
- **UI组件**: Element Plus 2.4.4
- **状态管理**: Pinia 2.1.7
- **路由管理**: Vue Router 4.2.5
- **图表库**: ECharts 5.4.3
- **网络拓扑**: D3.js 7.8.5
- **加密工具**: crypto-js 4.2.0
- **工具库**: @vueuse/core, dayjs, axios

### 开发工具
- **代码质量**: ESLint + Prettier
- **测试框架**: Pytest (后端) + Vitest (前端)
- **API文档**: 内置Swagger文档
- **版本控制**: Git

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 18.0+
- MySQL 8.0+
- Redis 6.0+ (可选)

### 项目结构
```
yuwei_python/
├── backend/                 # 后端代码
│   ├── app/                 # 应用代码
│   ├── config/              # 配置文件
│   ├── requirements.txt     # Python依赖
│   └── run.py              # 应用入口
├── frontend/               # 前端代码
│   ├── src/                 # 源代码
│   ├── package.json         # Node.js依赖
│   └── vite.config.ts       # Vite配置
├── database/               # 数据库脚本
├── .env.example            # 环境变量模板
├── gunicorn.conf.py        # Gunicorn配置
├── nginx.conf              # Nginx配置
├── docker-compose.yml      # Docker编排
├── Dockerfile              # Docker构建
└── it-ops-system.service   # systemd服务
```

### 后端启动
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/yuwei_python.git
cd yuwei_python

# 2. 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据库
# 创建MySQL数据库并导入init.sql
mysql -u root -p
CREATE DATABASE it_ops_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE it_ops_system;
source ../database/init.sql

# 5. 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库连接等信息

# 6. 运行应用
python run.py
```

### 前端启动
```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev
```

### 访问应用
- 前端地址: http://localhost:3001 (开发环境)
- 后端API: http://localhost:5000/api
- 默认账号: admin / admin123
- 健康检查: http://localhost:5000/health

## 📱 移动端支持

系统完全支持移动端访问，提供：
- 响应式设计，适配各种屏幕尺寸
- 移动端专用导航和操作界面
- 触控手势支持
- 二维码扫描功能
- 离线数据缓存

## 🔧 配置说明

### 环境变量配置
```env
# Flask应用配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-32-chars-minimum
JWT_SECRET_KEY=your-jwt-secret-key-32-chars-minimum

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=it_ops_system

# Redis配置 (可选)
REDIS_URL=redis://localhost:6379/0

# CORS配置
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800  # 50MB
```

## 🧪 测试

### 后端测试
```bash
cd backend
pytest tests/ -v
```

### 前端测试
```bash
cd frontend
npm run test
```

### 性能测试
```bash
# 后端性能测试
pytest tests/test_performance.py -v
```

## 📦 部署

详细的生产环境部署指南请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### Docker部署 (推荐)
```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件设置密钥和数据库密码

# 2. 启动完整服务栈
docker-compose up -d

# 3. 访问应用
# 前端: http://localhost:80
# 后端API: http://localhost:5000/api
```

### 传统部署
```bash
# 1. 安装依赖
pip install -r backend/requirements.txt
npm install --prefix frontend

# 2. 构建前端
npm run build --prefix frontend

# 3. 配置环境变量
cp .env.example .env
# 编辑环境变量

# 4. 启动服务
gunicorn -c gunicorn.conf.py backend.run:app
```

### systemd服务部署
```bash
# 1. 复制服务配置
sudo cp it-ops-system.service /etc/systemd/system/

# 2. 启用并启动服务
sudo systemctl enable it-ops-system
sudo systemctl start it-ops-system

# 3. 配置Nginx
sudo cp nginx.conf /etc/nginx/sites-available/it-ops-system
sudo ln -s /etc/nginx/sites-available/it-ops-system /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## 📸 系统截图

### 仪表板
![Dashboard](docs/images/dashboard.png)

### 资产管理
![Assets](docs/images/assets.png)

### 网络拓扑
![Network](docs/images/topology.png)

### 移动端界面
![Mobile](docs/images/mobile.png)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📋 更新日志

### v1.0.0 (2024-01-15)
- ✨ 完整的资产管理功能
- 🌐 网络设备管理和拓扑可视化
- 🔧 故障分析和处理系统
- 📝 运维记录管理
- 📊 统计分析和报表
- 📱 移动端响应式支持
- 👥 完整的权限管理系统

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 联系我们

- 项目主页: https://github.com/your-repo/yuwei_python
- 问题反馈: https://github.com/your-repo/yuwei_python/issues
- 邮箱: support@itops.com

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

**⭐ 如果这个项目对你有帮助，请给它一个星标！**