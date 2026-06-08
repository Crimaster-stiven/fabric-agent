"""
品牌类型画像 & 匹配规则

定义各品牌类型对应的面料偏好权重，
以及常见品牌 → 品牌类型的映射表。
"""

from typing import Optional

# ============================================================
# 品牌类型 → 面料类别权重映射
# ============================================================
# 权重值范围 1-10，越高代表该类型品牌越看重这类面料
BRAND_TYPE_PREFERENCES = {
    "户外 (Outdoor)": {
        "防晒类": 10,
        "防晒防透类": 10,
        "防水透湿类": 10,
        "保暖类": 8,
        "导湿速干类": 8,
        "弹力类": 4,
        "弹力亲肤类": 4,
        "防透类": 4,
        "环保再生类": 3,
        "凉感导湿类": 3,
    },
    "运动休闲 (Athleisure)": {
        "弹力类": 10,
        "弹力亲肤类": 10,
        "凉感类": 8,
        "凉感导湿类": 8,
        "导湿速干类": 8,
        "抗菌亲肤类": 8,
        "防晒类": 5,
        "防透类": 4,
        "环保再生类": 4,
    },
    "时尚快消 (Fast Fashion)": {
        "环保再生类": 8,
        "防透类": 6,
        "抗菌亲肤类": 6,
        "凉感类": 4,
        "弹力类": 3,
        "弹力亲肤类": 3,
        "防晒类": 3,
    },
    "童装 (Childrenswear)": {
        "抗菌亲肤类": 10,
        "防晒类": 8,
        "防晒防透类": 8,
        "导湿速干类": 6,
        "弹力亲肤类": 6,
        "环保再生类": 4,
        "保暖类": 3,
    },
    "工装/防护 (Workwear)": {
        "阻燃类": 10,
        "防水透湿类": 8,
        "弹力类": 4,
        "保暖类": 3,
    },
    "内衣/家居 (Intimate & Home)": {
        "抗菌亲肤类": 10,
        "弹力亲肤类": 8,
        "保暖类": 8,
        "环保再生类": 6,
        "凉感类": 4,
    },
}

# ============================================================
# 品牌 → 品牌类型映射表
# 常见海外服装/运动/户外品牌归类
# ============================================================
BRAND_TYPE_MAP = {
    # --- 户外品牌 ---
    "patagonia": "户外 (Outdoor)",
    "the north face": "户外 (Outdoor)",
    "arc'teryx": "户外 (Outdoor)",
    "columbia": "户外 (Outdoor)",
    "marmot": "户外 (Outdoor)",
    "mountain hardwear": "户外 (Outdoor)",
    "black diamond": "户外 (Outdoor)",
    "salomon": "户外 (Outdoor)",
    "helly hansen": "户外 (Outdoor)",
    "berghaus": "户外 (Outdoor)",
    "rab": "户外 (Outdoor)",
    "outdoor research": "户外 (Outdoor)",
    "north face": "户外 (Outdoor)",
    "arcteryx": "户外 (Outdoor)",

    # --- 运动休闲 ---
    "lululemon": "运动休闲 (Athleisure)",
    "nike": "运动休闲 (Athleisure)",
    "adidas": "运动休闲 (Athleisure)",
    "under armour": "运动休闲 (Athleisure)",
    "puma": "运动休闲 (Athleisure)",
    "reebok": "运动休闲 (Athleisure)",
    "sweaty betty": "运动休闲 (Athleisure)",
    "gymshark": "运动休闲 (Athleisure)",
    "alo yoga": "运动休闲 (Athleisure)",
    "vuori": "运动休闲 (Athleisure)",
    "rhone": "运动休闲 (Athleisure)",
    "outdoor voices": "运动休闲 (Athleisure)",
    "new balance": "运动休闲 (Athleisure)",
    "asics": "运动休闲 (Athleisure)",

    # --- 时尚快消 ---
    "zara": "时尚快消 (Fast Fashion)",
    "h&m": "时尚快消 (Fast Fashion)",
    "uniqlo": "时尚快消 (Fast Fashion)",
    "mango": "时尚快消 (Fast Fashion)",
    "gap": "时尚快消 (Fast Fashion)",
    "cos": "时尚快消 (Fast Fashion)",
    "& other stories": "时尚快消 (Fast Fashion)",
    "bershka": "时尚快消 (Fast Fashion)",
    "pull&bear": "时尚快消 (Fast Fashion)",

    # --- 童装 ---
    "carter's": "童装 (Childrenswear)",
    "carters": "童装 (Childrenswear)",
    "gap kids": "童装 (Childrenswear)",
    "petit bateau": "童装 (Childrenswear)",
    "mini boden": "童装 (Childrenswear)",
    "mamas & papas": "童装 (Childrenswear)",
    "jojo maman bébé": "童装 (Childrenswear)",
    "the children's place": "童装 (Childrenswear)",

    # --- 工装/防护 ---
    "carhartt": "工装/防护 (Workwear)",
    "dickies": "工装/防护 (Workwear)",
    "snickers": "工装/防护 (Workwear)",
    "blåkläder": "工装/防护 (Workwear)",
    "bla klader": "工装/防护 (Workwear)",
    "fristads": "工装/防护 (Workwear)",
    "portwest": "工装/防护 (Workwear)",

    # --- 内衣/家居 ---
    "victoria's secret": "内衣/家居 (Intimate & Home)",
    "calvin klein": "内衣/家居 (Intimate & Home)",
    "hanky panky": "内衣/家居 (Intimate & Home)",
    "la senza": "内衣/家居 (Intimate & Home)",
    "skims": "内衣/家居 (Intimate & Home)",
    "wolford": "内衣/家居 (Intimate & Home)",
}

# ============================================================
# 品牌类型的中文简称 → 完整名称映射
# ============================================================
BRAND_TYPE_SHORT_NAMES = {
    "户外": "户外 (Outdoor)",
    "运动休闲": "运动休闲 (Athleisure)",
    "时尚": "时尚快消 (Fast Fashion)",
    "快消": "时尚快消 (Fast Fashion)",
    "童装": "童装 (Childrenswear)",
    "工装": "工装/防护 (Workwear)",
    "防护": "工装/防护 (Workwear)",
    "内衣": "内衣/家居 (Intimate & Home)",
    "家居": "内衣/家居 (Intimate & Home)",
}


def get_all_brand_types() -> list[str]:
    """返回所有品牌类型完整名称列表"""
    return list(BRAND_TYPE_PREFERENCES.keys())


def get_preferred_categories(brand_type: str) -> dict[str, int]:
    """获取某品牌类型的偏好面料类别及权重"""
    full_name = BRAND_TYPE_SHORT_NAMES.get(brand_type, brand_type)
    return BRAND_TYPE_PREFERENCES.get(full_name, {})


def lookup_brand(brand_name: str) -> Optional[str]:
    """在品牌映射表中查找品牌（不区分大小写）"""
    key = brand_name.strip().lower()
    # 精确匹配
    if key in BRAND_TYPE_MAP:
        return BRAND_TYPE_MAP[key]
    # 部分匹配：品牌名包含在映射表中
    for brand, brand_type in BRAND_TYPE_MAP.items():
        if brand in key or key in brand:
            return brand_type
    return None
