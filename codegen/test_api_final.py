#!/usr/bin/env python
"""
代码补全API测试 - 完整测试套件

注意：要运行所有测试，需要有效的DeepSeek API密钥。
设置环境变量：export DEEPSEEK_API_KEY="your-api-key"

测试分类：
1. 基础测试：不需要API密钥（总是运行）
2. 错误测试：测试错误处理（总是运行）
3. API测试：需要有效的API密钥（如果API密钥无效则跳过）
"""
import json
import requests
import sys
import time
import os
from typing import Dict, Any, List


class TestCategory:
    """测试分类"""
    BASIC = "basic"      # 基础测试，总是运行
    ERROR = "error"      # 错误测试，总是运行  
    API = "api"          # API测试，需要有效密钥


class TestResult:
    """测试结果"""
    def __init__(self, name: str, category: str, passed: bool, 
                 message: str = "", duration: float = 0.0):
        self.name = name
        self.category = category
        self.passed = passed
        self.message = message
        self.duration = duration
    
    def __str__(self):
        status = "✅" if self.passed else "❌"
        return f"{status} {self.name:35} {self.duration:.3f}s"


class TestRunner:
    """测试运行器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1/completion"
        self.results: List[TestResult] = []
        self.has_valid_api_key = self.check_api_key()
    
    def check_api_key(self) -> bool:
        """检查是否有有效的API密钥"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key or api_key == "test-key":
            print("⚠️  警告: 使用测试API密钥或未设置API密钥")
            print("   API测试将被跳过")
            print("   设置有效密钥: export DEEPSEEK_API_KEY='your-real-key'")
            return False
        return True
    
    def run_test(self, test_func, category: str = TestCategory.BASIC) -> TestResult:
        """运行单个测试"""
        test_name = test_func.__name__.replace("test_", "").replace("_", " ")
        start = time.time()
        
        # 检查是否需要跳过API测试
        if category == TestCategory.API and not self.has_valid_api_key:
            result = TestResult(test_name, category, True, "跳过（无有效API密钥）", 0.0)
            self.results.append(result)
            print(f"⏭️  {test_name:35} 0.000s")
            print(f"   跳过: 需要有效的DeepSeek API密钥")
            return result
        
        try:
            test_func()
            passed = True
            message = "通过"
        except AssertionError as e:
            passed = False
            message = str(e)
        except Exception as e:
            passed = False
            message = f"错误: {str(e)}"
        
        duration = time.time() - start
        result = TestResult(test_name, category, passed, message, duration)
        self.results.append(result)
        
        # 立即输出结果
        print(str(result))
        if message and not passed:
            print(f"    {message}")
        
        return result
    
    def run_all(self):
        """运行所有测试"""
        print("🚀 代码补全API测试套件")
        print("=" * 70)
        
        if self.has_valid_api_key:
            print("✅ 检测到有效的API密钥，将运行所有测试")
        else:
            print("⚠️  未检测到有效的API密钥，API测试将被跳过")
        
        print()
        
        # 按分类运行测试
        categories = {
            "基础测试": TestCategory.BASIC,
            "错误测试": TestCategory.ERROR, 
            "API测试": TestCategory.API
        }
        
        for category_name, category_type in categories.items():
            print(f"\n📋 {category_name}")
            print("-" * 40)
            
            # 获取该分类的所有测试函数
            test_functions = []
            for attr in dir(self):
                if attr.startswith('test_'):
                    func = getattr(self, attr)
                    if callable(func):
                        # 从函数名推断分类
                        if category_type == TestCategory.BASIC and 'basic' in attr:
                            test_functions.append((attr, func))
                        elif category_type == TestCategory.ERROR and 'error' in attr:
                            test_functions.append((attr, func))
                        elif category_type == TestCategory.API and 'api' in attr:
                            test_functions.append((attr, func))
            
            # 运行该分类的测试
            for attr, func in sorted(test_functions):
                self.run_test(func, category_type)
        
        # 打印摘要
        self.print_summary()
    
    def print_summary(self):
        """打印测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print("\n" + "=" * 70)
        print("📊 测试摘要")
        print("=" * 70)
        print(f"总计: {total} 个测试")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        
        # 按分类统计
        for category in [TestCategory.BASIC, TestCategory.ERROR, TestCategory.API]:
            category_tests = [r for r in self.results if r.category == category]
            if category_tests:
                category_passed = sum(1 for r in category_tests if r.passed)
                category_name = {
                    TestCategory.BASIC: "基础测试",
                    TestCategory.ERROR: "错误测试",
                    TestCategory.API: "API测试"
                }[category]
                print(f"  {category_name}: {category_passed}/{len(category_tests)} 通过")
        
        if failed == 0:
            print("\n🎉 所有测试通过!")
        else:
            print(f"\n⚠️  有 {failed} 个测试失败")
    
    def make_api_request(self, data: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """发送API请求"""
        response = requests.post(self.api_url, json=data, timeout=timeout)
        assert response.status_code == 200, f"HTTP状态码 {response.status_code}"
        return response.json()
    
    # ========== 基础测试 ==========
    
    def test_basic_server_connection(self):
        """测试服务器连接"""
        response = requests.get(self.base_url, timeout=2)
        assert response.status_code in [200, 404, 403], f"连接失败"
    
    def test_basic_cors_support(self):
        """测试CORS支持"""
        response = requests.options(self.api_url, timeout=2)
        assert response.status_code == 200, f"CORS OPTIONS失败"
        assert 'Access-Control-Allow-Origin' in response.headers, "缺少CORS头"
    
    # ========== 错误测试 ==========
    
    def test_error_missing_prompt(self):
        """测试缺少prompt参数"""
        data = {"suffix": "test"}
        response = requests.post(self.api_url, json=data, timeout=5)
        assert response.status_code == 400, f"应该返回400"
        
        result = response.json()
        assert not result['success'], "应该失败"
        assert result['error_code'] == 'INVALID_PARAMS', f"错误码不正确"
        assert "缺少必填参数" in result['error'], f"错误消息不正确"
    
    def test_error_missing_suffix(self):
        """测试缺少suffix参数"""
        data = {"prompt": "test"}
        response = requests.post(self.api_url, json=data, timeout=5)
        assert response.status_code == 400, f"应该返回400"
        
        result = response.json()
        assert not result['success'], "应该失败"
        assert result['error_code'] == 'INVALID_PARAMS', f"错误码不正确"
    
    def test_error_invalid_json(self):
        """测试无效JSON"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.api_url, data="invalid json", headers=headers, timeout=5)
        assert response.status_code == 400, f"应该返回400"
        
        result = response.json()
        assert not result['success'], "应该失败"
        assert result['error_code'] == 'INVALID_JSON', f"错误码不正确"
        assert "无效的JSON格式" in result['error'], f"错误消息不正确"
    
    def test_error_empty_strings(self):
        """测试空字符串参数"""
        data = {"prompt": "", "suffix": ""}
        response = requests.post(self.api_url, json=data, timeout=5)
        
        # 空字符串应该导致错误
        assert response.status_code in [400, 500], f"应该返回400或500"
        
        result = response.json()
        assert not result['success'], "应该失败"
    
    # ========== API测试（需要有效密钥） ==========
    
    def test_api_minimal_request(self):
        """测试最小有效请求"""
        data = {
            "prompt": "int main() {\n    int a = 10;\n    ",
            "suffix": "\n    return 0;\n}"
        }
        
        result = self.make_api_request(data)
        assert result['success'], "API调用应该成功"
        assert 'suggestion' in result, "应该包含suggestion"
        
        suggestion = result['suggestion']
        assert 'text' in suggestion, "suggestion应该包含text"
        assert 'label' in suggestion, "suggestion应该包含label"
        assert len(suggestion['text']) > 0, "建议文本不能为空"
        
        print(f"    获得建议: {suggestion['label']}")
    
    def test_api_real_example(self):
        """真实成功案例测试 - API文档.md中的完整示例"""
        data = {
            "prompt": "int main() {\n    int a = 10;\n    int b = 20;\n    ",
            "suffix": "\n    return 0;\n}",
            "includes": ["#include <iostream>", "#include <vector>"],
            "other_functions": [
                {
                    "name": "calculate_sum",
                    "signature": "int calculate_sum(int a, int b)",
                    "return_type": "int",
                    "parameters": [
                        {"name": "a", "type": "int"},
                        {"name": "b", "type": "int"}
                    ]
                },
                {
                    "name": "calculate_product",
                    "signature": "int calculate_product(int a, int b)",
                    "return_type": "int",
                    "parameters": [
                        {"name": "a", "type": "int"},
                        {"name": "b", "type": "int"}
                    ]
                }
            ],
            "max_tokens": 100
        }
        
        result = self.make_api_request(data, timeout=15)
        assert result['success'], "API调用应该成功"
        assert 'suggestion' in result, "应该包含suggestion"
        
        suggestion = result['suggestion']
        text = suggestion['text']
        label = suggestion['label']
        
        # 基本验证
        assert len(text) > 0, "建议文本不能为空"
        assert len(label) > 0, "建议标签不能为空"
        
        # 验证是有效的C++代码
        assert any(c in text for c in [';', '=', '+', '-', '*', '/']), \
            f"应该包含C++语法: {text[:50]}..."
        
        # 输出结果
        print(f"    建议标签: {label}")
        print(f"    建议代码: {text[:80]}..." if len(text) > 80 else f"    建议代码: {text}")
        
        # 检查是否使用上下文变量
        if 'a' in text and 'b' in text:
            print(f"    ✅ 使用了上下文变量a和b")
        
        # 检查建议相关性
        if any(keyword in text.lower() for keyword in ['sum', 'add', '+', 'product', '*']):
            print(f"    ✅ 建议与计算相关")
    
    def test_api_with_includes(self):
        """测试包含include语句"""
        data = {
            "prompt": "int main() {\n    ",
            "suffix": "\n    return 0;\n}",
            "includes": ["#include <iostream>", "#include <string>", "#include <vector>"]
        }
        
        result = self.make_api_request(data)
        assert result['success'], "API调用应该成功"
        assert 'suggestion' in result, "应该包含suggestion"
        print(f"    包含{len(data['includes'])}个include语句")
    
    def test_api_with_functions(self):
        """测试包含其他函数"""
        data = {
            "prompt": "int main() {\n    ",
            "suffix": "\n    return 0;\n}",
            "other_functions": [
                {"name": "add", "signature": "int add(int x, int y)"},
                {"name": "multiply", "signature": "int multiply(int x, int y)"},
                {"name": "print_result", "signature": "void print_result(int value)"}
            ]
        }
        
        result = self.make_api_request(data)
        assert result['success'], "API调用应该成功"
        assert 'suggestion' in result, "应该包含suggestion"
        print(f"    包含{len(data['other_functions'])}个函数签名")
    
    def test_api_edge_cases(self):
        """测试边界情况"""
        test_cases = [
            ("循环", "for (int i = 0; i < 10; i++) {\n    ", "\n}"),
            ("条件语句", "if (x > 0) {\n    ", "\n}"),
            ("函数调用", "void process() {\n    std::cout << \"Hello\";\n    ", "\n}"),
            ("变量声明", "int main() {\n    double value = 3.14;\n    ", "\n}")
        ]
        
        for name, prompt, suffix in test_cases:
            data = {"prompt": prompt, "suffix": suffix}
            try:
                result = self.make_api_request(data, timeout=5)
                if result['success']:
                    print(f"    ✅ {name}测试通过")
                else:
                    print(f"    ❌ {name}测试失败")
            except:
                print(f"    ❌ {name}测试错误")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        return
    
    # 检查服务器
    try:
        requests.get("http://localhost:8000", timeout=1)
        print("✅ 服务器正在运行")
    except:
        print("❌ 错误: Django服务器未运行")
        print("   请先启动: pixi run python manage.py runserver")
        print("   然后重新运行测试")
        sys.exit(1)
    
    # 运行测试
    runner = TestRunner()
    runner.run_all()
    
    # 返回退出码
    failed = sum(1 for r in runner.results if not r.passed)
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()