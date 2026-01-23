import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import call_fim_api


def cors_exempt(view_func):
    """CORS装饰器（方案A）"""
    def wrapped_view(request, *args, **kwargs):
        if request.method == "OPTIONS":
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        response = view_func(request, *args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    return wrapped_view


@csrf_exempt
@cors_exempt
def completion(request):
    """代码补全接口"""
    try:
        # 解析请求
        data = json.loads(request.body)
        
        # 验证必填参数
        required_fields = ['prompt', 'suffix']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error_code': 'INVALID_PARAMS',
                    'error': f'缺少必填参数: {field}'
                }, status=400)
        
        prompt = data['prompt']
        suffix = data['suffix']
        includes = data.get('includes', [])
        other_functions = data.get('other_functions', [])
        max_tokens = data.get('max_tokens', 100)
        
        # 调用DeepSeek FIM API
        suggestion = call_fim_api(prompt, suffix, includes, other_functions, max_tokens)
        
        # 构造响应
        return JsonResponse({
            'success': True,
            'suggestion': suggestion
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error_code': 'INVALID_JSON',
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        error_msg = str(e)
        error_code = 'INTERNAL_ERROR'
        
        # 根据异常类型设置错误码
        if 'timeout' in error_msg.lower():
            error_code = 'API_TIMEOUT'
        elif 'connection' in error_msg.lower():
            error_code = 'API_CONNECTION_ERROR'
        elif 'LLM API' in error_msg:
            error_code = 'API_ERROR'
        
        return JsonResponse({
            'success': False,
            'error_code': error_code,
            'error': error_msg
        }, status=500)
