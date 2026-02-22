from typing import Dict, Any, List, Optional

from .prompt_templates import build_code_completion_prompt
from .model_providers import (
    get_provider,
    BaseProvider,
    validate_model,
    get_default_model,
)

DEFAULT_MAX_TOKENS = 1000
DEFAULT_PROVIDER = "zhipu"


def validate_context(context: Dict[str, Any]) -> None:
    """验证 context 参数"""
    if not isinstance(context, dict):
        raise ValueError("context 必须是字典")

    prompt = context.get("prompt", "")
    suffix = context.get("suffix", "")

    if not isinstance(prompt, str):
        raise ValueError("context.prompt 必须是字符串")

    if not isinstance(suffix, str):
        raise ValueError("context.suffix 必须是字符串")

    includes = context.get("includes", [])
    if includes and not isinstance(includes, list):
        raise ValueError("context.includes 必须是数组")

    other_functions = context.get("other_functions", [])
    if other_functions and not isinstance(other_functions, list):
        raise ValueError("context.other_functions 必须是数组")


def call_chat_api(
    context: Dict[str, Any],
    model: str = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    provider: str = DEFAULT_PROVIDER,
) -> Dict[str, str]:
    """
    调用 Chat API 获取代码补全建议

    Args:
        context: 包含 prompt, suffix, includes, other_functions 的字典
        model: 模型名称 (可选，默认使用 provider 的默认模型)
        max_tokens: 最大 token 数
        provider: 模型提供者 (deepseek, openai, anthropic, zhipu)

    Returns:
        包含 text 和 model 的字典
    """
    validate_context(context)

    model = model or get_default_model(provider)
    validate_model(provider, model)

    prompt = context.get("prompt", "")
    suffix = context.get("suffix", "")
    includes = context.get("includes", [])
    other_functions = context.get("other_functions", [])

    prompt_data = build_code_completion_prompt(
        prompt=prompt, suffix=suffix, includes=includes, other_functions=other_functions
    )

    messages = prompt_data["messages"]

    provider_instance = get_provider(provider)

    response_text = provider_instance.chat(messages, model, max_tokens)

    return {"text": response_text, "model": model, "provider": provider}
