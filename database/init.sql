-- IT运维综合管理系统数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS it_ops_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE it_ops_system;

-- 创建系统管理员用户
-- 密码: admin123
INSERT INTO sys_user (username, password_hash, email, real_name, status, created_at, updated_at) 
VALUES ('admin', 'pbkdf2:sha256:600000$FRQjJpFYLiLGLb2r$afc9d71b20c5a7b3c6f62b5bd9e32e1a8b5c5b8e7b0f3c9e8b5e7b8f8c5b5e8b', 'admin@itops.com', '系统管理员', 1, NOW(), NOW());

-- 创建角色
INSERT INTO sys_role (name, code, description, status, created_at, updated_at) VALUES
('系统管理员', 'ADMIN', '系统管理员，拥有所有权限', 1, NOW(), NOW()),
('运维员', 'OPERATOR', '运维人员，拥有操作权限', 1, NOW(), NOW()),
('查看员', 'VIEWER', '查看人员，只读权限', 1, NOW(), NOW());

-- 创建权限
INSERT INTO sys_permission (name, code, description, resource, action, created_at, updated_at) VALUES
-- 用户管理权限
('查看用户', 'user:view', '查看用户信息', 'user', 'view', NOW(), NOW()),
('创建用户', 'user:create', '创建新用户', 'user', 'create', NOW(), NOW()),
('编辑用户', 'user:edit', '编辑用户信息', 'user', 'edit', NOW(), NOW()),
('删除用户', 'user:delete', '删除用户', 'user', 'delete', NOW(), NOW()),

-- 角色权限管理
('查看角色', 'role:view', '查看角色信息', 'role', 'view', NOW(), NOW()),
('管理角色', 'role:manage', '管理角色权限', 'role', 'manage', NOW(), NOW()),

-- 资产管理权限
('查看资产', 'asset:view', '查看资产信息', 'asset', 'view', NOW(), NOW()),
('创建资产', 'asset:create', '创建新资产', 'asset', 'create', NOW(), NOW()),
('编辑资产', 'asset:edit', '编辑资产信息', 'asset', 'edit', NOW(), NOW()),
('删除资产', 'asset:delete', '删除资产', 'asset', 'delete', NOW(), NOW()),
('导入导出资产', 'asset:import_export', '导入导出资产数据', 'asset', 'import_export', NOW(), NOW()),

-- 网络设备权限
('查看设备', 'device:view', '查看网络设备', 'device', 'view', NOW(), NOW()),
('管理设备', 'device:manage', '管理网络设备', 'device', 'manage', NOW(), NOW()),
('查看拓扑', 'topology:view', '查看网络拓扑', 'topology', 'view', NOW(), NOW()),
('编辑拓扑', 'topology:edit', '编辑网络拓扑', 'topology', 'edit', NOW(), NOW()),

-- 运维记录权限
('查看运维记录', 'maintenance:view', '查看运维记录', 'maintenance', 'view', NOW(), NOW()),
('创建运维记录', 'maintenance:create', '创建运维记录', 'maintenance', 'create', NOW(), NOW()),
('编辑运维记录', 'maintenance:edit', '编辑运维记录', 'maintenance', 'edit', NOW(), NOW()),
('删除运维记录', 'maintenance:delete', '删除运维记录', 'maintenance', 'delete', NOW(), NOW()),

-- 故障管理权限
('查看故障', 'fault:view', '查看故障记录', 'fault', 'view', NOW(), NOW()),
('处理故障', 'fault:handle', '处理故障', 'fault', 'handle', NOW(), NOW()),

-- 统计分析权限
('查看统计', 'statistics:view', '查看统计数据', 'statistics', 'view', NOW(), NOW()),

-- 系统管理权限
('系统配置', 'system:config', '系统配置管理', 'system', 'config', NOW(), NOW()),
('操作日志', 'log:view', '查看操作日志', 'log', 'view', NOW(), NOW());

-- 为系统管理员分配所有权限
INSERT INTO role_permissions (role_id, permission_id, created_at)
SELECT 1, id, NOW() FROM sys_permission;

-- 为运维员分配操作权限
INSERT INTO role_permissions (role_id, permission_id, created_at)
SELECT 2, id, NOW() FROM sys_permission 
WHERE code NOT IN ('user:create', 'user:delete', 'role:manage', 'system:config');

-- 为查看员分配查看权限
INSERT INTO role_permissions (role_id, permission_id, created_at)
SELECT 3, id, NOW() FROM sys_permission 
WHERE code LIKE '%:view';

-- 为管理员用户分配角色
INSERT INTO user_roles (user_id, role_id, created_at) VALUES (1, 1, NOW());

-- 创建默认楼宇数据
INSERT INTO building_info (name, code, address, description, status, created_at, updated_at) VALUES
('总部大楼', 'HQ001', '北京市朝阳区XX路1号', '公司总部办公大楼', 1, NOW(), NOW()),
('研发中心', 'RD001', '北京市海淀区XX路2号', '研发中心大楼', 1, NOW(), NOW());

-- 创建楼层数据
INSERT INTO floor_info (building_id, name, code, floor_number, description, status, created_at, updated_at) VALUES
(1, '1层', 'F01', 1, '大厅和接待区', 1, NOW(), NOW()),
(1, '2层', 'F02', 2, '办公区域', 1, NOW(), NOW()),
(1, '3层', 'F03', 3, '会议室和培训室', 1, NOW(), NOW()),
(1, '4层', 'F04', 4, '技术部门', 1, NOW(), NOW()),
(2, '1层', 'F01', 1, '服务器机房', 1, NOW(), NOW()),
(2, '2层', 'F02', 2, '研发办公区', 1, NOW(), NOW());

-- 创建房间数据
INSERT INTO room_info (floor_id, name, code, room_type, area, capacity, description, status, created_at, updated_at) VALUES
(1, '大厅', 'R001', '公共区域', 200.00, 100, '主大厅', 1, NOW(), NOW()),
(2, '办公室201', 'R201', '办公室', 50.00, 10, '普通办公室', 1, NOW(), NOW()),
(2, '办公室202', 'R202', '办公室', 50.00, 10, '普通办公室', 1, NOW(), NOW()),
(4, '机房401', 'R401', '机房', 80.00, 5, '小型机房', 1, NOW(), NOW()),
(5, '主机房', 'R101', '机房', 300.00, 10, '主要服务器机房', 1, NOW(), NOW()),
(6, '研发部', 'R201', '办公室', 120.00, 20, '研发部门办公区', 1, NOW(), NOW());

-- 创建资产类别
INSERT INTO asset_category (name, code, parent_id, description, sort_order, created_at, updated_at) VALUES
('计算机设备', 'COMPUTER', NULL, '各类计算机设备', 1, NOW(), NOW()),
('网络设备', 'NETWORK', NULL, '网络相关设备', 2, NOW(), NOW()),
('办公设备', 'OFFICE', NULL, '办公相关设备', 3, NOW(), NOW()),
('服务器', 'SERVER', 1, '各类服务器', 1, NOW(), NOW()),
('工作站', 'WORKSTATION', 1, '员工工作电脑', 2, NOW(), NOW()),
('笔记本电脑', 'LAPTOP', 1, '笔记本电脑', 3, NOW(), NOW()),
('交换机', 'SWITCH', 2, '网络交换机', 1, NOW(), NOW()),
('路由器', 'ROUTER', 2, '网络路由器', 2, NOW(), NOW()),
('打印机', 'PRINTER', 3, '各类打印机', 1, NOW(), NOW());

-- 创建示例资产数据
INSERT INTO it_asset (asset_code, name, brand, model, category, building_id, floor_id, room_id, 
                     supplier, purchase_date, purchase_price, warranty_start_date, warranty_end_date, 
                     warranty_period, user_name, user_department, deploy_date, status, 
                     condition_rating, serial_number, created_at, updated_at) VALUES
('AS20240001', 'Dell服务器01', 'Dell', 'PowerEdge R740', '服务器', 2, 5, 5, 
 'Dell中国', '2024-01-15', 85000.00, '2024-01-15', '2027-01-15', 36, 
 '张三', 'IT部', '2024-01-20', '在用', '优', 'DL001SN2024001', NOW(), NOW()),

('AS20240002', 'HP工作站01', 'HP', 'Z4 G4', '工作站', 1, 4, 4, 
 'HP中国', '2024-02-10', 12000.00, '2024-02-10', '2027-02-10', 36, 
 '李四', '研发部', '2024-02-15', '在用', '良', 'HP001SN2024002', NOW(), NOW()),

('AS20240003', 'Cisco交换机01', 'Cisco', 'Catalyst 3850', '交换机', 2, 5, 5, 
 'Cisco中国', '2024-01-20', 25000.00, '2024-01-20', '2027-01-20', 36, 
 '网络管理员', 'IT部', '2024-01-25', '在用', '优', 'CS001SN2024003', NOW(), NOW());

-- 创建示例网络设备数据
INSERT INTO network_device (name, device_type, brand, model, ip_address, mac_address, 
                           building_id, floor_id, room_id, status, serial_number, 
                           description, created_at, updated_at) VALUES
('核心交换机01', '交换机', 'Cisco', 'Catalyst 3850', '192.168.1.1', '00:1B:44:11:3A:B7', 
 2, 5, 5, '正常', 'CS001SN2024003', '机房核心交换机', NOW(), NOW()),

('接入交换机01', '交换机', 'HP', 'ProCurve 2920', '192.168.1.10', '00:1F:29:CD:67:8F', 
 1, 4, 4, '正常', 'HP001SW2024001', '4层接入交换机', NOW(), NOW()),

('边界路由器01', '路由器', 'Cisco', 'ISR 4321', '192.168.1.254', '00:1A:2F:BB:28:FC', 
 2, 5, 5, '正常', 'CS002RT2024001', '网络边界路由器', NOW(), NOW());

-- 创建设备端口数据
INSERT INTO device_port (device_id, port_name, port_type, port_speed, status, description, created_at, updated_at) VALUES
-- 核心交换机端口
(1, 'GigabitEthernet1/0/1', 'ethernet', '1Gbps', '使用中', '连接到路由器', NOW(), NOW()),
(1, 'GigabitEthernet1/0/2', 'ethernet', '1Gbps', '使用中', '连接到接入交换机', NOW(), NOW()),
(1, 'GigabitEthernet1/0/3', 'ethernet', '1Gbps', '未使用', '备用端口', NOW(), NOW()),

-- 接入交换机端口
(2, 'FastEthernet0/1', 'ethernet', '100Mbps', '使用中', '连接到核心交换机', NOW(), NOW()),
(2, 'FastEthernet0/2', 'ethernet', '100Mbps', '使用中', '连接到服务器', NOW(), NOW()),
(2, 'FastEthernet0/3', 'ethernet', '100Mbps', '未使用', '备用端口', NOW(), NOW()),

-- 路由器端口
(3, 'GigabitEthernet0/0', 'ethernet', '1Gbps', '使用中', '内网接口', NOW(), NOW()),
(3, 'GigabitEthernet0/1', 'ethernet', '1Gbps', '使用中', '外网接口', NOW(), NOW());

-- 建立端口连接关系
UPDATE device_port SET is_connected = TRUE, connected_device_id = 3, connected_port_id = 7 WHERE id = 1;
UPDATE device_port SET is_connected = TRUE, connected_device_id = 1, connected_port_id = 1 WHERE id = 7;

UPDATE device_port SET is_connected = TRUE, connected_device_id = 2, connected_port_id = 4 WHERE id = 2;
UPDATE device_port SET is_connected = TRUE, connected_device_id = 1, connected_port_id = 2 WHERE id = 4;

-- 创建运维模板数据
INSERT INTO maintenance_template (name, template_type, description, work_content_template, 
                                 checklist_template, estimated_duration, difficulty_level, 
                                 created_at, updated_at) VALUES
('服务器日常巡检', '巡检', '服务器设备日常检查模板', '1. 检查服务器运行状态\n2. 查看系统日志\n3. 检查硬盘使用情况\n4. 检查内存使用情况\n5. 检查网络连接', 
 '["检查电源指示灯", "检查硬盘指示灯", "检查网络连接", "检查温度", "记录运行日志"]', 2, '简单', NOW(), NOW()),

('网络设备维护', '例行维护', '网络设备定期维护模板', '1. 清理设备灰尘\n2. 检查线缆连接\n3. 更新设备配置\n4. 备份配置文件\n5. 测试网络连通性', 
 '["断电前备份配置", "清理设备表面", "检查端口状态", "测试连通性", "恢复配置"]', 3, '中等', NOW(), NOW());

-- 插入初始化完成标记
INSERT INTO sys_permission (name, code, description, resource, action, created_at, updated_at) 
VALUES ('数据库初始化完成', 'db:initialized', '标记数据库已完成初始化', 'system', 'init', NOW(), NOW());