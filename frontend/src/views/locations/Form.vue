<template>
  <div class="location-form-page">
    <div class="page-header">
      <div class="header-content">
        <h2>{{ isEdit ? '编辑位置' : '新增位置' }}</h2>
        <div class="header-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" @click="saveLocation" :loading="saving">
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
        class="location-form"
      >
        <el-card title="基本信息" class="form-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="位置名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入位置名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="位置代码" prop="code">
                <el-input v-model="form.code" placeholder="请输入位置代码" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="位置类型" prop="type">
                <el-select v-model="form.type" placeholder="请选择位置类型" style="width: 100%">
                  <el-option label="数据中心" value="datacenter" />
                  <el-option label="建筑" value="building" />
                  <el-option label="楼层" value="floor" />
                  <el-option label="房间" value="room" />
                  <el-option label="机柜" value="rack" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="上级位置" prop="parent_id">
                <el-cascader
                  v-model="form.parent_id"
                  :options="locationTree"
                  :props="cascaderProps"
                  placeholder="请选择上级位置"
                  style="width: 100%"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="详细地址" prop="address">
            <el-input v-model="form.address" placeholder="请输入详细地址" />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="建筑楼层">
                <el-input v-model="form.floor" placeholder="如：地下1层" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="房间号">
                <el-input v-model="form.room" placeholder="如：A001" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="面积(m²)">
                <el-input-number 
                  v-model="form.area" 
                  :min="0" 
                  placeholder="面积"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <el-card title="管理信息" class="form-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="负责人" prop="manager">
                <el-select v-model="form.manager" placeholder="请选择负责人" style="width: 100%">
                  <el-option 
                    v-for="user in availableUsers" 
                    :key="user.id" 
                    :label="user.name" 
                    :value="user.name"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系电话">
                <el-input v-model="form.phone" placeholder="请输入联系电话" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-radio-group v-model="form.status">
                  <el-radio label="active">正常</el-radio>
                  <el-radio label="maintenance">维护中</el-radio>
                  <el-radio label="inactive">停用</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="安全等级">
                <el-select v-model="form.security_level" placeholder="请选择安全等级" style="width: 100%">
                  <el-option label="公开" value="public" />
                  <el-option label="内部" value="internal" />
                  <el-option label="机密" value="confidential" />
                  <el-option label="绝密" value="top_secret" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="备注">
            <el-input 
              v-model="form.remarks" 
              type="textarea" 
              :rows="3"
              placeholder="请输入备注信息..."
            />
          </el-form-item>
        </el-card>

        <el-card title="环境配置" class="form-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="温度范围">
                <div class="range-input">
                  <el-input-number v-model="form.temp_min" :min="0" :max="50" size="small" />
                  <span class="range-separator">-</span>
                  <el-input-number v-model="form.temp_max" :min="0" :max="50" size="small" />
                  <span class="unit">°C</span>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="湿度范围">
                <div class="range-input">
                  <el-input-number v-model="form.humidity_min" :min="0" :max="100" size="small" />
                  <span class="range-separator">-</span>
                  <el-input-number v-model="form.humidity_max" :min="0" :max="100" size="small" />
                  <span class="unit">%</span>
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="环境监控">
                <el-switch 
                  v-model="form.monitor_enabled"
                  active-text="启用监控"
                  inactive-text="禁用监控"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="告警通知">
                <el-switch 
                  v-model="form.alert_enabled"
                  active-text="启用告警"
                  inactive-text="禁用告警"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <el-card title="访问控制" class="form-section">
          <el-form-item label="访问权限">
            <el-checkbox-group v-model="form.access_permissions">
              <el-checkbox label="public">公开访问</el-checkbox>
              <el-checkbox label="employee">员工访问</el-checkbox>
              <el-checkbox label="manager">管理员访问</el-checkbox>
              <el-checkbox label="maintenance">维护人员访问</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="授权用户">
            <el-select
              v-model="form.authorized_users"
              multiple
              placeholder="选择授权用户"
              style="width: 100%"
            >
              <el-option
                v-for="user in availableUsers"
                :key="user.id"
                :label="user.name"
                :value="user.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="访问时间">
            <el-time-picker
              v-model="form.access_time_start"
              placeholder="开始时间"
              style="width: 45%; margin-right: 10px"
            />
            <span>-</span>
            <el-time-picker
              v-model="form.access_time_end"
              placeholder="结束时间"
              style="width: 45%; margin-left: 10px"
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
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)

const isEdit = computed(() => !!route.params.id)
const locationId = computed(() => route.params.id as string)

const form = ref({
  name: '',
  code: '',
  type: '',
  parent_id: [] as any[],
  address: '',
  floor: '',
  room: '',
  area: null as number | null,
  manager: '',
  phone: '',
  status: 'active',
  security_level: 'internal',
  remarks: '',
  temp_min: 18,
  temp_max: 26,
  humidity_min: 40,
  humidity_max: 70,
  monitor_enabled: true,
  alert_enabled: true,
  access_permissions: ['employee'] as string[],
  authorized_users: [] as number[],
  access_time_start: null as Date | null,
  access_time_end: null as Date | null
})

const locationTree = ref([
  {
    value: 1,
    label: '总部大楼',
    children: [
      {
        value: 2,
        label: '地下1层',
        children: [
          { value: 3, label: '主机房' },
          { value: 4, label: '配电室' }
        ]
      },
      {
        value: 5,
        label: '1层',
        children: [
          { value: 6, label: '大厅' },
          { value: 7, label: '会议室' }
        ]
      }
    ]
  }
])

const availableUsers = ref([
  { id: 1, name: '张三' },
  { id: 2, name: '李四' },
  { id: 3, name: '王五' },
  { id: 4, name: '赵六' }
])

const cascaderProps = {
  expandTrigger: 'hover' as const,
  value: 'value',
  label: 'label',
  children: 'children',
  emitPath: false
}

const rules: FormRules = {
  name: [
    { required: true, message: '请输入位置名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入位置代码', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择位置类型', trigger: 'change' }
  ],
  address: [
    { required: true, message: '请输入详细地址', trigger: 'blur' }
  ],
  manager: [
    { required: true, message: '请选择负责人', trigger: 'change' }
  ]
}

const loadLocationData = async () => {
  if (!isEdit.value) return
  
  try {
    // 模拟API调用
    const mockLocation = {
      name: '主机房A',
      code: 'DC-A-001',
      type: 'datacenter',
      parent_id: [1, 2],
      address: '北京市朝阳区科技园区1号楼',
      floor: '地下1层',
      room: 'A001',
      area: 120,
      manager: '张三',
      phone: '13800138000',
      status: 'active',
      security_level: 'confidential',
      remarks: '主要存放核心服务器和网络设备',
      temp_min: 18,
      temp_max: 26,
      humidity_min: 40,
      humidity_max: 70,
      monitor_enabled: true,
      alert_enabled: true,
      access_permissions: ['employee', 'manager'],
      authorized_users: [1, 2],
      access_time_start: null,
      access_time_end: null
    }
    
    Object.assign(form.value, mockLocation)
  } catch (error) {
    console.error('加载位置数据失败:', error)
    ElMessage.error('加载位置数据失败')
  }
}

const saveLocation = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success(isEdit.value ? '位置更新成功' : '位置创建成功')
    router.push('/app/locations')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadLocationData()
})
</script>

<style scoped>
.location-form-page {
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

.location-form {
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

.range-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: #909399;
}

.unit {
  color: #606266;
  font-size: 12px;
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
  
  .range-input {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>