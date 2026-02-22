# AGENTS.md - Code Completion Server Guide

## Project Overview
Django-based code completion API server for VSCode intelligent coding assistant plugin using DeepSeek FIM API.

## Quick Start
```bash
pixi install
export DEEPSEEK_API_KEY="your-api-key"
pixi run python manage.py migrate
pixi run python manage.py runserver
```

## Build/Test Commands

### Development
```bash
pixi run python manage.py check          # Check configuration
pixi run python manage.py runserver       # Run server
pixi run python manage.py runserver 8080 # Specific port
pixi run python manage.py makemigrations # Create migrations
pixi run python manage.py migrate        # Apply migrations
```

### Testing
```bash
pixi run python test_api_final.py        # Full test suite (recommended)
pixi run python test_api_simple.py       # Simplified tests
pixi run python test_api.py              # Original tests
pixi run python test_api.py test_name    # Run single test (e.g., test_missing_prompt)
pixi run python manage.py test           # Django tests
```

### Linting
```bash
pixi run python -m py_compile **/*.py    # Syntax check
pixi run python -m mypy .                # Type checking
pixi run python -m isort .               # Import sorting
pixi run python -m black .               # Code formatting
```

## Code Style

### Import Order
1. Standard library (`json`, `os`, `typing`)
2. Third-party (`requests`, `django.http`)
3. Django modules (`csrf_exempt`, `require_http_methods`)
4. Local modules (`from .services import ...`)

### Naming Conventions
- Functions/Variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_private_method`
- Database models: Singular nouns

### Type Hints (Required)
```python
def call_fim_api(
    prompt: str,
    suffix: str,
    includes: List[str],
    other_functions: List[Dict[str, Any]],
    max_tokens: int = 100
) -> Optional[Dict[str, str]]:
```

### Error Handling
```python
# Use specific exceptions
raise ValueError("prompt和suffix必须是字符串")

# Return consistent errors
return JsonResponse({
    'success': False,
    'error_code': 'INVALID_PARAMS',
    'error': f'缺少必填参数: {field}'
}, status=400)

# Handle API errors
try:
    response = requests.post(url, timeout=10)
except requests.exceptions.Timeout:
    raise Exception("LLM API调用超时")
```

### String Formatting
- Use f-strings: `f"错误: {field}"`
- Use triple quotes for long strings

## File Structure
```
codegen/
├── api/                  # Django project
│   ├── settings.py      # Settings
│   └── urls.py          # URL routing
├── completion/          # Main app
│   ├── views.py         # API views (@csrf_exempt, @cors_exempt)
│   ├── services.py      # DeepSeek API service
│   ├── urls.py          # Routes
│   └── models.py        # Database models
└── test_api_*.py        # Test suites
```

## API Specification
- **Endpoint**: `POST /api/v1/completion`
- **Required**: `prompt`, `suffix` (strings)
- **Optional**: `includes[]`, `other_functions[]`, `max_tokens` (default: 100)
- **Response**: `{"success": bool, "suggestion": {"text": str, "label": str}}`

## Constants
```python
MAX_TOTAL_LENGTH = 8000   # FIM API limit
MAX_INCLUDES = 10
MAX_FUNCTIONS = 5
MAX_PROMPT_LENGTH = 4000
MAX_SUFFIX_LENGTH = 4000
DEEPSEEK_MODEL = "deepseek-chat"
DEFAULT_MAX_TOKENS = 100
DEFAULT_TIMEOUT = 10
```

## Error Codes
| Code | Meaning |
|------|---------|
| INVALID_PARAMS | Missing required parameters |
| INVALID_JSON | Invalid JSON format |
| API_TIMEOUT | LLM API timeout |
| API_CONNECTION_ERROR | Cannot connect to LLM API |
| API_ERROR | LLM API error |
| INTERNAL_ERROR | Server internal error |

## Notes for AI Agents
- Use Chinese error messages
- Validate inputs before API calls
- Skip API tests gracefully when no valid key
- Always use type hints
- Use `@csrf_exempt` for POST endpoints
- Return consistent JSON error responses
- Test both success and error cases

## Testing Guidelines
1. Run basic tests before making changes
2. Run full test suite after changes
3. Test categories: Basic, Error, API (requires valid key)
4. Each test should be independent

---

*Updated: 2026-02-22*
