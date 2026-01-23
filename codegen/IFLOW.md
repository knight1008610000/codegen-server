# Codegen Server 项目文档

## 项目概述

这是一个基于 Django 6.0 的代码补全 API 服务器，为 VSCode 智能编码助手插件提供后端服务。项目使用 Python 3.14 和 DeepSeek FIM API 构建，实现了基于 Fill-In-Middle (FIM) 技术的智能代码补全功能。

### 主要技术栈

- **后端框架**: Django 6.0
- **Python 版本**: 3.14.1
- **依赖管理**: Pixi (conda-forge)
- **数据库**: SQLite3
- **LLM 集成**: DeepSeek FIM API (deepseek-chat 模型)
- **HTTP 客户端**: requests 2.32.5

### 项目结构

```
codegen/
├── api/                    # Django 项目配置目录
│   ├── settings.py        # Django 设置
│   ├── urls.py           # 主 URL 配置
│   ├── wsgi.py           # WSGI 配置
│   ├── asgi.py           # ASGI 配置
│   └── __pycache__/      # Python 缓存
├── completion/            # 代码补全应用
│   ├── views.py          # API 视图函数
│   ├── services.py       # DeepSeek API 服务
│   ├── urls.py          # 应用 URL 配置
│   ├── models.py        # 数据模型（当前为空）
│   ├── admin.py         # 管理后台配置
│   ├── apps.py          # 应用配置
│   ├── tests.py         # 测试文件
│   ├── __init__.py      # 包初始化
│   └── migrations/      # 数据库迁移文件
├── manage.py             # Django 管理脚本
├── start.sh             # 快速启动脚本
├── test_api.py          # API 测试框架
├── API文档.md           # 完整 API 文档
├── AGENTS.md            # 开发指南
├── 部署指南.md          # 部署说明
└── db.sqlite3           # SQLite 数据库文件
```

## 构建和运行

### 环境设置

使用 Pixi 管理项目环境：

```bash
# 安装依赖并创建环境
pixi install

# 激活环境
pixi shell
```

### 环境变量配置

```bash
# 必需：DeepSeek API 密钥
export DEEPSEEK_API_KEY="your-api-key"

# 可选：自定义 API 端点
export DEEPSEEK_BASE_URL="https://api.deepseek.com/beta"
export DEEPSEEK_TIMEOUT=10
```

### Django 管理命令

```bash
# 进入项目目录
cd /home/niclas/codegen-server/codegen

# 检查项目配置
pixi run python manage.py check

# 运行开发服务器（默认端口 8000）
pixi run python manage.py runserver

# 指定端口运行
pixi run python manage.py runserver 8080

# 创建数据库迁移
pixi run python manage.py makemigrations

# 应用数据库迁移
pixi run python manage.py migrate

# 创建超级用户（用于管理后台）
pixi run python manage.py createsuperuser

# 运行测试
pixi run python manage.py test

# 启动交互式 Python shell
pixi run python manage.py shell
```

### 快速启动

使用提供的启动脚本：

```bash
# 确保已设置 DEEPSEEK_API_KEY 环境变量
export DEEPSEEK_API_KEY="your-api-key"

# 运行启动脚本
bash start.sh
```

### API 测试

```bash
# 运行完整的测试套件
pixi run python test_api.py

# 运行特定测试
pixi run python test_api.py test_server_connection

# 查看测试帮助
pixi run python test_api.py --help
```

## 开发约定

### 应用结构

- 每个 Django 应用应包含标准文件：`models.py`, `views.py`, `urls.py`, `admin.py`, `apps.py`, `tests.py`
- 应用配置类继承自 `AppConfig`，并设置 `name` 属性

### 代码风格

#### 1. 导入顺序
```python
# 1. 标准库
import json
import os
from typing import Optional, Dict, List

# 2. 第三方库
import requests
from django.http import JsonResponse

# 3. Django 模块
from django.views.decorators.csrf import csrf_exempt

# 4. 本地模块
from .services import call_fim_api
```

#### 2. 命名约定
- **函数/变量**: `snake_case` (例如: `call_fim_api`, `max_tokens`)
- **类**: `PascalCase` (例如: `CodeCompletionView`)
- **常量**: `UPPER_SNAKE_CASE` (例如: `MAX_TOTAL_LENGTH`, `DEFAULT_TIMEOUT`)
- **私有成员**: 前缀单下划线 `_private_method`

#### 3. 类型提示
```python
def call_fim_api(
    prompt: str, 
    suffix: str, 
    includes: List[str],
    other_functions: List[Dict[str, Any]],
    max_tokens: int
) -> Optional[Dict[str, str]]:
    """函数文档字符串"""
    # 函数体
```

#### 4. 错误处理
- 使用具体的异常类型
- 提供有意义的错误消息（中文）
- 遵循 API 文档中的错误码规范
- 记录异常但不暴露内部细节

#### 5. 字符串格式化
```python
# 推荐：f-string
error_msg = f"缺少必填参数: {field_name}"

# 避免：字符串拼接
error_msg = "缺少必填参数: " + field_name
```

### URL 路由

- 主路由配置在 `api/urls.py`
- 应用级路由在各自应用的 `urls.py` 中
- 使用 `path()` 函数定义路由，使用 `include()` 包含其他 URLconf
- 路由命名使用 `name` 参数

### 开发环境配置

- 当前使用开发模式（`DEBUG = True`）
- 数据库使用 SQLite，文件位于 `codegen/db.sqlite3`
- 时区设置为 UTC
- 语言设置为英语（en-us）
- 启用国际化和时区支持

## 当前功能

### API 端点

#### 代码补全接口

- **URL**: `POST /api/v1/completion`
- **Content-Type**: `application/json`
- **认证**: 无（MVP 版本）

**请求参数**:
```json
{
  "prompt": "string (必填) - 光标之前的代码",
  "suffix": "string (必填) - 光标之后的代码",
  "includes": ["string数组 (可选) - include语句列表"],
  "other_functions": ["对象数组 (可选) - 其他函数签名"],
  "max_tokens": "integer (可选，默认100) - 最大生成token数"
}
```

**成功响应**:
```json
{
  "success": true,
  "suggestion": {
    "text": "生成的代码",
    "label": "简短标签"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error_code": "错误码",
  "error": "错误描述"
}
```

**错误码定义**:
| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| INVALID_PARAMS | 400 | 请求参数缺失或格式错误 |
| INVALID_JSON | 400 | JSON格式无效 |
| API_TIMEOUT | 500 | LLM API调用超时 |
| API_CONNECTION_ERROR | 500 | 无法连接到LLM API |
| API_ERROR | 500 | LLM API返回错误 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 核心功能模块

#### 1. 视图层 (`completion/views.py`)

- `completion()`: 代码补全接口主视图
- `cors_exempt()`: CORS 装饰器，处理跨域请求
- 请求参数验证（prompt、suffix 必填）
- 错误处理和响应格式化

#### 2. 服务层 (`completion/services.py`)

- `call_fim_api()`: 调用 DeepSeek FIM API 的核心函数
- 数据验证和类型检查
- Prompt 优化和构造（包含 include 和函数签名）
- 长度限制和自动截断
- 响应解析和清理
- 完整的错误处理

#### 3. 测试框架 (`test_api.py`)

- 类似 cargo test 的测试系统
- 测试分类：单元测试、集成测试、错误测试、边界测试
- 自动化测试运行器
- 详细的测试报告和摘要
- 支持运行特定测试

### API 端点

- `/api/v1/completion` - 代码补全接口
- `/admin/` - Django 管理后台

## 依赖项

主要依赖（来自 pixi.toml）：

- `django` >= 6.0, < 7
- `requests` >= 2.31, < 3
- `llama-index` >= 0.12.52, < 0.13
- `django-stubs` >= 5.2.8, < 6

Pixi 配置（来自 pixi.toml）：

- `python` >= 3.14.1, < 3.15
- `pip` >= 25.3, < 26

## 数据库迁移

当前 `completion` 应用没有定义数据模型，`models.py` 为空。如需添加数据模型，需要：

1. 在 `completion/models.py` 中定义模型
2. 运行 `python manage.py makemigrations completion` 创建迁移文件
3. 运行 `python manage.py migrate` 应用迁移

## 注意事项

- **API 密钥安全**: 永远不要将 `DEEPSEEK_API_KEY` 提交到版本控制
- **生产环境**: 当前使用开发密钥，生产环境需要更改 `SECRET_KEY` 并关闭 `DEBUG` 模式
- **数据库文件**: `db.sqlite3` 已被 Git 忽略，需要通过迁移重新创建
- **Python 缓存**: `__pycache__/` 目录已被忽略
- **CORS 配置**: 当前允许所有来源（`*`），生产环境应限制具体域名
- **超时设置**: DeepSeek API 调用默认超时时间为 10 秒
- **输入验证**: 所有用户输入都经过验证和清理
- **错误处理**: 不暴露内部错误细节给客户端

## 相关文档

- [API文档.md](./API文档.md) - 完整的 API 规范和使用示例
- [AGENTS.md](./AGENTS.md) - 开发指南和代码风格规范
- [部署指南.md](./部署指南.md) - 部署和运维说明

## 常见问题

### Q: 启动时提示 "DEEPSEEK_API_KEY 未设置"
A: 设置环境变量：`export DEEPSEEK_API_KEY="your-api-key"`

### Q: API 返回 500 错误
A: 检查 Django 服务器日志，查看具体错误信息

### Q: 如何添加新的 API 端点？
A:
1. 在 `completion/views.py` 中添加新视图函数
2. 在 `completion/urls.py` 中添加路由
3. 添加相应的测试

### Q: 如何修改 DeepSeek API 配置？
A: 修改 `completion/services.py` 中的硬编码常量（`DEEPSEEK_API_URL`, `DEEPSEEK_MODEL`, `DEFAULT_TIMEOUT`）

### Q: 测试失败怎么办？
A: 确保服务器正在运行，API 密钥已正确设置，网络连接正常

---

*最后更新: 2025-01-22*