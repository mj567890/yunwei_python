"""
等保2.0合规性检查工具
实施网络安全等级保护2.0标准的合规性检查
"""
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re
import socket
import ssl


class ComplianceLevel(Enum):
    """合规等级"""
    LEVEL_1 = "一级"
    LEVEL_2 = "二级"  
    LEVEL_3 = "三级"
    LEVEL_4 = "四级"
    LEVEL_5 = "五级"


class SecurityRequirement(Enum):
    """安全要求类别"""
    PHYSICAL_SECURITY = "物理安全"
    NETWORK_SECURITY = "网络安全"
    HOST_SECURITY = "主机安全"
    APPLICATION_SECURITY = "应用安全"
    DATA_SECURITY = "数据安全"
    SECURITY_MANAGEMENT = "安全管理"


class ComplianceCheck:
    """合规性检查项"""
    
    def __init__(self, requirement: SecurityRequirement, check_id: str, 
                 description: str, level: ComplianceLevel):
        self.requirement = requirement
        self.check_id = check_id
        self.description = description
        self.level = level
        self.status = False
        self.details = ""
        self.risk_score = 0


class PasswordComplexityChecker:
    """密码复杂性检查器"""
    
    @staticmethod
    def check_password_strength(password: str) -> Tuple[bool, str, int]:
        """
        检查密码强度
        返回: (是否合规, 详细信息, 强度评分)
        """
        score = 0
        issues = []
        
        # 长度检查
        if len(password) >= 8:
            score += 20
        else:
            issues.append("密码长度应不少于8位")
        
        # 字符类型检查
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        char_types = sum([has_lower, has_upper, has_digit, has_special])
        
        if char_types >= 3:
            score += 30
        elif char_types >= 2:
            score += 15
        else:
            issues.append("密码应包含至少3种字符类型（大写字母、小写字母、数字、特殊字符）")
        
        # 复杂度检查
        if len(set(password)) >= len(password) * 0.6:  # 字符重复度检查
            score += 20
        else:
            issues.append("密码字符重复度过高")
        
        # 常见弱密码检查
        weak_patterns = [
            r'123+', r'abc+', r'qwerty', r'password', r'admin',
            r'000+', r'111+', r'aaa+', r'root', r'guest'
        ]
        
        is_weak = any(re.search(pattern, password.lower()) for pattern in weak_patterns)
        if not is_weak:
            score += 20
        else:
            issues.append("密码包含常见弱密码模式")
        
        # 键盘序列检查
        keyboard_sequences = ['qwerty', 'asdf', '1234', 'abcd']
        has_sequence = any(seq in password.lower() for seq in keyboard_sequences)
        if not has_sequence:
            score += 10
        else:
            issues.append("密码包含键盘序列")
        
        is_compliant = score >= 70 and len(issues) == 0
        details = "密码强度检查通过" if is_compliant else "; ".join(issues)
        
        return is_compliant, details, score


class NetworkSecurityChecker:
    """网络安全检查器"""
    
    @staticmethod
    def check_ssl_configuration(hostname: str, port: int = 443) -> Tuple[bool, str]:
        """检查SSL/TLS配置"""
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    protocol = ssock.version()
                    cipher = ssock.cipher()
                    
                    issues = []
                    
                    # 检查协议版本
                    if protocol in ['TLSv1.2', 'TLSv1.3']:
                        pass  # 合规
                    else:
                        issues.append(f"不安全的TLS版本: {protocol}")
                    
                    # 检查加密套件
                    if cipher and len(cipher) >= 3:
                        cipher_name = cipher[0]
                        if 'AES' not in cipher_name or '128' in cipher_name:
                            issues.append(f"加密强度不足: {cipher_name}")
                    
                    # 检查证书有效期
                    if cert:
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        if not_after - datetime.now() < timedelta(days=30):
                            issues.append("SSL证书即将过期")
                    
                    is_compliant = len(issues) == 0
                    details = "SSL配置检查通过" if is_compliant else "; ".join(issues)
                    
                    return is_compliant, details
                    
        except Exception as e:
            return False, f"SSL检查失败: {str(e)}"
    
    @staticmethod
    def check_security_headers(headers: Dict[str, str]) -> Tuple[bool, str]:
        """检查HTTP安全头"""
        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': None,  # 存在即可
            'Content-Security-Policy': None,
            'Referrer-Policy': None
        }
        
        missing_headers = []
        incorrect_headers = []
        
        for header, expected in required_headers.items():
            if header not in headers:
                missing_headers.append(header)
            elif expected and isinstance(expected, str):
                if headers[header] != expected:
                    incorrect_headers.append(f"{header}: {headers[header]}")
            elif expected and isinstance(expected, list):
                if headers[header] not in expected:
                    incorrect_headers.append(f"{header}: {headers[header]}")
        
        issues = []
        if missing_headers:
            issues.append(f"缺少安全头: {', '.join(missing_headers)}")
        if incorrect_headers:
            issues.append(f"不正确的安全头: {', '.join(incorrect_headers)}")
        
        is_compliant = len(issues) == 0
        details = "HTTP安全头检查通过" if is_compliant else "; ".join(issues)
        
        return is_compliant, details


class DataSecurityChecker:
    """数据安全检查器"""
    
    @staticmethod
    def check_encryption_strength(algorithm: str, key_length: int) -> Tuple[bool, str]:
        """检查加密强度"""
        compliant_algorithms = {
            'AES': {'min_key_length': 256},
            'RSA': {'min_key_length': 2048},
            'ECC': {'min_key_length': 256},
            'SM2': {'min_key_length': 256},
            'SM4': {'min_key_length': 128}
        }
        
        if algorithm not in compliant_algorithms:
            return False, f"不支持的加密算法: {algorithm}"
        
        min_length = compliant_algorithms[algorithm]['min_key_length']
        if key_length < min_length:
            return False, f"{algorithm}密钥长度{key_length}位不足，至少需要{min_length}位"
        
        return True, f"{algorithm}-{key_length}加密强度符合要求"
    
    @staticmethod
    def check_hash_algorithm(algorithm: str) -> Tuple[bool, str]:
        """检查哈希算法"""
        secure_algorithms = ['SHA256', 'SHA384', 'SHA512', 'SM3']
        insecure_algorithms = ['MD5', 'SHA1']
        
        if algorithm in insecure_algorithms:
            return False, f"不安全的哈希算法: {algorithm}"
        
        if algorithm in secure_algorithms:
            return True, f"哈希算法{algorithm}符合安全要求"
        
        return False, f"未知的哈希算法: {algorithm}"


class ComplianceManager:
    """等保2.0合规性管理器"""
    
    def __init__(self, target_level: ComplianceLevel = ComplianceLevel.LEVEL_3):
        self.target_level = target_level
        self.checks: List[ComplianceCheck] = []
        self.password_checker = PasswordComplexityChecker()
        self.network_checker = NetworkSecurityChecker()
        self.data_checker = DataSecurityChecker()
        self._initialize_checks()
    
    def _initialize_checks(self):
        """初始化合规检查项"""
        # 身份鉴别检查
        self.checks.extend([
            ComplianceCheck(
                SecurityRequirement.APPLICATION_SECURITY,
                "AUTH_001",
                "密码复杂度符合要求",
                ComplianceLevel.LEVEL_2
            ),
            ComplianceCheck(
                SecurityRequirement.APPLICATION_SECURITY,
                "AUTH_002", 
                "账户锁定机制启用",
                ComplianceLevel.LEVEL_2
            ),
            ComplianceCheck(
                SecurityRequirement.APPLICATION_SECURITY,
                "AUTH_003",
                "会话管理安全",
                ComplianceLevel.LEVEL_2
            )
        ])
        
        # 访问控制检查
        self.checks.extend([
            ComplianceCheck(
                SecurityRequirement.APPLICATION_SECURITY,
                "ACCESS_001",
                "基于角色的访问控制(RBAC)",
                ComplianceLevel.LEVEL_2
            ),
            ComplianceCheck(
                SecurityRequirement.APPLICATION_SECURITY,
                "ACCESS_002",
                "最小权限原则",
                ComplianceLevel.LEVEL_2
            )
        ])
        
        # 网络安全检查
        self.checks.extend([
            ComplianceCheck(
                SecurityRequirement.NETWORK_SECURITY,
                "NET_001",
                "通信加密",
                ComplianceLevel.LEVEL_2
            ),
            ComplianceCheck(
                SecurityRequirement.NETWORK_SECURITY,
                "NET_002",
                "网络边界防护",
                ComplianceLevel.LEVEL_2
            )
        ])
        
        # 数据安全检查
        self.checks.extend([
            ComplianceCheck(
                SecurityRequirement.DATA_SECURITY,
                "DATA_001",
                "数据加密存储",
                ComplianceLevel.LEVEL_2
            ),
            ComplianceCheck(
                SecurityRequirement.DATA_SECURITY,
                "DATA_002",
                "数据完整性校验",
                ComplianceLevel.LEVEL_2
            )
        ])
        
        # 安全审计检查
        self.checks.extend([
            ComplianceCheck(
                SecurityRequirement.SECURITY_MANAGEMENT,
                "AUDIT_001",
                "安全审计日志记录",
                ComplianceLevel.LEVEL_2
            ),
            ComplianceCheck(
                SecurityRequirement.SECURITY_MANAGEMENT,
                "AUDIT_002",
                "日志完整性保护",
                ComplianceLevel.LEVEL_2
            )
        ])
    
    def check_password_compliance(self, password: str) -> ComplianceCheck:
        """检查密码合规性"""
        check = next((c for c in self.checks if c.check_id == "AUTH_001"), None)
        if check:
            is_compliant, details, score = self.password_checker.check_password_strength(password)
            check.status = is_compliant
            check.details = details
            check.risk_score = 100 - score if not is_compliant else 0
        return check
    
    def check_network_compliance(self, hostname: str, headers: Dict[str, str]) -> List[ComplianceCheck]:
        """检查网络安全合规性"""
        results = []
        
        # SSL检查
        net_check = next((c for c in self.checks if c.check_id == "NET_001"), None)
        if net_check:
            is_compliant, details = self.network_checker.check_ssl_configuration(hostname)
            net_check.status = is_compliant
            net_check.details = details
            net_check.risk_score = 80 if not is_compliant else 0
            results.append(net_check)
        
        # 安全头检查
        header_check = next((c for c in self.checks if c.check_id == "NET_002"), None)
        if header_check:
            is_compliant, details = self.network_checker.check_security_headers(headers)
            header_check.status = is_compliant
            header_check.details = details
            header_check.risk_score = 60 if not is_compliant else 0
            results.append(header_check)
        
        return results
    
    def check_encryption_compliance(self, algorithm: str, key_length: int) -> ComplianceCheck:
        """检查加密合规性"""
        check = next((c for c in self.checks if c.check_id == "DATA_001"), None)
        if check:
            is_compliant, details = self.data_checker.check_encryption_strength(algorithm, key_length)
            check.status = is_compliant
            check.details = details
            check.risk_score = 90 if not is_compliant else 0
        return check
    
    def generate_compliance_report(self) -> Dict:
        """生成合规性报告"""
        total_checks = len(self.checks)
        passed_checks = sum(1 for check in self.checks if check.status)
        compliance_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # 按要求分类统计
        requirements = {}
        for check in self.checks:
            req_name = check.requirement.value
            if req_name not in requirements:
                requirements[req_name] = {'total': 0, 'passed': 0, 'high_risk': 0}
            
            requirements[req_name]['total'] += 1
            if check.status:
                requirements[req_name]['passed'] += 1
            if check.risk_score >= 80:
                requirements[req_name]['high_risk'] += 1
        
        # 识别高风险项
        high_risk_items = [
            {
                'check_id': check.check_id,
                'description': check.description,
                'requirement': check.requirement.value,
                'risk_score': check.risk_score,
                'details': check.details
            }
            for check in self.checks 
            if check.risk_score >= 80
        ]
        
        return {
            'compliance_level': self.target_level.value,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'compliance_rate': round(compliance_rate, 2),
            'requirements_summary': requirements,
            'high_risk_items': high_risk_items,
            'recommendation': self._generate_recommendations(compliance_rate),
            'checked_at': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, compliance_rate: float) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if compliance_rate < 60:
            recommendations.append("系统安全合规性严重不足，需要立即进行全面安全整改")
        elif compliance_rate < 80:
            recommendations.append("系统安全合规性有待提升，建议优先处理高风险项")
        elif compliance_rate < 95:
            recommendations.append("系统安全合规性良好，建议完善剩余检查项")
        else:
            recommendations.append("系统安全合规性优秀，建议定期复查维持现状")
        
        # 基于高风险项添加具体建议
        high_risk_checks = [c for c in self.checks if c.risk_score >= 80]
        for check in high_risk_checks:
            if check.check_id == "AUTH_001":
                recommendations.append("加强密码策略，要求用户使用复杂密码")
            elif check.check_id == "NET_001":
                recommendations.append("升级SSL/TLS配置，使用更安全的加密套件")
            elif check.check_id == "DATA_001":
                recommendations.append("升级数据加密算法，使用更长的密钥长度")
        
        return recommendations


# 创建全局合规性管理器实例
compliance_manager = ComplianceManager(ComplianceLevel.LEVEL_3)