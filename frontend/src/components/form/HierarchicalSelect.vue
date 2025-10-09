<template>
  <div class="hierarchical-select" :class="{ 'error': hasError }" ref="selectRef">
    <div class="select-dropdown" @click="toggleDropdown" :tabindex="0">
      <div class="selected-value">
        {{ selectedText || placeholder }}
      </div>
      <div class="dropdown-arrow" :class="{ 'open': isOpen }">▼</div>
    </div>
    
    <div v-if="isOpen" class="dropdown-menu">
      <div v-if="loading" class="loading-item">
        <span>🔄 加载中...</span>
      </div>
      <div v-else-if="items.length === 0" class="empty-item">
        <span>暂无数据</span>
      </div>
      <div v-else class="dropdown-content">
        <div v-for="item in flatItems" :key="item.id" class="dropdown-item" 
             :class="{ 
               'selected': modelValue === item.name,
               'parent': !item.parent_id,
               'child': item.parent_id,
               'expanded': expandedItems.has(item.id),
               'collapsed': !expandedItems.has(item.id) && hasChildren(item.id)
             }"
             @click="selectItem(item)"
             @mousedown.prevent>
          <div class="item-content" :style="{ paddingLeft: ((item.level || 0) * 20) + 'px' }">
            <span v-if="hasChildren(item.id)" 
                  class="expand-icon" 
                  @click.stop.prevent="toggleExpand(item.id)"
                  @mousedown.stop.prevent>
              {{ expandedItems.has(item.id) ? '📂' : '📁' }}
            </span>
            <span v-else class="expand-placeholder">📄</span>
            <span class="item-name">{{ item.name }}</span>
            <span v-if="item.code" class="item-code">({{ item.code }})</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// 接口定义
interface HierarchicalItem {
  id: number
  name: string
  code: string
  description?: string
  parent_id?: number | null
  sort_order: number
  is_active: boolean
  level?: number
  children?: HierarchicalItem[]
}

// Props
const props = defineProps<{
  modelValue: string
  placeholder?: string
  items: HierarchicalItem[]
  loading?: boolean
  hasError?: boolean
}>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// 响应式数据
const isOpen = ref(false)
const expandedItems = ref(new Set<number>())
const selectRef = ref<HTMLElement>()

// 计算属性
const selectedText = computed(() => {
  if (!props.modelValue) return ''
  const item = props.items.find(item => item.name === props.modelValue)
  return item ? item.name : props.modelValue
})

// 构建树形结构并计算层级
const treeItems = computed(() => {
  const buildTree = (items: HierarchicalItem[], parentId: number | null = null, level: number = 0): HierarchicalItem[] => {
    return items
      .filter(item => item.parent_id === parentId && item.is_active)
      .sort((a, b) => a.sort_order - b.sort_order)
      .map(item => ({
        ...item,
        level,
        children: buildTree(items, item.id, level + 1)
      }))
  }
  return buildTree(props.items)
})

// 扁平化的项目列表（用于渲染）
const flatItems = computed(() => {
  const flattenItems = (items: HierarchicalItem[]): HierarchicalItem[] => {
    const result: HierarchicalItem[] = []
    
    for (const item of items) {
      result.push(item)
      
      // 如果有子项且已展开，则递归添加子项
      if (item.children && item.children.length > 0 && expandedItems.value.has(item.id)) {
        result.push(...flattenItems(item.children))
      }
    }
    
    return result
  }
  
  return flattenItems(treeItems.value)
})

// 检查是否有子项
const hasChildren = (itemId: number) => {
  const item = props.items.find(i => i.id === itemId)
  return props.items.some(i => i.parent_id === itemId && i.is_active)
}

// 方法
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  if (selectRef.value && !selectRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

const selectItem = (item: HierarchicalItem) => {
  emit('update:modelValue', item.name)
  isOpen.value = false
}

const toggleExpand = (itemId: number) => {
  if (expandedItems.value.has(itemId)) {
    expandedItems.value.delete(itemId)
  } else {
    expandedItems.value.add(itemId)
  }
}

// 初始化展开顶级项目
onMounted(() => {
  // 默认展开所有顶级项目
  treeItems.value.forEach(item => {
    if (!item.parent_id) {
      expandedItems.value.add(item.id)
    }
  })
  
  // 添加点击外部事件监听
  document.addEventListener('click', handleClickOutside)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 监听数据变化，重新初始化展开状态
watch(() => props.items, () => {
  expandedItems.value.clear()
  // 默认展开所有顶级项目
  treeItems.value.forEach(item => {
    if (!item.parent_id) {
      expandedItems.value.add(item.id)
    }
  })
}, { immediate: true })
</script>

<style scoped>
.hierarchical-select {
  position: relative;
  width: 100%;
}

.select-dropdown {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  user-select: none;
  transition: border-color 0.2s;
}

.select-dropdown:hover {
  border-color: #40a9ff;
}

.select-dropdown:focus {
  outline: none;
  border-color: #40a9ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.hierarchical-select.error .select-dropdown {
  border-color: #ff4d4f;
}

.selected-value {
  flex: 1;
  color: #333;
  font-size: 14px;
}

.selected-value:empty::before {
  content: attr(placeholder);
  color: #bfbfbf;
}

.dropdown-arrow {
  font-size: 12px;
  color: #bfbfbf;
  transition: transform 0.2s;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  background: white;
  border: 1px solid #d9d9d9;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  max-height: 300px;
  overflow-y: auto;
}

.loading-item,
.empty-item {
  padding: 12px 16px;
  text-align: center;
  color: #8c8c8c;
  font-size: 14px;
}

.dropdown-content {
  padding: 4px 0;
}

.dropdown-item {
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.dropdown-item.selected {
  background-color: #e6f7ff;
  color: #1890ff;
}

.item-content {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  font-size: 14px;
}

.expand-icon {
  width: 16px;
  margin-right: 6px;
  cursor: pointer;
  user-select: none;
}

.expand-placeholder {
  width: 16px;
  margin-right: 6px;
  opacity: 0.6;
}

.item-name {
  flex: 1;
  margin-right: 8px;
}

.item-code {
  font-size: 12px;
  color: #8c8c8c;
  font-family: monospace;
}

.dropdown-item.parent .item-name {
  font-weight: 600;
  color: #1890ff;
}

.dropdown-item.child .item-name {
  color: #595959;
}

/* 滚动条样式 */
.dropdown-menu::-webkit-scrollbar {
  width: 6px;
}

.dropdown-menu::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.dropdown-menu::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.dropdown-menu::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>