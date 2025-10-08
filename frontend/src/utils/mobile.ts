// @ts-nocheck
// 移动端检测工具
export const isMobile = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// 获取设备类型
export const getDeviceType = (): 'mobile' | 'tablet' | 'desktop' => {
  const width = window.innerWidth
  if (width <= 768) return 'mobile'
  if (width <= 1024) return 'tablet'
  return 'desktop'
}

// 触控事件处理
export class TouchHandler {
  private startX: number = 0
  private startY: number = 0
  private threshold: number = 50

  constructor(threshold: number = 50) {
    this.threshold = threshold
  }

  onTouchStart = (event: TouchEvent) => {
    const touch = event.touches[0]
    this.startX = touch.clientX
    this.startY = touch.clientY
  }

  onTouchEnd = (event: TouchEvent, callbacks: {
    onSwipeLeft?: () => void
    onSwipeRight?: () => void
    onSwipeUp?: () => void
    onSwipeDown?: () => void
  }) => {
    const touch = event.changedTouches[0]
    const deltaX = touch.clientX - this.startX
    const deltaY = touch.clientY - this.startY

    // 水平滑动
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > this.threshold) {
      if (deltaX > 0) {
        callbacks.onSwipeRight?.()
      } else {
        callbacks.onSwipeLeft?.()
      }
    }
    // 垂直滑动
    else if (Math.abs(deltaY) > this.threshold) {
      if (deltaY > 0) {
        callbacks.onSwipeDown?.()
      } else {
        callbacks.onSwipeUp?.()
      }
    }
  }
}

// 移动端工具栏配置
export interface MobileToolbarItem {
  icon: string
  label: string
  action: () => void
  active?: boolean
}

// 响应式断点
export const breakpoints = {
  xs: 0,      // 超小屏幕
  sm: 576,    // 小屏幕
  md: 768,    // 中等屏幕
  lg: 992,    // 大屏幕
  xl: 1200,   // 超大屏幕
  xxl: 1600   // 极大屏幕
}

// 移动端布局管理器
export class MobileLayoutManager {
  private mediaQueries: Map<string, MediaQueryList> = new Map()
  private callbacks: Map<string, (matches: boolean) => void> = new Map()

  constructor() {
    this.setupMediaQueries()
  }

  private setupMediaQueries() {
    Object.entries(breakpoints).forEach(([key, value]) => {
      const query = window.matchMedia(`(min-width: ${value}px)`)
      this.mediaQueries.set(key, query)
    })
  }

  onBreakpointChange(breakpoint: string, callback: (matches: boolean) => void) {
    const query = this.mediaQueries.get(breakpoint)
    if (query) {
      this.callbacks.set(breakpoint, callback)
      query.addEventListener('change', (e) => callback(e.matches))
      callback(query.matches) // 初始调用
    }
  }

  getCurrentBreakpoint(): string {
    const width = window.innerWidth
    if (width >= breakpoints.xxl) return 'xxl'
    if (width >= breakpoints.xl) return 'xl'
    if (width >= breakpoints.lg) return 'lg'
    if (width >= breakpoints.md) return 'md'
    if (width >= breakpoints.sm) return 'sm'
    return 'xs'
  }

  isMobileLayout(): boolean {
    return ['xs', 'sm'].includes(this.getCurrentBreakpoint())
  }
}

// 虚拟滚动优化（移动端性能优化）
export class VirtualScroll {
  private container: HTMLElement
  private itemHeight: number
  private visibleCount: number
  private totalCount: number
  private scrollTop: number = 0

  constructor(container: HTMLElement, itemHeight: number) {
    this.container = container
    this.itemHeight = itemHeight
    this.visibleCount = Math.ceil(container.clientHeight / itemHeight) + 2
    this.totalCount = 0
  }

  setTotalCount(count: number) {
    this.totalCount = count
  }

  getVisibleRange(): { start: number; end: number } {
    const start = Math.floor(this.scrollTop / this.itemHeight)
    const end = Math.min(start + this.visibleCount, this.totalCount)
    return { start: Math.max(0, start), end }
  }

  onScroll(scrollTop: number) {
    this.scrollTop = scrollTop
  }
}

// 移动端手势识别
export class GestureRecognizer {
  private element: HTMLElement
  private isLongPress: boolean = false
  private longPressTimer: number | null = null
  private longPressDelay: number = 500

  constructor(element: HTMLElement) {
    this.element = element
    this.setupGestures()
  }

  private setupGestures() {
    this.element.addEventListener('touchstart', this.onTouchStart.bind(this))
    this.element.addEventListener('touchend', this.onTouchEnd.bind(this))
    this.element.addEventListener('touchcancel', this.onTouchCancel.bind(this))
  }

  private onTouchStart(event: TouchEvent) {
    this.isLongPress = false
    this.longPressTimer = window.setTimeout(() => {
      this.isLongPress = true
      this.onLongPress(event)
    }, this.longPressDelay)
  }

  private onTouchEnd(event: TouchEvent) {
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer)
      this.longPressTimer = null
    }

    if (!this.isLongPress) {
      this.onTap(event)
    }
  }

  private onTouchCancel(event: TouchEvent) {
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer)
      this.longPressTimer = null
    }
    this.isLongPress = false
  }

  onTap(event: TouchEvent) {
    // 由子类实现
  }

  onLongPress(event: TouchEvent) {
    // 由子类实现
  }
}

// 移动端适配工具函数
export const mobileUtils = {
  // 设置viewport
  setViewport: () => {
    const viewport = document.querySelector('meta[name="viewport"]')
    if (viewport) {
      viewport.setAttribute('content', 
        'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
      )
    }
  },

  // 禁用移动端橡皮筋效果
  disableBounce: () => {
    document.body.style.overflow = 'hidden'
    document.addEventListener('touchmove', (e) => {
      e.preventDefault()
    }, { passive: false })
  },

  // 优化触控目标大小
  optimizeTouchTargets: () => {
    const style = document.createElement('style')
    style.textContent = `
      .touch-target {
        min-height: 44px;
        min-width: 44px;
        padding: 8px;
      }
      
      .mobile-button {
        padding: 12px 20px;
        font-size: 16px;
        border-radius: 8px;
      }
      
      .mobile-input {
        padding: 12px;
        font-size: 16px;
        border-radius: 8px;
      }
    `
    document.head.appendChild(style)
  },

  // 处理iOS安全区域
  handleSafeArea: () => {
    const style = document.createElement('style')
    style.textContent = `
      .safe-area-inset-top {
        padding-top: env(safe-area-inset-top);
      }
      
      .safe-area-inset-bottom {
        padding-bottom: env(safe-area-inset-bottom);
      }
      
      .safe-area-inset-left {
        padding-left: env(safe-area-inset-left);
      }
      
      .safe-area-inset-right {
        padding-right: env(safe-area-inset-right);
      }
    `
    document.head.appendChild(style)
  }
}

export default {
  isMobile,
  getDeviceType,
  TouchHandler,
  MobileLayoutManager,
  VirtualScroll,
  GestureRecognizer,
  mobileUtils,
  breakpoints
}