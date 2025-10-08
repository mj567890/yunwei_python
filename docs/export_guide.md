# 资产导出功能使用说明

## 功能概述

IT运维系统提供了完整的资产导出功能，支持Excel和CSV格式导出，可以根据搜索条件灵活导出所需的资产数据。

## 主要特性

### 1. 后端导出API
- **路径**: `/api/assets/export`
- **方法**: GET
- **支持格式**: Excel (.xlsx) 和 CSV (.csv)
- **搜索过滤**: 支持与列表页面相同的搜索条件

### 2. 前端导出界面
- 导出对话框提供友好的用户界面
- 支持选择导出范围（当前搜索结果/全部数据）
- 支持选择导出格式（Excel/CSV）
- 实时显示导出状态

### 3. 本地导出工具
- 前端本地导出功能（使用xlsx和file-saver）
- 支持自定义导出字段和表头
- 提供多种预设导出配置
- 数据格式化和本地化处理

## 使用方式

### 方式一：通过Web界面导出

1. 访问资产列表页面 (http://127.0.0.1:3000/app/assets/list)
2. 设置搜索条件（可选）
3. 点击 "📄 导出资产" 按钮
4. 在导出对话框中：
   - 选择导出范围
   - 选择导出格式
   - 点击 "确认导出"
5. 文件将自动下载到您的设备

### 方式二：直接调用API

```bash
# 导出全部资产
curl "http://localhost:5000/api/assets/export" -o assets.xlsx

# 按条件导出
curl "http://localhost:5000/api/assets/export?name=Dell&status=在用" -o dell_assets.xlsx

# 下载导入模板
curl "http://localhost:5000/api/assets/import-template" -o template.xlsx
```

### 方式三：在代码中使用导出工具

```typescript
import { exportAssets, exportWithPreset, EXPORT_PRESETS } from '@/utils/assetExport'

// 基本导出
exportAssets(assetList, {
  format: 'excel',
  filename: '资产列表_2024-01-01'
})

// 使用预设配置导出
exportWithPreset(assetList, 'basic', 'excel', '基本资产信息')

// 自定义字段导出
exportAssets(assetList, {
  format: 'csv',
  includeFields: ['asset_code', 'name', 'status'],
  customHeaders: {
    asset_code: '编码',
    name: '名称', 
    status: '状态'
  }
})
```

## 导出字段说明

### 默认导出字段
- **资产编码**: 唯一标识资产的编码
- **资产名称**: 资产的名称
- **品牌**: 资产品牌
- **型号**: 资产型号
- **类别**: 资产分类
- **状态**: 资产当前状态（在用/闲置/维修/报废）
- **使用人**: 当前使用人员
- **使用部门**: 所属部门
- **位置**: 资产放置位置
- **保修状态**: 保修状态（保修中/已过保/即将到期）
- **保修剩余天数**: 保修期剩余天数
- **创建时间**: 资产录入时间

### 预设导出配置

1. **基本信息** (basic): 资产编码、名称、品牌、型号、类别、状态
2. **完整信息** (full): 包含所有字段
3. **保修信息** (warranty): 资产编码、名称、保修状态、剩余天数
4. **使用情况** (usage): 资产编码、名称、使用人、部门、位置、状态

## 技术实现

### 后端实现
- 使用Flask框架提供RESTful API
- 支持pandas和openpyxl生成Excel文件
- 当依赖库不可用时自动降级为CSV格式
- 支持中文字符编码（UTF-8 with BOM）

### 前端实现
- Vue 3 + TypeScript
- 使用xlsx和file-saver库进行本地导出
- 响应式UI设计，支持移动端
- 完整的错误处理和用户反馈

## 注意事项

1. **文件大小限制**: 大量数据导出时请注意文件大小和浏览器下载限制
2. **中文支持**: CSV格式已添加BOM头支持中文显示
3. **搜索条件**: 导出会应用当前页面的搜索条件
4. **权限控制**: 确保用户具有资产查看权限
5. **浏览器兼容**: 建议使用现代浏览器（Chrome、Firefox、Edge等）

## 故障排除

### 常见问题

1. **导出文件为空**
   - 检查搜索条件是否过于严格
   - 确认数据库中有匹配的资产记录

2. **中文显示乱码**
   - CSV文件请用Excel打开或选择UTF-8编码
   - Excel文件不会有编码问题

3. **导出失败**
   - 检查网络连接
   - 确认后端服务正常运行
   - 查看浏览器控制台错误信息

4. **文件无法下载**
   - 检查浏览器下载设置
   - 确认没有被弹窗拦截器阻止

### 开发调试

查看后端日志获取详细错误信息：
```bash
# 在后端目录运行
python full_server.py
# 观察控制台输出的请求和响应日志
```

前端调试：
```javascript
// 打开浏览器开发者工具，在控制台查看
console.log('导出参数:', searchParams)
```

## 更新日志

- **v1.0.0**: 基础导出功能，支持Excel和CSV格式
- **v1.1.0**: 添加导出对话框和格式选择
- **v1.2.0**: 增加预设导出配置和本地导出工具
- **v1.3.0**: 优化中文支持和错误处理