"""
品牌类型识别

策略：
1. 先在内置品牌映射表中查找（不区分大小写）
2. 未匹配到则调用 DeepSeek API 分析
3. 允许手动指定兜底
"""

from typing import Optional
from openai import OpenAI
from knowledge_base.brand_profiles import lookup_brand, get_all_brand_types


def identify_brand_type(
    brand_name: str,
    use_llm: bool = False,
    api_key: Optional[str] = None,
    model: str = "deepseek-chat",
) -> dict:
    """识别品牌类型

    Args:
        brand_name: 品牌名称
        use_llm: 是否允许使用 LLM 兜底识别
        api_key: DeepSeek API Key
        model: 使用的模型

    Returns:
        dict: {"brand_type": "完整品牌类型名称" or None,
               "source": "local" or "llm" or "manual",
               "confidence": "high" or "medium" or "low"}
    """
    # 1. 本地映射表查找
    result = lookup_brand(brand_name)
    if result:
        return {
            "brand_type": result,
            "source": "local",
            "confidence": "high",
        }

    # 2. 如果允许 LLM 兜底
    if use_llm and api_key:
        return _analyze_with_llm(brand_name, api_key, model)

    return {
        "brand_type": None,
        "source": None,
        "confidence": "low",
    }


def _analyze_with_llm(
    brand_name: str, api_key: str, model: str = "deepseek-chat"
) -> dict:
    """调用 DeepSeek API 分析品牌类型"""
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    brand_types_list = get_all_brand_types()
    brand_types_str = ", ".join(brand_types_list)

    prompt = f"""You are a fashion and sportswear industry expert.

A user has entered the brand name: "{brand_name}"

Based on your knowledge of global apparel brands, classify this brand into ONE of the following categories:

{brand_types_str}

Rules:
- If the brand is an outdoor/performance brand → choose "户外 (Outdoor)"
- If the brand is sportswear/activewear/athleisure → choose "运动休闲 (Athleisure)"
- If the brand is fast fashion → choose "时尚快消 (Fast Fashion)"
- If the brand is childrenswear → choose "童装 (Childrenswear)"
- If the brand is workwear/protective → choose "工装/防护 (Workwear)"
- If the brand is intimate apparel/homewear → choose "内衣/家居 (Intimate & Home)"

Respond with ONLY the category name, nothing else. If you genuinely don't know, respond with "unknown"."""

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=50,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        result = response.choices[0].message.content.strip()
        # 验证返回结果是否有效
        all_types = get_all_brand_types()
        if result in all_types:
            return {
                "brand_type": result,
                "source": "llm",
                "confidence": "medium",
            }
        return {
            "brand_type": None,
            "source": "llm",
            "confidence": "low",
        }
    except Exception:
        return {
            "brand_type": None,
            "source": "llm",
            "confidence": "low",
        }
