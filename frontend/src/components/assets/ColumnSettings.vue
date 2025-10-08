<template>
  <div class="column-settings">
    <!-- 列配置按钮 -->
    <button @click="showDialog = true" class="btn btn-outline" title="自定义列显示">
      ⚙️ 列设置
    </button>

    <!-- 列配置对话框 -->
    <div v-if="showDialog" class="modal-overlay" @click="showDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>自定义列显示</h3>
          <button @click="showDialog = false" class="close-btn">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="settings-intro">
            <p>✨ 您可以根据需要选择要显示的列，个别必需列无法取消显示</p>
          </div>

          <!-- 分类显示列配置 -->
          <div class="column-categories">
            <!-- 基本信息 -->
            <div class="category-section">
              <h4>📋 基本信息</h4>
              <div class="column-list">
                <div 
                  v-for="column in basicColumns" 
                  :key="column.key"
                  class="column-item"
                  :class="{ 'required': column.required, 'disabled': column.required }"
                >
                  <label class="column-checkbox">
                    <input 
                      type="checkbox" 
                      v-model="column.visible" 
                      :disabled="column.required"
                    />
                    <span class="checkbox-label">
                      {{ column.title }}
                      <span v-if="column.required" class="required-tag">必需</span>
                    </span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 位置信息 -->
            <div class="category-section">
              <h4>📍 位置信息</h4>
              <div class="column-list">
                <div 
                  v-for="column in locationColumns" 
                  :key="column.key"
                  class="column-item"
                >
                  <label class="column-checkbox">
                    <input type="checkbox" v-model="column.visible" />
                    <span class="checkbox-label">{{ column.title }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 采购信息 -->
            <div class="category-section">
              <h4>💰 采购信息</h4>
              <div class="column-list">
                <div 
                  v-for="column in purchaseColumns" 
                  :key="column.key"
                  class="column-item"
                >
                  <label class="column-checkbox">
                    <input type="checkbox" v-model="column.visible" />
                    <span class="checkbox-label">{{ column.title }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 保修信息 -->
            <div class="category-section">
              <h4>🛡️ 保修信息</h4>
              <div class="column-list">
                <div 
                  v-for="column in warrantyColumns" 
                  :key="column.key"
                  class="column-item"
                >
                  <label class="column-checkbox">
                    <input type="checkbox" v-model="column.visible" />
                    <span class="checkbox-label">{{ column.title }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 使用信息 -->
            <div class="category-section">
              <h4>👤 使用信息</h4>
              <div class="column-list">
                <div 
                  v-for="column in userColumns" 
                  :key="column.key"
                  class="column-item"
                >
                  <label class="column-checkbox">
                    <input type="checkbox" v-model="column.visible" />
                    <span class="checkbox-label">{{ column.title }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 网络信息 -->
            <div class="category-section">
              <h4>🌐 网络信息</h4>
              <div class="column-list">
                <div 
                  v-for="column in networkColumns" 
                  :key="column.key"
                  class="column-item"
                >
                  <label class="column-checkbox">
                    <input type="checkbox" v-model="column.visible" />
                    <span class="checkbox-label">{{ column.title }}</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 其他信息 -->
            <div class="category-section">
              <h4>📝 其他信息</h4>
              <div class="column-list">
                <div 
                  v-for="column in otherColumns" 
                  :key="column.key"
                  class="column-item"
                >
                  <label class="column-checkbox">
                    <input type="checkbox" v-model="column.visible" />
                    <span class="checkbox-label">{{ column.title }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- 快速操作 -->
          <div class="quick-actions">
            <div class="preset-buttons">
              <button @click="applyPreset('minimal')" class="btn btn-sm btn-outline">
                📄 简化视图
              </button>
              <button @click="applyPreset('standard')" class="btn btn-sm btn-outline">
                📋 标准视图
              </button>
              <button @click="applyPreset('detailed')" class="btn btn-sm btn-outline">
                📊 详细视图
              </button>
              <button @click="applyPreset('all')" class="btn btn-sm btn-outline">
                📚 完整视图
              </button>
            </div>
            
            <div class="selection-info">
              <span class="visible-count">
                已选择 {{ visibleColumnCount }} / {{ totalColumnCount }} 列
              </span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="resetToDefault" class="btn btn-secondary">
            🔄 重置默认
          </button>
          <button @click="showDialog = false" class="btn btn-info">
            取消
          </button>
          <button @click="applySettings" class="btn btn-primary">
            ✅ 应用设置
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// 列配置接口
export interface ColumnConfig {
  key: string
  title: string
  width?: number
  visible: boolean
  required?: boolean  // 必需列，无法取消显示
  sortable?: boolean
  category: string
}

// Props
interface Props {
  columns: ColumnConfig[]
}

// Emits
interface Emits {
  (e: 'update:columns', columns: ColumnConfig[]): void
  (e: 'apply-settings', columns: ColumnConfig[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const showDialog = ref(false)

// 按类别分组的列配置
const basicColumns = computed(() => 
  props.columns.filter(col => col.category === 'basic')
)

const locationColumns = computed(() => 
  props.columns.filter(col => col.category === 'location')
)

const purchaseColumns = computed(() => 
  props.columns.filter(col => col.category === 'purchase')
)

const warrantyColumns = computed(() => 
  props.columns.filter(col => col.category === 'warranty')
)

const userColumns = computed(() => 
  props.columns.filter(col => col.category === 'user')
)

const networkColumns = computed(() => 
  props.columns.filter(col => col.category === 'network')
)

const otherColumns = computed(() => 
  props.columns.filter(col => col.category === 'other')
)

// 统计信息
const visibleColumnCount = computed(() => 
  props.columns.filter(col => col.visible).length
)

const totalColumnCount = computed(() => props.columns.length)

// 预设配置
const applyPreset = (preset: string) => {
  const updatedColumns = [...props.columns]
  
  switch (preset) {
    case 'minimal':
      // 简化视图：只显示最基本的信息
      updatedColumns.forEach(col => {
        if (['asset_code', 'name', 'category', 'status', 'actions'].includes(col.key)) {
          col.visible = true
        } else if (!col.required) {
          col.visible = false
        }
      })
      break
      
    case 'standard':
      // 标准视图：显示常用信息（当前默认显示的列）
      updatedColumns.forEach(col => {
        if (['asset_code', 'name', 'brand_model', 'category', 'location', 'user_name', 'status', 'warranty_status', 'actions'].includes(col.key)) {
          col.visible = true
        } else if (!col.required) {
          col.visible = false
        }
      })
      break
      
    case 'detailed':
      // 详细视图：显示大部分有用信息
      updatedColumns.forEach(col => {
        if (['remark'].includes(col.key)) {
          col.visible = false
        } else {
          col.visible = true
        }
      })
      break
      
    case 'all':
      // 完整视图：显示所有列
      updatedColumns.forEach(col => {
        col.visible = true
      })
      break
  }
  
  emit('update:columns', updatedColumns)
}

// 重置为默认设置
const resetToDefault = () => {
  applyPreset('standard')
}

// 应用设置
const applySettings = () => {
  // 保存到本地存储
  const columnsConfig = props.columns.map(col => ({
    key: col.key,
    visible: col.visible,
    width: col.width
  }))
  
  try {
    localStorage.setItem('asset-columns-config', JSON.stringify(columnsConfig))
    console.log('列配置已保存到本地存储')
  } catch (error) {
    console.error('保存列配置失败:', error)
  }
  
  // 触发应用设置事件
  emit('apply-settings', props.columns)
  
  // 关闭对话框
  showDialog.value = false
}

// 监听列变化，实时更新
watch(() => props.columns, (newColumns) => {
  emit('update:columns', newColumns)
}, { deep: true })
</script>

<style scoped>
.column-settings {
  display: inline-block;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  background: white;
  color: #606266;
}

.btn-outline {
  border: 1px solid #dcdfe6;
  background: white;
  color: #606266;
}

.btn-outline:hover {
  border-color: #409eff;
  color: #409eff;
}

.btn-primary {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

.btn-secondary {
  background: #909399;
  color: white;
  border-color: #909399;
}

.btn-info {
  background: #17a2b8;
  color: white;
  border-color: #17a2b8;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn:hover {
  opacity: 0.8;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 700px;
  max-width: 90vw;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
  background: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #909399;
  padding: 4px;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #606266;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.settings-intro {
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 20px;
}

.settings-intro p {
  margin: 0;
  color: #409eff;
  font-size: 14px;
}

.column-categories {
  display: grid;
  gap: 20px;
}

.category-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.column-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
  background: #fafbfc;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e6e6e6;
}

.column-item {
  display: flex;
  align-items: center;
}

.column-item.required {
  background: #f0f9ff;
  border-radius: 4px;
  padding: 4px 8px;
}

.column-item.disabled {
  opacity: 0.6;
}

.column-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  width: 100%;
}

.column-checkbox input[type="checkbox"] {
  margin-right: 8px;
  cursor: pointer;
}

.column-checkbox input[type="checkbox"]:disabled {
  cursor: not-allowed;
}

.checkbox-label {
  font-size: 14px;
  color: #606266;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.required-tag {
  background: #409eff;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.quick-actions {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-top: 24px;
}

.preset-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.selection-info {
  display: flex;
  justify-content: center;
  align-items: center;
}

.visible-count {
  color: #409eff;
  font-weight: 600;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
  background: #f8f9fa;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95vw;
    height: 90vh;
  }
  
  .column-list {
    grid-template-columns: 1fr;
  }
  
  .preset-buttons {
    flex-direction: column;
  }
}
</style>