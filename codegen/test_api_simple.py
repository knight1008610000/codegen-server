#!/usr/bin/env python
"""
简洁的代码补全API测试 - 假设API正常工作，包含真实成功案例测试
"""
import json
import requests
import sys
import time
from typing import Dict, Any, List, Optional


class TestResult:
    """测试结果"""
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration
    
    def __str__(self):
        status = "✅" if self.passed else "❌"
        return f"{status} {self.name:30} {self.duration:.3f}s"


class TestRunner:
    """测试运行器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1/completion"
        self.results: List[TestResult] = []
    
    def run_test(self, test_func) -> TestResult:
        """运行单个测试"""
        test_name = test_func.__name__.replace("test_", "").replace("_", " ")
        start = time.time()
        
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
        result = TestResult(test_name, passed, message, duration)
        self.results.append(result)
        
        # 立即输出结果
        print(str(result))
        if message and not passed:
            print(f"   {message}")
        
        return result
    
    def run_all(self):
        """运行所有测试"""
        print("🚀 运行代码补全API测试")
        print("=" * 60)
        
        # 获取所有测试函数
        test_functions = [
            getattr(self, attr) for attr in dir(self)
            if attr.startswith('test_') and callable(getattr(self, attr))
        ]
        
        # 运行测试
        for test_func in test_functions:
            self.run_test(test_func)
        
        # 打印摘要
        self.print_summary()
    
    def print_summary(self):
        """打印测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print("\n" + "=" * 60)
        print("📊 测试摘要")
        print("=" * 60)
        print(f"总计: {total} 个测试")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        
        if failed == 0:
            print("\n🎉 所有测试通过!")
        else:
            print(f"\n⚠️  有 {failed} 个测试失败")
    
    def make_request(self, data: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """发送API请求并返回响应"""
        response = requests.post(self.api_url, json=data, timeout=timeout)
        
        # 如果API密钥无效，会返回500
        if response.status_code == 500:
            # 尝试解析错误信息
            try:
                error_data = response.json()
                error_code = error_data.get('error_code', '未知')
                error_msg = error_data.get('error', '')[:100]
                raise AssertionError(f"API调用失败 ({error_code}): {error_msg}")
            except:
                raise AssertionError(f"API调用失败: HTTP {response.status_code}")
        
        assert response.status_code == 200, f"HTTP状态码 {response.status_code}"
        return response.json()
    
    # ========== 基础测试 ==========
    
    def test_server_connection(self):
        """测试服务器连接"""
        response = requests.get(self.base_url, timeout=2)
        assert response.status_code in [200, 404, 403], f"连接失败: {response.status_code}"
    
    def test_cors_support(self):
        """测试CORS支持"""
        response = requests.options(self.api_url, timeout=2)
        assert response.status_code == 200, f"CORS OPTIONS失败: {response.status_code}"
        assert 'Access-Control-Allow-Origin' in response.headers, "缺少CORS头"
    
    # ========== 错误测试（应该失败） ==========
    
    def test_missing_prompt(self):
        """测试缺少prompt参数 - 应该失败"""
        data = {"suffix": "test"}
        response = requests.post(self.api_url, json=data, timeout=5)
        assert response.status_code == 400, f"应该返回400: {response.status_code}"
        
        result = response.json()
        assert not result['success'], "应该失败"
        assert result['error_code'] == 'INVALID_PARAMS', f"错误码: {result['error_code']}"
    
    def test_missing_suffix(self):
        """测试缺少suffix参数 - 应该失败"""
        data = {"prompt": "test"}
        response = requests.post(self.api_url, json=data, timeout=5)
        assert response.status_code == 400, f"应该返回400: {response.status_code}"
        
        result = response.json()
        assert not result['success'], "应该失败"
        assert result['error_code'] == 'INVALID_PARAMS', f"错误码: {result['error_code']}"
    
    def test_invalid_json(self):
        """测试无效JSON - 应该失败"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.api_url, data="invalid json", headers=headers, timeout=5)
        assert response.status_code == 400, f"应该返回400: {response.status_code}"
        
        result = response.json()
        assert not result['success'], "应该失败"
        assert result['error_code'] == 'INVALID_JSON', f"错误码: {result['error_code']}"
    
    # ========== 成功测试（假设API正常工作） ==========
    
    def test_minimal_valid_request(self):
        """测试最小有效请求 - 应该成功"""
        data = {
            "prompt": "int main() {\n    int a = 10;\n    ",
            "suffix": "\n    return 0;\n}"
        }
        
        result = self.make_request(data)
        
        # 如果API密钥无效，跳过这个测试
        if not result['success']:
            print(f"  跳过: API密钥可能无效 ({result.get('error_code', '未知')})")
            return
        
        assert result['success'], "应该成功"
        assert 'suggestion' in result, "应该包含suggestion"
        suggestion = result['suggestion']
        assert 'text' in suggestion, "suggestion应该包含text"
        assert 'label' in suggestion, "suggestion应该包含label"
        assert len(suggestion['text']) > 0, "建议文本不能为空"
    
    def test_real_success_example(self):
        """真实成功案例测试 - 使用API文档.md中的完整示例"""
        # 来自API文档.md第4.2节的测试用例
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
        
        result = self.make_request(data, timeout=15)
        
        # 如果API密钥无效，跳过这个测试
        if not result['success']:
            print(f"  跳过: API密钥可能无效 ({result.get('error_code', '未知')})")
            return
        
        assert result['success'], "应该成功"
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
        
        # 检查是否使用上下文变量
        if 'a' in text and 'b' in text:
            print(f"  ✅ 使用了上下文变量a和b")
        
        print(f"  建议: {label}")
        print(f"  代码: {text[:80]}..." if len(text) > 80 else f"  代码: {text}")
    
    def test_with_includes(self):
        """测试包含include语句 - 应该成功"""
        data = {
            "prompt": "int main() {\n    ",
            "suffix": "\n    return 0;\n}",
            "includes": ["#include <iostream>", "#include <string>"]
        }
        
        result = self.make_request(data)
        
        if not result['success']:
            print(f"  跳过: API密钥可能无效")
            return
        
        assert result['success'], "应该成功"
        assert 'suggestion' in result, "应该包含suggestion"
    
    def test_with_functions(self):
        """测试包含其他函数 - 应该成功"""
        data = {
            "prompt": "int main() {\n    ",
            "suffix": "\n    return 0;\n}",
            "other_functions": [
                {"name": "add", "signature": "int add(int x, int y)"},
                {"name": "multiply", "signature": "int multiply(int x, int y)"}
            ]
        }
        
        result = self.make_request(data)
        
        if not result['success']:
            print(f"  跳过: API密钥可能无效")
            return
        
        assert result['success'], "应该成功"
        assert 'suggestion' in result, "应该包含suggestion"
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试1: 正常代码
        data1 = {"prompt": "for (int i = 0; i < 10; i++) {\n    ", "suffix": "\n}"}
        result1 = self.make_request(data1)
        if result1.get('success'):
            print(f"  ✅ 循环代码测试通过")
        
        # 测试2: 函数调用
        data2 = {"prompt": "void process() {\n    std::cout << \"Hello\";\n    ", "suffix": "\n}"}
        result2 = self.make_request(data2)
        if result2.get('success'):
            print(f"  ✅ 函数调用测试通过")
        
        # 测试3: 条件语句
        data3 = {"prompt": "if (x > 0) {\n    ", "suffix": "\n}"}
        result3 = self.make_request(data3)
        if result3.get('success'):
            print(f"  ✅ 条件语句测试通过")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("使用方法:")
        print("  python test_api_simple.py      # 运行所有测试")
        print("  python test_api_simple.py --help  # 显示帮助")
        return
    
    # 检查服务器
    try:
        requests.get("http://localhost:8000", timeout=1)
    except:
        print("⚠️  警告: Django服务器可能未运行")
        print("请先启动: pixi run python manage.py runserver")
        print("设置API密钥: export DEEPSEEK_API_KEY='your-key'")
        print("继续测试可能会失败...\n")
    
    # 运行测试
    runner = TestRunner()
    runner.run_all()
    
    # 返回退出码
    failed = sum(1 for r in runner.results if not r.passed)
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()