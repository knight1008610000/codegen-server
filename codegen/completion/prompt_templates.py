from typing import Dict, Any

CODE_COMPLETION_SYSTEM = """你是一个专业的代码补全助手。
根据上下文代码，补全光标处的代码。
只输出需要补全的代码，不要输出解释或其他内容。
保持代码风格与上下文一致。"""

CODE_COMPLETION_USER_TEMPLATE = """上下文代码:
```
{includes}
```

当前文件中的函数:
{functions}

待补全代码:
```
{prompt}▌{suffix}
```

请补全光标处的代码:"""


def build_code_completion_prompt(
    prompt: str,
    suffix: str,
    includes: list = None,
    other_functions: list = None
) -> Dict[str, Any]:
    """构建代码补全提示词"""
    includes = includes or []
    other_functions = other_functions or []

    includes_str = '\n'.join(includes[:10]) if includes else "无"

    functions_str = ""
    if other_functions:
        functions_list = []
        for func in other_functions[:5]:
            sig = func.get('signature', func.get('name', ''))
            if sig:
                functions_list.append(f"  {sig}")
        functions_str = '\n'.join(functions_list) if functions_list else "无"

    user_content = CODE_COMPLETION_USER_TEMPLATE.format(
        includes=includes_str,
        functions=functions_str,
        prompt=prompt,
        suffix=suffix
    )

    return {
        "messages": [
            {"role": "system", "content": CODE_COMPLETION_SYSTEM},
            {"role": "user", "content": user_content}
        ]
    }
