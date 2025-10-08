#!/usr/bin/env python3
"""
IT运维系统 - 综合健康检查脚本
检查系统的所有组件是否正常运行，包括数据库连接、API接口、文件权限等
"""

import os
import sys
import json
import requests
import subprocess  
import time
from datetime import datetime
from typing import Dict, List, Any

class SystemHealthChecker:
    def __init__(self):
        self.results = {}
        self.backend_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:5173"
        
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_file_permissions(self) -> Dict[str, Any]:
        """检查文件权限"""
        self.log("检查文件权限...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        # 检查关键目录
        key_dirs = [
            "backend/uploads",
            "backend/logs",
            "backend/instance"
        ]
        
        for dir_path in key_dirs:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    result["details"][dir_path] = "创建成功"
                except Exception as e:
                    result["status"] = "fail"
                    result["issues"].append(f"无法创建目录 {dir_path}: {str(e)}")
            else:
                # 检查读写权限
                if os.access(dir_path, os.R_OK | os.W_OK):
                    result["details"][dir_path] = "权限正常"
                else:
                    result["status"] = "fail"
                    result["issues"].append(f"目录 {dir_path} 权限不足")
        
        return result
    
    def check_python_dependencies(self) -> Dict[str, Any]:
        """检查Python依赖"""
        self.log("检查Python依赖...")
        
        result = {
            "status": "pass",
            "issues": [],
            "installed": [],
            "missing": []
        }
        
        # 读取requirements.txt
        try:
            with open("backend/requirements.txt", "r") as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except FileNotFoundError:
            result["status"] = "fail"
            result["issues"].append("找不到 requirements.txt 文件")
            return result
        
        # 检查每个依赖
        for req in requirements:
            package_name = req.split("==")[0].split(">=")[0].split("<=")[0]
            try:
                __import__(package_name.replace("-", "_"))
                result["installed"].append(package_name)
            except ImportError:
                result["missing"].append(package_name)
                result["status"] = "fail"
        
        if result["missing"]:
            result["issues"].append(f"缺少依赖包: {', '.join(result['missing'])}")
            
        return result
    
    def check_database_connection(self) -> Dict[str, Any]:
        """检查数据库连接"""
        self.log("检查数据库连接...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        try:
            import pymysql
            from backend.config.config import Config
            
            config = Config()
            
            # 解析数据库URI
            uri = config.SQLALCHEMY_DATABASE_URI
            if "mysql+pymysql://" in uri:
                parts = uri.replace("mysql+pymysql://", "").split("/")
                auth_host = parts[0]
                database = parts[1].split("?")[0] if "?" in parts[1] else parts[1]
                
                user_pass, host_port = auth_host.split("@")
                username, password = user_pass.split(":")
                host_port_parts = host_port.split(":")
                host = host_port_parts[0]
                port = int(host_port_parts[1]) if len(host_port_parts) > 1 else 3306
                
                # 测试连接
                connection = pymysql.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=password,
                    database=database,
                    charset='utf8mb4'
                )
                
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                
                result["details"]["database"] = database
                result["details"]["version"] = version
                result["details"]["host"] = f"{host}:{port}"
                
                cursor.close()
                connection.close()
                
        except Exception as e:
            result["status"] = "fail"
            result["issues"].append(f"数据库连接失败: {str(e)}")
            
        return result
    
    def check_backend_api(self) -> Dict[str, Any]:
        """检查后端API"""
        self.log("检查后端API...")
        
        result = {
            "status": "pass",
            "issues": [],
            "endpoints": {}
        }
        
        # 测试关键API端点
        test_endpoints = [
            {"url": "/api/auth/login", "method": "POST", "data": {"username": "test", "password": "test"}},
            {"url": "/api/assets", "method": "GET"},
            {"url": "/api/statistics/overview", "method": "GET"}
        ]
        
        for endpoint in test_endpoints:
            try:
                url = f"{self.backend_url}{endpoint['url']}"
                
                if endpoint["method"] == "GET":
                    response = requests.get(url, timeout=5)
                elif endpoint["method"] == "POST":
                    response = requests.post(url, json=endpoint.get("data", {}), timeout=5)
                
                result["endpoints"][endpoint["url"]] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
                
                # 对于登录接口，401是预期的（因为是测试凭据）
                if endpoint["url"] == "/api/auth/login" and response.status_code == 401:
                    continue
                    
                # 对于需要认证的接口，401是预期的
                if response.status_code == 401:
                    continue
                    
                if response.status_code >= 500:
                    result["status"] = "fail"
                    result["issues"].append(f"端点 {endpoint['url']} 返回服务器错误")
                    
            except requests.exceptions.ConnectionError:
                result["status"] = "fail"
                result["issues"].append(f"无法连接到后端服务器 {self.backend_url}")
                break
            except Exception as e:
                result["status"] = "fail"
                result["issues"].append(f"测试端点 {endpoint['url']} 时出错: {str(e)}")
        
        return result
    
    def check_frontend_build(self) -> Dict[str, Any]:
        """检查前端构建"""
        self.log("检查前端构建...")
        
        result = {
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        # 检查package.json
        try:
            with open("frontend/package.json", "r") as f:
                package_data = json.load(f)
                result["details"]["name"] = package_data.get("name")
                result["details"]["version"] = package_data.get("version")
        except FileNotFoundError:
            result["status"] = "fail"
            result["issues"].append("找不到 frontend/package.json")
            return result
        
        # 检查node_modules
        if not os.path.exists("frontend/node_modules"):
            result["status"] = "fail"
            result["issues"].append("前端依赖未安装，请运行 npm install")
        
        # 检查关键文件
        key_files = [
            "frontend/src/main.ts",
            "frontend/src/App.vue",
            "frontend/index.html"
        ]
        
        for file_path in key_files:
            if not os.path.exists(file_path):
                result["status"] = "fail"
                result["issues"].append(f"缺少关键文件: {file_path}")
        
        return result
    
    def check_security_config(self) -> Dict[str, Any]:
        """检查安全配置"""
        self.log("检查安全配置...")
        
        result = {
            "status": "pass",
            "issues": [],
            "warnings": [],
            "details": {}
        }
        
        # 检查环境变量
        env_vars = ["SECRET_KEY", "JWT_SECRET_KEY", "MYSQL_PASSWORD"]
        for var in env_vars:
            if not os.environ.get(var):
                if os.environ.get("FLASK_ENV") == "production":
                    result["status"] = "fail"
                    result["issues"].append(f"生产环境必须设置环境变量: {var}")
                else:
                    result["warnings"].append(f"开发环境建议设置环境变量: {var}")
        
        # 检查配置文件
        try:
            from backend.config.config import Config
            config = Config()
            
            # 检查密钥长度
            if hasattr(config, 'SECRET_KEY') and len(config.SECRET_KEY) < 32:
                result["warnings"].append("SECRET_KEY 长度建议至少32位")
                
            result["details"]["debug"] = getattr(config, 'DEBUG', False)
            result["details"]["testing"] = getattr(config, 'TESTING', False)
            
        except Exception as e:
            result["status"] = "fail"
            result["issues"].append(f"无法加载配置: {str(e)}")
        
        return result
    
    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查"""
        self.log("开始系统健康检查...")
        
        checks = [
            ("文件权限", self.check_file_permissions),
            ("Python依赖", self.check_python_dependencies),
            ("数据库连接", self.check_database_connection),
            ("安全配置", self.check_security_config),
            ("前端构建", self.check_frontend_build),
            ("后端API", self.check_backend_api)
        ]
        
        overall_status = "pass"
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                self.results[check_name] = result
                
                if result["status"] == "fail":
                    overall_status = "fail"
                    self.log(f"✗ {check_name}: 失败", "ERROR")
                    for issue in result["issues"]:
                        self.log(f"  - {issue}", "ERROR")
                else:
                    self.log(f"✓ {check_name}: 通过", "INFO")
                    if "warnings" in result and result["warnings"]:
                        for warning in result["warnings"]:
                            self.log(f"  ⚠ {warning}", "WARNING")
                            
            except Exception as e:
                self.log(f"✗ {check_name}: 检查时出错 - {str(e)}", "ERROR")
                self.results[check_name] = {
                    "status": "fail",
                    "issues": [f"检查过程出错: {str(e)}"]
                }
                overall_status = "fail"
        
        self.results["overall_status"] = overall_status
        self.results["timestamp"] = datetime.now().isoformat()
        
        return self.results
    
    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("=" * 60)
        report.append("IT运维系统 - 健康检查报告")
        report.append("=" * 60)
        report.append(f"检查时间: {self.results.get('timestamp', 'N/A')}")
        report.append(f"总体状态: {'✓ 通过' if self.results.get('overall_status') == 'pass' else '✗ 失败'}")
        report.append("")
        
        for check_name, result in self.results.items():
            if check_name in ["overall_status", "timestamp"]:
                continue
                
            status_icon = "✓" if result["status"] == "pass" else "✗"
            report.append(f"{status_icon} {check_name}: {result['status'].upper()}")
            
            if result.get("issues"):
                for issue in result["issues"]:
                    report.append(f"  ✗ {issue}")
            
            if result.get("warnings"):
                for warning in result["warnings"]:
                    report.append(f"  ⚠ {warning}")
            
            if result.get("details"):
                for key, value in result["details"].items():
                    report.append(f"  • {key}: {value}")
            
            report.append("")
        
        return "\n".join(report)


def main():
    """主函数"""
    checker = SystemHealthChecker()
    
    # 运行检查
    results = checker.run_all_checks()
    
    # 生成报告
    report = checker.generate_report()
    print("\n" + report)
    
    # 保存报告到文件
    report_file = f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存到: {report_file}")
    
    # 根据检查结果设置退出码
    exit_code = 0 if results["overall_status"] == "pass" else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()