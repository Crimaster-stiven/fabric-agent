"""
将客户 Excel 面料数据转换为 fabrics.csv

从「产品说明」字段中解析出功能特点、适用产品、核心卖点，
并自动分类面料类别和适用品牌类型。
"""

import re
import pandas as pd

# ============================================================
# 读取 Excel
# ============================================================
df = pd.read_excel(
    "/Users/cri/Downloads/产品说明4-6加英文.xlsx",
    sheet_name="面料资料",
    header=None,
)

rows = []
for i in range(2, len(df)):
    row = df.iloc[i]
    code = str(row[1]).strip() if pd.notna(row[1]) else ""
    name = str(row[2]).strip() if pd.notna(row[2]) else ""
    spec = str(row[3]).strip() if pd.notna(row[3]) else ""
    composition = str(row[4]).strip() if pd.notna(row[4]) else ""
    price = str(row[5]) if pd.notna(row[5]) else ""
    desc_cn = str(row[6]).strip() if pd.notna(row[6]) else ""

    # 英文描述（在 Col13）
    desc_en = ""
    if len(row) > 13 and pd.notna(row[13]):
        desc_en = str(row[13]).strip()

    if not code:
        continue

    rows.append({
        "code": code,
        "name": name,
        "spec": spec,
        "composition": composition,
        "price": price,
        "desc_cn": desc_cn,
        "desc_en": desc_en,
    })

print(f"共读取 {len(rows)} 条面料数据\n")

# ============================================================
# 分类逻辑
# ============================================================

def classify_fabric(code, name, desc):
    """根据面料名称和描述判断类别"""
    text = f"{name} {desc}"

    # 保暖优先（摇粒、抓绒、羊毛）
    if "摇粒" in text or "抓绒" in text or "poly" in text.lower() and "保暖" in text:
        return "保暖类"
    if "羊毛" in text and ("保暖" in text or "秋冬" in text or "打底" in text):
        return "保暖类"
    if "保暖" in text or "发热" in text:
        return "保暖类"

    # 防晒+防透复合
    if "遮热" in text and ("防透" in text or "防透" in name):
        return "防晒防透类"

    # 防晒
    if "防晒" in text or "UPF" in text or "抗uv" in text.lower() or "抗UV" in text:
        return "防晒类"

    # 凉感（在弹力之前）
    if "凉感" in text or "凉感" in name or "接触凉" in text:
        if "导湿" in text or "速干" in text:
            return "凉感导湿类"
        return "凉感类"

    # 防水透湿
    if "防水" in text or "透湿" in text:
        return "防水透湿类"

    # 阻燃
    if "阻燃" in text or "阻燃" in name:
        return "阻燃类"

    # 防透
    if "防透" in text or "防透" in name:
        return "防透类"

    # 环保再生
    if "环保" in text or "再生" in text or "GRS" in text:
        return "环保再生类"

    # 弹力（含氨纶/弹性）
    if "弹力" in text or "弹性" in text or ("氨纶" in composition or "SP" in composition):
        if "亲肤" in text or "棉感" in text:
            return "弹力亲肤类"
        return "弹力类"

    # 导湿速干
    if "导湿" in text or "速干" in text or "排汗" in text or "单向导湿" in text:
        return "导湿速干类"

    # 抗菌亲肤
    if "抗菌" in text or "亲肤" in text or "棉感" in text:
        return "抗菌亲肤类"

    # 兜底
    return "功能面料类"


def extract_features(desc):
    """从产品说明中提取核心功能特点"""
    features = []
    lines = desc.strip().split("\n")
    for line in lines:
        line = line.strip()
        # 去掉编号前缀如 "1、", "1.", "1，"
        line = re.sub(r"^\d+[、.,，]\s*", "", line)
        if not line:
            continue
        # 提取关键功能句（30字以内且不含"适合"）
        if "适合" in line or "提供" in line or "吊牌" in line:
            continue
        # 太长的不作为feature
        if len(line) < 50 and line not in features:
            features.append(line)
    return "、".join(features[:6]) if features else "功能面料"


def extract_applications(desc, name):
    """从产品说明中提取适用产品"""
    apps = set()
    # 从"适合做"或"适合"后面提取
    match = re.search(r"适合[做于用]([^。\n]+)", desc)
    if match:
        items = re.split(r"[、，,]", match.group(1))
        for item in items:
            item = item.strip()
            if item and len(item) < 20:
                apps.add(item)
    # 从单品词匹配
    keywords = ["T恤", "外套", "裤子", "POLO", "polo", "连衣裙", "防晒服",
                "运动服", "瑜伽裤", "骑行服", "内衣", "童装", "背心",
                "夹克", "帽子", "工装", "运动T恤", "百褶裙", "短裤",
                "打底", "内搭", "运动套装", "高尔夫"]
    for kw in keywords:
        if kw in desc or kw in name:
            apps.add(kw)
    apps_list = list(apps)
    return "、".join(apps_list[:6]) if apps_list else "服装"


def extract_selling_points(desc):
    """提取核心卖点（简短有力）"""
    points = []
    lines = desc.strip().split("\n")
    for line in lines:
        line = re.sub(r"^\d+[、.,，]\s*", "", line).strip()
        if not line:
            continue
        # 卖点通常包含技术指标
        if any(kw in line for kw in ["%", "+", "：", ":", "UPF", "标准"]):
            points.append(line)
        elif "专利" in line or "科技" in line or "高端" in line:
            points.append(line)
    return "；".join(points[:4]) if points else "功能面料"


def determine_brand_types(category, desc, name):
    """根据类别和描述确定适用品牌类型"""
    types = set()
    text = f"{name} {desc}"

    if "户外" in text or "防晒" in text or "防水" in text:
        types.add("户外")
    if "运动" in text or "弹力" in text or "瑜伽" in text or "速干" in text or "轻量" in text:
        types.add("运动休闲")
    if "时尚" in text or "潮牌" in text or "日韩" in text:
        types.add("时尚")
    if "童装" in text or "儿童" in text:
        types.add("童装")
    if "工装" in text or "防护" in text:
        types.add("工装")
    if "内衣" in text or "家居" in text or "打底" in text or "贴身" in text:
        types.add("内衣家居")
    if "GOLF" in text or "高尔夫" in text or "商务" in text:
        types.add("运动休闲")
    if "休闲" in text and "运动休闲" not in types:
        types.add("户外")

    # 基于类别的兜底规则
    if not types:
        cat_map = {
            "防晒类": "户外,运动休闲",
            "防晒防透类": "户外,运动休闲",
            "防透类": "运动休闲,时尚",
            "弹力类": "运动休闲",
            "弹力亲肤类": "运动休闲,童装",
            "导湿速干类": "户外,运动休闲",
            "凉感导湿类": "运动休闲",
            "抗菌亲肤类": "运动休闲,童装",
            "保暖类": "户外,运动休闲,内衣家居",
            "凉感类": "运动休闲",
            "防水透湿类": "户外",
            "环保再生类": "时尚,运动休闲",
            "功能面料类": "运动休闲",
        }
        return cat_map.get(category, "运动休闲")

    # 保暖类额外追加 运动休闲 和 内衣家居
    if category == "保暖类":
        types.update(["户外", "运动休闲", "内衣家居"])

    return ",".join(sorted(types))


def extract_weight(spec):
    """从规格中提取重量"""
    # "165CM实*120克" → "120g/m²"
    # "160CM*100克" → "100g/m²"
    # "152cm*255g" → "255g/m²"
    match = re.search(r'([\d.]+)\s*克', spec)
    if match:
        return f"{match.group(1)}g/m²"
    match = re.search(r'([\d.]+)\s*g\b', spec, re.IGNORECASE)
    if match:
        return f"{match.group(1)}g/m²"
    return spec


# ============================================================
# 生成 CSV
# ============================================================
output_rows = []
for r in rows:
    category = classify_fabric(r["code"], r["name"], r["desc_cn"])
    features = extract_features(r["desc_cn"])
    applications = extract_applications(r["desc_cn"], r["name"])
    selling_points = extract_selling_points(r["desc_cn"])
    brand_types = determine_brand_types(category, r["desc_cn"], r["name"])
    weight = extract_weight(r["spec"])
    composition = r["composition"]

    output_rows.append({
        "fabric_id": r["code"],
        "name": r["name"],
        "features": features,
        "applications": applications,
        "selling_points": selling_points,
        "category": category,
        "suitable_brand_types": brand_types,
        "weight": weight,
        "composition": composition,
    })

# 输出为 CSV
out_df = pd.DataFrame(output_rows)
out_path = "/Users/cri/Desktop/Person/self stu/cursor/CLaude set/fabric-agent/knowledge_base/fabrics.csv"
out_df.to_csv(out_path, index=False, encoding="utf-8-sig")

print(f"已生成 {len(output_rows)} 条面料数据 → fabrics.csv\n")

# 打印分类统计
print("=== 类别分布 ===")
for cat in out_df["category"].value_counts().items():
    print(f"  {cat[0]}: {cat[1]} 条")

print("\n=== 前 5 条预览 ===")
pd.set_option("display.max_colwidth", 50)
for _, row in out_df.head(5).iterrows():
    print(f"\n{row['fabric_id']} | {row['name']}")
    print(f"  类别: {row['category']}")
    print(f"  功能: {row['features'][:60]}")
    print(f"  适用: {row['applications'][:60]}")
    print(f"  品牌: {row['suitable_brand_types']}")
