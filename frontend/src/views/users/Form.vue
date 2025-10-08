<template>
  <div class="user-form-page">
    <div class="page-header">
      <div class="header-content">
        <h2>{{ isEdit ? '编辑用户' : '新增用户' }}</h2>
        <div class="header-actions">
          <el-button @click="goBack">返回</el-button>
          <el-button type="primary" @click="saveUser" :loading="saving">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="page-content">
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="120px"
        class="user-form"
      >
        <el-card title="基本信息" class="form-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="用户名" prop="username">
                <el-input 
                  v-model="form.username" 
                  placeholder="请输入用户名"
                  :disabled="isEdit"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="真实姓名" prop="real_name">
                <el-input 
                  v-model="form.real_name" 
                  placeholder="请输入真实姓名"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="邮箱" prop="email">
                <el-input 
                  v-model="form.email" 
                  placeholder="请输入邮箱地址"
                  type="email"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="电话" prop="phone">
                <el-input 
                  v-model="form.phone" 
                  placeholder="请输入电话号码"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="部门" prop="department">
                <el-select 
                  v-model="form.department" 
                  placeholder="请选择部门"
                  style="width: 100%"
                >
                  <el-option 
                    v-for="dept in departments" 
                    :key="dept.value" 
                    :label="dept.label" 
                    :value="dept.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职位" prop="position">
                <el-input 
                  v-model="form.position" 
                  placeholder="请输入职位"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <el-card title="账户设置" class="form-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="角色" prop="role_id">
                <el-select 
                  v-model="form.role_id" 
                  placeholder="请选择角色"
                  style="width: 100%"
                >
                  <el-option 
                    v-for="role in roles" 
                    :key="role.id" 
                    :label="role.name" 
                    :value="role.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-radio-group v-model="form.status">
                  <el-radio :label="1">启用</el-radio>
                  <el-radio :label="0">禁用</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20" v-if="!isEdit">
            <el-col :span="12">
              <el-form-item label="密码" prop="password">
                <el-input 
                  v-model="form.password" 
                  placeholder="请输入密码"
                  type="password"
                  show-password
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="确认密码" prop="confirm_password">
                <el-input 
                  v-model="form.confirm_password" 
                  placeholder="请再次输入密码"
                  type="password"
                  show-password
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="允许的IP范围" prop="allowed_ips">
            <el-input 
              v-model="form.allowed_ips" 
              placeholder="请输入允许的IP范围，多个用逗号分隔"
              type="textarea"
              :rows="2"
            />
            <div class="form-help">
              示例：192.168.1.0/24, 10.0.0.1, 支持CIDR格式
            </div>
          </el-form-item>
        </el-card>

        <el-card title="权限配置" class="form-section">
          <el-form-item label="功能权限">
            <el-checkbox-group v-model="form.permissions">
              <div class="permission-group" v-for="group in permissionGroups" :key="group.name">
                <div class="permission-group-title">{{ group.name }}</div>
                <div class="permission-items">
                  <el-checkbox 
                    v-for="perm in group.permissions" 
                    :key="perm.id" 
                    :label="perm.id"
                    class="permission-item"
                  >
                    {{ perm.name }}
                  </el-checkbox>
                </div>
              </div>
            </el-checkbox-group>
          </el-form-item>
        </el-card>

        <el-card title="个人设置" class="form-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="时区">
                <el-select 
                  v-model="form.timezone" 
                  placeholder="请选择时区"
                  style="width: 100%"
                >
                  <el-option label="Asia/Shanghai" value="Asia/Shanghai" />
                  <el-option label="UTC" value="UTC" />
                  <el-option label="America/New_York" value="America/New_York" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="语言">
                <el-select 
                  v-model="form.language" 
                  placeholder="请选择语言"
                  style="width: 100%"
                >
                  <el-option label="中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="备注">
            <el-input 
              v-model="form.remarks" 
              placeholder="请输入备注信息"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
        </el-card>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)

const isEdit = computed(() => !!route.params.id)
const userId = computed(() => route.params.id as string)

const form = ref({
  username: '',
  real_name: '',
  email: '',
  phone: '',
  department: '',
  position: '',
  role_id: null,
  status: 1,
  password: '',
  confirm_password: '',
  allowed_ips: '',
  permissions: [],
  timezone: 'Asia/Shanghai',
  language: 'zh-CN',
  remarks: ''
})

const departments = ref([
  { label: 'IT部门', value: 'IT' },
  { label: '运维部门', value: 'OPS' },
  { label: '安全部门', value: 'SEC' },
  { label: '业务部门', value: 'BIZ' }
])

const roles = ref([
  { id: 1, name: '超级管理员' },
  { id: 2, name: '系统管理员' },
  { id: 3, name: '运维工程师' },
  { id: 4, name: '普通用户' }
])

const permissionGroups = ref([
  {
    name: '资产管理',
    permissions: [
      { id: 'asset_view', name: '查看资产' },
      { id: 'asset_create', name: '创建资产' },
      { id: 'asset_edit', name: '编辑资产' },
      { id: 'asset_delete', name: '删除资产' }
    ]
  },
  {
    name: '网络管理',
    permissions: [
      { id: 'network_view', name: '查看网络' },
      { id: 'network_config', name: '配置网络' },
      { id: 'topology_edit', name: '编辑拓扑' }
    ]
  },
  {
    name: '用户管理',
    permissions: [
      { id: 'user_view', name: '查看用户' },
      { id: 'user_create', name: '创建用户' },
      { id: 'user_edit', name: '编辑用户' },
      { id: 'user_delete', name: '删除用户' }
    ]
  },
  {
    name: '系统设置',
    permissions: [
      { id: 'system_config', name: '系统配置' },
      { id: 'backup_manage', name: '备份管理' },
      { id: 'log_view', name: '查看日志' }
    ]
  }
])

const validatePassword = (rule: any, value: any, callback: any) => {
  if (!isEdit.value && !value) {
    callback(new Error('请输入密码'))
  } else if (value && value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (!isEdit.value && !value) {
    callback(new Error('请确认密码'))
  } else if (value !== form.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role_id: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirm_password: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const loadUserData = async () => {
  if (!isEdit.value) return
  
  try {
    // 模拟API调用
    const userData = {
      id: userId.value,
      username: 'demo_user',
      real_name: '演示用户',
      email: 'demo@example.com',
      phone: '13800138000',
      department: 'IT',
      position: '系统管理员',
      role_id: 2,
      status: 1,
      allowed_ips: '192.168.1.0/24',
      permissions: ['asset_view', 'asset_create', 'network_view'],
      timezone: 'Asia/Shanghai',
      language: 'zh-CN',
      remarks: '演示用户账户'
    }
    
    Object.assign(form.value, userData)
  } catch (error) {
    console.error('加载用户数据失败:', error)
    ElMessage.error('加载用户数据失败')
  }
}

const saveUser = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success(isEdit.value ? '用户更新成功' : '用户创建成功')
    goBack()
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error('保存用户失败')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.user-form-page {
  background: #f5f7fa;
  min-height: 100%;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.header-content h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.page-content {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.user-form {
  background: white;
}

.form-section {
  margin-bottom: 24px;
}

.form-section :deep(.el-card__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  font-weight: 500;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.permission-group {
  margin-bottom: 20px;
}

.permission-group-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #e6e6e6;
}

.permission-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
}

.permission-item {
  margin: 0;
}

@media (max-width: 768px) {
  .page-content {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    height: auto;
    padding: 16px 0;
  }
  
  .header-actions {
    margin-top: 12px;
    width: 100%;
  }
  
  .permission-items {
    grid-template-columns: 1fr;
  }
}
</style>