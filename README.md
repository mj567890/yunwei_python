# IT运维系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.0+-brightgreen.svg)](https://vuejs.org)
[![Flask](https://img.shields.io/badge/flask-2.0+-orange.svg)](https://flask.palletsprojects.com)

## 📋 项目简介

IT运维系统是一套基于Vue 3 + Flask的现代化企业级IT资产管理和网络运维平台。系统提供资产全生命周期管理、网络设备拓扑可视化、端口连接管理、故障处理等核心功能，帮助企业实现IT基础设施的智能化管理。

## ✨ 核心功能

### 📦 资产管理
- **全生命周期管理**: 从采购到报废的完整资产生命周期跟踪
- **智能分类**: 灵活的设备分类体系，支持自定义类别
- **保修管理**: 自动保修状态监控和到期提醒
- **批量操作**: 支持Excel批量导入导出
- **高级搜索**: 多维度筛选和快速定位

### 🌐 网络拓扑
- **可视化拓扑**: 直观的网络设备连接关系展示
- **设备管理**: 交换机、路由器、服务器等多类型设备支持
- **拖拽布局**: 支持手动调整设备位置和多种自动布局
- **实时状态**: 设备和连接状态的实时监控
- **搜索定位**: 快速查找和定位网络设备

### 🔌 端口管理
- **端口配置**: 灵活的端口添加和配置管理
- **连接管理**: 设备间端口连接的建立和维护
- **状态监控**: 端口使用状态和连接质量监控
- **快速配置**: 基于设备类型的端口模板快速创建
- **统计分析**: 端口利用率和连接统计

### 📊 统计报表
- **资产统计**: 设备数量、类别分布、状态统计
- **保修分析**: 保修状态分布和到期预警
- **网络统计**: 设备连接状态和端口利用率
- **可视化图表**: 直观的数据展示和趋势分析

## 🛠 技术架构

### 前端技术栈
- **Vue 3**: 现代化响应式前端框架
- **TypeScript**: 类型安全的JavaScript超集
- **Vite**: 快速的前端构建工具
- **Element Plus**: 优秀的Vue 3 UI组件库
- **Vue Router**: 官方路由管理
- **Pinia**: 轻量级状态管理

### 后端技术栈
- **Flask**: 轻量级Python Web框架
- **SQLite**: 轻量级嵌入式数据库
- **SQLAlchemy**: Python ORM框架
- **Flask-CORS**: 跨域请求处理
- **Gunicorn**: Python WSGI服务器

### 架构特点
- **前后端分离**: 清晰的架构边界和职责分工
- **RESTful API**: 标准化的API接口设计
- **响应式设计**: 支持多种屏幕尺寸和设备
- **模块化设计**: 可维护、可扩展的代码结构

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16.0+
- npm 8.0+

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/mj567890/yunwei_python.git
cd yunwei_python
```

2. **后端安装**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python sqlite_init.py
python setup_topology_categories.py
```

3. **前端安装**
```bash
cd frontend
npm install
```

4. **启动服务**
```bash
# 后端（终端1）
cd backend
python full_server.py

# 前端（终端2）
cd frontend
npm run dev
```

5. **访问系统**
- 前端地址: http://localhost:3000
- 后端地址: http://localhost:5000
- 默认账户: admin / admin123

## 📚 文档指南

- **[安装部署手册](INSTALLATION_GUIDE.md)**: 详细的系统安装和部署指南
- **[用户操作手册](USER_MANUAL.md)**: 完整的功能使用说明
- **[API文档](docs/API.md)**: 后端接口文档（开发中）
- **[开发指南](docs/DEVELOPMENT.md)**: 二次开发指南（开发中）

## 🎯 系统特色

### 🔧 灵活的设备分类
- 支持服务器、工作站等多种设备的网络拓扑显示
- 基于数据库配置的动态设备类别管理
- 可自定义设备图标和颜色

### 🌐 智能网络管理
- 支持混合网络环境的设备管理
- 端口级别的精细化连接管理
- 实时的网络状态监控和告警

### 📊 数据驱动决策
- 丰富的统计报表和数据分析
- 保修管理和成本控制
- 资产使用效率分析

### 🔒 企业级安全
- 用户权限管理和访问控制
- 数据备份和恢复机制
- 操作日志和审计跟踪

## 🗂 项目结构

```
yunwei_python/
├── backend/                 # 后端代码
│   ├── app/                # 应用模块
│   ├── config/             # 配置文件
│   ├── full_server.py      # 主服务文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── src/               # 源代码
│   │   ├── api/           # API接口
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   └── types/         # TypeScript类型
│   ├── package.json       # Node.js依赖
│   └── vite.config.ts     # Vite配置
├── docs/                  # 项目文档
├── INSTALLATION_GUIDE.md  # 安装指南
├── USER_MANUAL.md         # 用户手册
└── README.md              # 项目说明
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 开源协议

本项目采用 MIT 协议开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- **项目地址**: https://github.com/mj567890/yunwei_python
- **问题反馈**: 提交 [Issue](https://github.com/mj567890/yunwei_python/issues)
- **邮箱**: aremeng@gmail.com

## 🙏 致谢

感谢所有开源项目和社区的贡献，特别是：
- Vue.js 团队提供的优秀前端框架
- Flask 社区的轻量级后端解决方案
- Element Plus 提供的精美UI组件
- 所有参与项目开发和测试的贡献者

---

**版本**: v1.0.0  
**更新时间**: 2024年12月  
**维护者**: IT运维系统开发团队