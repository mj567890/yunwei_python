#!/usr/bin/env python3
"""
执行资产类别拓扑配置的简化脚本
"""
import os
import sys

# 添加backend路径到sys.path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# 执行配置
from setup_topology_categories import setup_category_topology_config

if __name__ == '__main__':
    try:
        setup_category_topology_config()
        print("\n🎉 资产类别配置成功！")
        print("现在服务器、工作站等设备都可以在拓扑图中显示和进行端口连接了。")
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)