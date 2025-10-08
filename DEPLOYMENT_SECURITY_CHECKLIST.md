# IT运维系统 - 生产环境部署安全检查清单

## 🔐 安全配置检查

### 高优先级（必须完成）

#### 1. 环境变量配置 ✅
- [ ] **SECRET_KEY**: 生产环境密钥（至少32位随机字符）
- [ ] **JWT_SECRET_KEY**: JWT签名密钥（至少32位随机字符）
- [ ] **MYSQL_PASSWORD**: 数据库密码（强密码）
- [ ] **FLASK_ENV**: 设置为 `production`
- [ ] **ALLOWED_ORIGINS**: 配置允许的前端域名

```bash
# 环境变量设置示例
export SECRET_KEY="your-super-secret-production-key-32-chars-min"
export JWT_SECRET_KEY="your-jwt-secret-production-key-32-chars-min"
export MYSQL_PASSWORD="your-strong-database-password"
export FLASK_ENV="production"
export ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

#### 2. 数据库安全 ✅
- [ ] 数据库用户权限最小化
- [ ] 数据库密码复杂度符合要求
- [ ] 数据库备份策略已配置
- [ ] 数据库连接加密（SSL）

#### 3. API安全 ✅
- [ ] Flask-Limiter频率限制已启用
- [ ] 登录接口频率限制（5次/分钟）
- [ ] JWT令牌过期时间合理
- [ ] CORS配置限制为特定域名

#### 4. 文件上传安全 ✅
- [ ] 文件类型白名单验证
- [ ] 文件内容验证（MIME类型检查）
- [ ] 文件大小限制
- [ ] 上传目录权限配置

### 中优先级（建议完成）

#### 5. HTTPS配置
- [ ] SSL证书已安装
- [ ] 强制HTTPS重定向
- [ ] 安全头配置（HSTS, CSP等）

#### 6. 日志和监控
- [ ] 生产环境日志级别设置
- [ ] 敏感信息日志过滤
- [ ] 错误监控配置
- [ ] 性能监控配置

#### 7. 系统加固
- [ ] 防火墙规则配置
- [ ] 不必要服务禁用
- [ ] 系统更新和补丁

## 🧪 功能测试检查

### 核心功能测试
- [ ] 用户登录/登出
- [ ] 权限验证
- [ ] 资产管理CRUD
- [ ] 网络设备管理
- [ ] 维护记录管理
- [ ] 文件上传下载
- [ ] 统计报表生成

### 异常情况测试
- [ ] 无效登录凭据
- [ ] 权限不足访问
- [ ] 文件上传失败
- [ ] 数据库连接中断
- [ ] 网络超时处理

## 🚀 性能检查

### 数据库性能
- [ ] 索引优化
- [ ] 查询性能测试
- [ ] 连接池配置

### 前端性能
- [ ] 静态资源压缩
- [ ] 代码分割
- [ ] 缓存策略

### 服务器性能
- [ ] 内存使用监控
- [ ] CPU使用监控
- [ ] 磁盘空间监控

## 📋 部署步骤清单

### 1. 环境准备
```bash
# 1. 创建生产环境配置文件
cp .env.example .env.production

# 2. 编辑环境变量
nano .env.production

# 3. 安装依赖
pip install -r backend/requirements.txt
npm install --prefix frontend

# 4. 数据库初始化
flask db upgrade
python -c "from database.init_data import init_database; init_database()"
```

### 2. 安全配置
```bash
# 1. 设置文件权限
chmod 600 .env.production
chmod -R 755 backend/uploads
chmod -R 755 backend/logs

# 2. 创建必要目录
mkdir -p backend/logs
mkdir -p backend/uploads
mkdir -p backend/instance

# 3. 配置日志轮转
sudo logrotate -d /etc/logrotate.d/it-ops-system
```

### 3. 应用部署
```bash
# 1. 构建前端
npm run build --prefix frontend

# 2. 启动后端（使用gunicorn）
gunicorn -c gunicorn.conf.py app:app

# 3. 配置Nginx（可选）
sudo cp nginx.conf /etc/nginx/sites-available/it-ops-system
sudo ln -s /etc/nginx/sites-available/it-ops-system /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 4. 验证部署
```bash
# 1. 运行健康检查
python health_check.py

# 2. 检查服务状态
systemctl status it-ops-system
systemctl status nginx

# 3. 检查日志
tail -f backend/logs/it_ops_system.log
```

## 🔍 安全漏洞检查

### 已修复的安全问题 ✅
1. **默认密钥风险**: 生产环境强制环境变量
2. **Token存储风险**: 前端加密存储
3. **API频率限制**: Flask-Limiter集成
4. **文件上传安全**: 内容验证和清理
5. **CORS配置**: 环境变量控制

### 需要持续关注的安全点
1. **依赖更新**: 定期更新第三方库
2. **日志监控**: 异常行为检测
3. **备份验证**: 定期验证备份完整性
4. **权限审计**: 定期检查用户权限

## 📊 性能基准

### 预期性能指标
- **API响应时间**: < 200ms
- **页面加载时间**: < 2s
- **并发用户数**: 100+
- **数据库查询时间**: < 100ms

### 性能测试命令
```bash
# API性能测试
ab -n 1000 -c 10 http://localhost:5000/api/assets

# 前端性能测试
lighthouse http://localhost:5173 --output=html

# 数据库性能测试
mysqlslap --delimiter=";" --create-schema=it_ops_system --query="SELECT * FROM assets LIMIT 100;" --concurrency=10 --iterations=100
```

## 🚨 应急预案

### 服务故障处理
1. **数据库连接失败**: 检查连接配置和服务状态
2. **内存不足**: 重启服务或扩容
3. **磁盘空间满**: 清理日志和临时文件
4. **安全事件**: 立即禁用受影响账户，检查日志

### 回滚计划
1. **代码回滚**: 使用Git回滚到上一个稳定版本
2. **数据库回滚**: 使用最近的备份恢复
3. **配置回滚**: 恢复之前的配置文件

## ✅ 最终检查

在正式部署前，请确认：
- [ ] 所有高优先级安全检查已完成
- [ ] 核心功能测试通过
- [ ] 性能指标达到预期
- [ ] 监控和日志系统正常
- [ ] 备份策略已实施
- [ ] 应急预案已准备

---

**部署负责人**: _________________  
**安全审核人**: _________________  
**部署日期**: _________________  
**版本号**: _________________