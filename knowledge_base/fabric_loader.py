"""
面料数据加载 & 查询函数

从 fabrics.csv 读取面料数据，提供按类别、品牌类型等维度的查询能力。
"""

import os
from typing import Optional
import pandas as pd

# 当前文件所在目录
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_CSV_PATH = os.path.join(_CURRENT_DIR, "fabrics.csv")


def load_all_fabrics() -> pd.DataFrame:
    """加载所有面料数据"""
    df = pd.read_csv(_CSV_PATH)
    # 处理 suitable_brand_types：逗号分隔转列表
    df["suitable_brand_types_list"] = df["suitable_brand_types"].apply(
        lambda x: [t.strip() for t in str(x).split(",")]
    )
    return df


def get_fabric_by_id(fabric_id: str) -> Optional[dict]:
    """按面料编号查询"""
    df = load_all_fabrics()
    row = df[df["fabric_id"] == fabric_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def get_fabrics_by_category(category: str) -> pd.DataFrame:
    """按面料大类查询"""
    df = load_all_fabrics()
    return df[df["category"] == category]


def get_fabrics_by_brand_type(brand_type_short: str) -> pd.DataFrame:
    """查询适合某品牌类型的面料

    使用 suitable_brand_types 字段进行模糊匹配。
    """
    df = load_all_fabrics()
    mask = df["suitable_brand_types"].str.contains(
        brand_type_short, case=False, na=False
    )
    return df[mask]


def get_all_categories() -> list[str]:
    """获取所有面料类别"""
    df = load_all_fabrics()
    return df["category"].unique().tolist()
