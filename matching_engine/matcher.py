"""
核心面料匹配算法

根据品牌类型，对面料进行评分排序，返回最匹配的 Top N 面料。
"""

from knowledge_base.fabric_loader import load_all_fabrics
from knowledge_base.brand_profiles import get_preferred_categories


def match_fabrics(
    brand_type: str,
    top_n: int = 5,
) -> list[dict]:
    """匹配最适合某品牌类型的面料

    算法：
    1. 获取该品牌类型的偏好面料类别权重映射
    2. 遍历所有面料，对每块面料的 category 匹配权重并计算总分
    3. 补充加分项：面料 suitable_brand_types 包含该品牌类型
    4. 按总分降序返回 Top N

    Args:
        brand_type: 品牌类型完整名称 (如 "户外 (Outdoor)")
        top_n: 返回前 N 条结果

    Returns:
        list[dict]: [
            {
                "fabric": DataFrame row dict,
                "score": int,
                "match_reason": str,
                "matched_categories": list[str],
            },
            ...
        ]
    """
    preferences = get_preferred_categories(brand_type)
    df = load_all_fabrics()

    results = []
    for _, row in df.iterrows():
        fabric = row.to_dict()
        category = fabric.get("category", "")
        suitable_types = fabric.get("suitable_brand_types_list", [])
        features_str = fabric.get("features", "")

        score = 0
        matched_categories = []

        # 1. 偏好权重匹配
        # 面料的 category 可能以逗号分隔多个类别
        for cat in [c.strip() for c in str(category).split(",")]:
            if cat in preferences:
                weight = preferences[cat]
                score += weight
                matched_categories.append(cat)

        # 2. 补充加分：suitable_brand_types 包含该类型
        brand_type_short = brand_type.split(" (")[0] if " (" in brand_type else brand_type
        if any(brand_type_short in st for st in suitable_types):
            score += 3

        # 3. 功能特点关键词加分
        # 提取品牌偏好中的关键词，在 features 中匹配到一项 +1
        keyword_map = {
            "户外": ["防晒", "防水", "防风", "透湿", "保暖", "轻量"],
            "运动休闲": ["弹力", "抗菌", "亲肤", "快干", "导湿", "凉感"],
            "时尚": ["环保", "防透", "轻薄", "色彩"],
            "童装": ["抗菌", "亲肤", "防晒", "柔软"],
            "工装": ["阻燃", "耐磨", "高强度", "防水"],
            "内衣家居": ["抗菌", "亲肤", "保暖", "柔软"],
        }

        for type_key, keywords in keyword_map.items():
            if type_key in brand_type:
                bonus = sum(1 for kw in keywords if kw in str(features_str))
                score += min(bonus, 3)  # 最多加 3 分
                break

        if score > 0:
            # 生成推荐理由
            match_reason = _generate_match_reason(
                fabric, brand_type, matched_categories, score
            )
            results.append({
                "fabric": fabric,
                "score": score,
                "match_reason": match_reason,
                "matched_categories": matched_categories,
            })

    # 按分数降序排列
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


def _generate_match_reason(
    fabric: dict,
    brand_type: str,
    matched_categories: list[str],
    score: int,
) -> str:
    """生成面料推荐理由"""
    brand_short = brand_type.split(" (")[0] if " (" in brand_type else brand_type
    categories_str = "、".join(matched_categories) if matched_categories else "功能匹配"
    name = fabric.get("name", "")
    features = fabric.get("features", "")

    return (
        f"该品牌为{brand_short}类型，{name}（{categories_str}）"
        f"在功能特性（{features}）上高度契合其产品需求，"
        f"适合用于该品牌的产品线开发。"
    )


def get_match_score_label(score: int, max_possible: int = 30) -> tuple[str, float]:
    """将分数转换为可读的匹配度标签和百分比"""
    ratio = min(score / max_possible, 1.0)
    if ratio >= 0.8:
        return "★★★★★", round(ratio * 100)
    elif ratio >= 0.6:
        return "★★★★☆", round(ratio * 100)
    elif ratio >= 0.4:
        return "★★★☆☆", round(ratio * 100)
    elif ratio >= 0.2:
        return "★★☆☆☆", round(ratio * 100)
    else:
        return "★☆☆☆☆", round(ratio * 100)
