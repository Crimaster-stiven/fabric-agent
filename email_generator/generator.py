"""
邮件生成逻辑

调用 DeepSeek API 生成个性化开发邮件。
DeepSeek 兼容 OpenAI 接口格式。
"""

from typing import Optional
from openai import OpenAI
from email_generator.prompt_templates import SYSTEM_PROMPT, build_user_prompt


def _get_client(api_key: str) -> OpenAI:
    """创建 DeepSeek 客户端"""
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


def generate_email(
    api_key: str,
    brand_name: str,
    brand_type: str,
    fabrics_info: list[dict],
    company_info: Optional[dict] = None,
    model: str = "deepseek-chat",
    temperature: float = 0.4,
) -> str:
    """生成英文开发邮件

    Args:
        api_key: DeepSeek API Key
        brand_name: 品牌名称
        brand_type: 品牌类型
        fabrics_info: 匹配面料信息列表
        company_info: 公司信息
        model: 模型名称 (deepseek-chat / deepseek-reasoner)
        temperature: 生成温度 (0.0-1.0)

    Returns:
        str: 生成的邮件全文
    """
    client = _get_client(api_key)
    user_prompt = build_user_prompt(
        brand_name=brand_name,
        brand_type=brand_type,
        fabrics_info=fabrics_info,
        company_info=company_info,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=1500,
            temperature=temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"邮件生成失败: {e}")


def regenerate_email(
    api_key: str,
    previous_email: str,
    feedback: str = "",
    model: str = "deepseek-chat",
    temperature: float = 0.5,
) -> str:
    """基于反馈重新生成邮件

    Args:
        api_key: DeepSeek API Key
        previous_email: 上一版邮件内容
        feedback: 修改意见
        model: 模型名称
        temperature: 生成温度

    Returns:
        str: 重新生成的邮件
    """
    client = _get_client(api_key)

    prompt = f"""Below is a previously generated B2B outreach email for a fabric sourcing pitch.

{previous_email}

Please rewrite it based on this feedback: {feedback if feedback else "Make it more engaging and natural."}

Keep the same fabric recommendations and brand focus, but improve the tone, flow, and persuasiveness."""

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=1500,
            temperature=temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"邮件重新生成失败: {e}")
