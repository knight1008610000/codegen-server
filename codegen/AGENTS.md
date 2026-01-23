# AGENTS.md - Code Completion Server Guide for AI Agents

## Project Overview
Django-based code completion API server for VSCode intelligent coding assistant plugin.

## Quick Start
```bash
# Setup
pixi install
export DEEPSEEK_API_KEY="your-api-key"

# Run
pixi run python manage.py migrate
pixi run python manage.py runserver
```

## Build/Test/Lint Commands

### Development Commands
```bash
# Check project configuration
pixi run python manage.py check

# Run development server
pixi run python manage.py runserver
pixi run python manage.py runserver 8080  # specific port

# Database operations
pixi run python manage.py makemigrations
pixi run python manage.py migrate

# Create superuser
pixi run python manage.py createsuperuser
```

### Testing Commands
```bash
# Run comprehensive test suite (recommended)
pixi run python test_api_final.py

# Run specific test categories
DEEPSEEK_API_KEY="valid-key" pixi run python test_api_final.py  # All tests
pixi run python test_api_final.py  # Basic + error tests only

# Run simplified test suite
pixi run python test_api_simple.py

# Run original test script
pixi run python test_api.py

# Run Django tests (currently no tests in completion/tests.py)
pixi run python manage.py test
pixi run python manage.py test completion

# Run single test file
pixi run python manage.py test completion.tests

# Test API directly
curl -X POST http://localhost:8000/api/v1/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "suffix": "test"}'
```

### Test Categories
1. **Basic Tests** (always run): Server connection, CORS support
2. **Error Tests** (always run): Parameter validation, error handling
3. **API Tests** (requires valid API key): Real API integration tests

### Linting & Code Quality
```bash
# Check for Python syntax errors
pixi run python -m py_compile **/*.py

# Type checking (if mypy is installed)
pixi run python -m mypy --ignore-missing-imports .

# Import sorting (if isort is installed)
pixi run python -m isort .

# Code formatting (if black is installed)
pixi run python -m black .
```

## Code Style Guidelines

### Import Order
```python
# 1. Standard library
import json
import os
import sys
from typing import Optional, Dict, List, Any, Tuple

# 2. Third-party libraries
import requests
from django.http import JsonResponse, HttpResponse

# 3. Django modules
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 4. Local modules
from .services import call_fim_api
from .models import CompletionRequest
```

### Naming Conventions
- **Functions/Variables**: `snake_case` (`call_fim_api`, `max_tokens`)
- **Classes**: `PascalCase` (`TestRunner`, `CodeCompletionView`)
- **Constants**: `UPPER_SNAKE_CASE` (`MAX_TOTAL_LENGTH`, `DEFAULT_TIMEOUT`)
- **Private members**: Single underscore prefix (`_private_method`)
- **Type variables**: `T`, `K`, `V` or descriptive names
- **Database models**: Singular nouns (`CompletionRequest`, `User`)
- **URL patterns**: `snake_case` with hyphens (`api/v1/completion`)

### Type Hints (Required)
```python
def call_fim_api(
    prompt: str,
    suffix: str,
    includes: List[str],
    other_functions: List[Dict[str, Any]],
    max_tokens: int = DEFAULT_MAX_TOKENS
) -> Optional[Dict[str, str]]:
    """Call DeepSeek FIM API for code completion."""
    # Implementation
```

### Error Handling
```python
# Use specific exception types
raise ValueError("prompt和suffix必须是字符串")

# Follow API error code规范
error_codes = {
    'INVALID_PARAMS': '请求参数缺失或格式错误',
    'INVALID_JSON': '无效的JSON格式',
    'API_TIMEOUT': 'LLM API调用超时',
    'API_CONNECTION_ERROR': '无法连接到LLM API',
    'API_ERROR': 'LLM API返回错误',
    'INTERNAL_ERROR': '服务器内部错误',
}

# Return consistent JSON error responses
return JsonResponse({
    'success': False,
    'error_code': 'INVALID_PARAMS',
    'error': f'缺少必填参数: {field}'
}, status=400)

# Use try-except for external API calls
try:
    response = requests.post(api_url, json=data, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
except requests.exceptions.Timeout:
    return JsonResponse({
        'success': False,
        'error_code': 'API_TIMEOUT',
        'error': 'LLM API调用超时'
    }, status=504)
except requests.exceptions.RequestException as e:
    return JsonResponse({
        'success': False,
        'error_code': 'API_CONNECTION_ERROR',
        'error': f'无法连接到LLM API: {str(e)}'
    }, status=502)
```

### String Formatting
```python
# Use f-strings
error_msg = f"缺少必填参数: {field_name}"

# Avoid concatenation
# Bad: error_msg = "缺少必填参数: " + field_name

# Use triple quotes for long strings
prompt_text = f"""
请根据以下上下文补全代码：

{prompt}

{suffix}
"""
```

### Documentation
```python
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process input data for API consumption.
    
    Args:
        data: Raw input data dictionary
        
    Returns:
        Processed data dictionary
        
    Raises:
        ValueError: If data is invalid
        TypeError: If data types are incorrect
        
    Examples:
        >>> process_data({"prompt": "def test():"})
        {"prompt": "def test():", "suffix": ""}
    """
    # Implementation
```

### Django-Specific Guidelines
```python
# Use class-based views for complex logic
from django.views import View

class CompletionView(View):
    def post(self, request):
        # Handle POST request
        pass

# Use function-based views for simple endpoints
@csrf_exempt
@require_http_methods(["POST"])
def completion(request):
    # Simple endpoint logic
    pass

# Use Django's JsonResponse for API responses
from django.http import JsonResponse
return JsonResponse({"success": True, "data": result})

# Validate data before processing
if not request.body:
    return JsonResponse({
        'success': False,
        'error_code': 'INVALID_JSON',
        'error': '请求体为空'
    }, status=400)
```

## File Structure
```
codegen/
├── api/                    # Django project
│   ├── settings.py        # Project settings
│   ├── urls.py           # URL routing
│   └── ...
├── completion/            # Completion app
│   ├── views.py          # API views (@csrf_exempt, @cors_exempt)
│   ├── services.py       # DeepSeek API service (call_fim_api)
│   ├── urls.py          # App routes (/completion)
│   ├── models.py        # Database models
│   ├── tests.py         # Django tests
│   └── ...
├── test_api_final.py     # Comprehensive test suite
├── test_api_simple.py    # Simplified tests
├── test_api.py          # Original test script
└── AGENTS.md           # This file
```

## API Specification
- **Endpoint**: `POST /api/v1/completion`
- **Required**: `prompt`, `suffix` (strings)
- **Optional**: `includes[]`, `other_functions[]`, `max_tokens` (default: 100)
- **Response**: `{"success": bool, "suggestion": {"text": str, "label": str}}`
- **Errors**: Consistent error codes with Chinese messages

## Constants (Hardcoded)
```python
# completion/services.py
MAX_TOTAL_LENGTH = 8000    # FIM API total length limit
MAX_INCLUDES = 10          # Max include statements
MAX_FUNCTIONS = 5          # Max function signatures
MAX_PROMPT_LENGTH = 4000   # Max prompt length
MAX_SUFFIX_LENGTH = 4000   # Max suffix length
DEEPSEEK_MODEL = "deepseek-chat"
DEFAULT_MAX_TOKENS = 100
DEFAULT_TIMEOUT = 10
```

## Development Workflow
1. Set `DEEPSEEK_API_KEY` environment variable
2. Run `pixi run python manage.py check`
3. Write code following style guidelines
4. Run tests: `pixi run python test_api_final.py`
5. Commit with descriptive messages

## Notes for AI Agents
- Assume API works correctly when testing with valid API key
- Use Chinese error messages as per API documentation
- Hardcode constants as shown in `services.py`
- Implement CORS via decorator (see `views.py`)
- Validate all inputs before calling external APIs
- Skip API tests gracefully when no valid API key
- Always use type hints for function signatures
- Follow Django best practices for views and models
- Use `@csrf_exempt` for API endpoints that accept POST requests
- Return consistent JSON error responses with appropriate HTTP status codes
- Test both success and error cases
- Document complex logic with clear comments

## Testing Guidelines for Agents
1. **Before making changes**: Run basic tests to ensure system is working
2. **After making changes**: Run comprehensive test suite
3. **When adding features**: Add corresponding tests
4. **Test categories to always run**: Basic + Error tests
5. **API tests**: Only run with valid API key, skip gracefully otherwise
6. **Test isolation**: Each test should be independent
7. **Cleanup**: Tests should not leave side effects

---

*Updated: 2026-01-23*