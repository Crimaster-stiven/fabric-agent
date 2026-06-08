"""
邮件 Prompt 模板

构建发送给 Claude API 的 System Prompt 和 User Prompt。
"""

from typing import Optional

# ============================================================
# System Prompt
# ============================================================
SYSTEM_PROMPT = """You are a senior textile and fabric sourcing specialist with 15+ years of experience in international B2B trade. You excel at writing professional, personalized cold outreach emails that get responses from overseas fashion and sportswear brands.

Your writing style:
- Professional but warm — not overly formal, not too casual
- Concise and value-driven — every sentence serves a purpose
- Brand-aware — show genuine understanding of the target brand's products and market position
- Natural English — no template clichés, no robotic phrasing
- B2B appropriate — focus on business value, quality, and partnership

CRITICAL formatting rules:
- DO NOT use any markdown formatting (no **bold**, no *italic*, no # headings, no `code`)
- Output plain text only — the email should be ready to copy and send directly
- Use plain line breaks to separate paragraphs
- Subject line should be plain text, no brackets or special formatting

Email structure guidelines:
1. Subject: Compelling, specific (not generic like "Fabric Inquiry")
2. Opening: Reference the brand's work specifically — shows you've done your homework
3. Body: Present 2-3 fabric recommendations with clear WHY each one fits their products
4. Value proposition: What makes your fabrics/factory different (quality, certifications, MOQ flexibility, etc.)
5. Call to action: Low-friction next step (sample request, technical data sheet, call)
6. Closing: Professional signature with contact details

CRITICAL: Do NOT use placeholders like [Brand Name] or [Your Company]. Write the email as if it's ready to send."""


# ============================================================
# User Prompt Builder
# ============================================================

def build_user_prompt(
    brand_name: str,
    brand_type: str,
    fabrics_info: list[dict],
    company_info: Optional[dict] = None,
) -> str:
    """构建用户 prompt

    Args:
        brand_name: 品牌名称
        brand_type: 品牌类型 (如 "户外 (Outdoor)")
        fabrics_info: 匹配的面料列表，每项包含:
            - name: 面料名称
            - fabric_id: 编号
            - features: 功能特点
            - applications: 适用产品
            - selling_points: 核心卖点
            - match_reason: 推荐理由
        company_info: 公司信息 (可选)
            - company_name: 公司名称
            - advantages: 工厂优势
            - certifications: 认证信息
            - contact: 联系方式

    Returns:
        str: 格式化后的 User Prompt
    """
    # 品牌类型简称
    brand_short = brand_type.split(" (")[0] if " (" in brand_type else brand_type

    # 公司信息
    company_section = ""
    if company_info:
        name = company_info.get("company_name", "").strip()
        adv = company_info.get("advantages", "").strip()
        cert = company_info.get("certifications", "").strip()
        contact = company_info.get("contact", "").strip()

        parts = []
        if name:
            parts.append(f"Company: {name}")
        if adv:
            parts.append(f"Factory advantages: {adv}")
        if cert:
            parts.append(f"Certifications: {cert}")
        if contact:
            parts.append(f"Contact: {contact}")
        if parts:
            company_section = "\n".join(parts)

    # 面料信息
    fabrics_section = ""
    for i, fb in enumerate(fabrics_info, 1):
        fabric = fb.get("fabric", {})
        reason = fb.get("match_reason", "")
        fabrics_section += f"""
Fabric {i}: {fabric.get('fabric_id', '')} - {fabric.get('name', '')}
  • Features: {fabric.get('features', '')}
  • Applications: {fabric.get('applications', '')}
  • Selling Points: {fabric.get('selling_points', '')}
  • Why recommended: {reason}

"""

    prompt = f"""Target brand: {brand_name}
Brand category: {brand_type} (short: {brand_short})

{company_section}

Below are the fabrics we want to recommend to this brand:

{fabrics_section}

Please write a complete, professional B2B cold outreach email to {brand_name}'s sourcing or product development team. Use the information above naturally — don't just list specs. The email should sound like it was written by an industry expert who genuinely understands {brand_name}'s products and market position.

Key requirements:
- Subject line that would catch a sourcing manager's attention
- Natural opening referencing the brand's product category ({brand_short})
- Present the recommended fabrics with context (not just feature dumping)
- Explain why each fabric fits their specific product lines
- Include a low-pressure call to action (samples, tech data, call)
- Professional email signature"""

    return prompt


# ============================================================
# Few-shot 示例 (用于稳定输出格式)
# ============================================================
FEW_SHOT_EXAMPLE = """
Example of a well-written outreach email (plain text, no markdown):

Subject: Technical Fabrics for [Brand]'s Running Collection

Dear [Brand] Product Team,

I've been following [Brand]'s recent expansion into premium running apparel, particularly your lightweight layer system. The combination of performance and aesthetics you've achieved is impressive.

We specialize in high-performance knitted fabrics for activewear and believe two of our developments would be an excellent fit for your next season:

1. F-005 Lightweight Moisture-Wicking Fabric (60g/m2)
   With rapid moisture transfer and featherlight handfeel, this fabric would work exceptionally well in your running tops and base layers. It meets AATCC drying standards and has been tested across marathon-level conditions.

2. F-004 4-Way Stretch Fabric (180g/m2)
   The 95% stretch recovery rate makes this ideal for compression pieces and training shorts where freedom of movement is non-negotiable. It's also pilling-resistant after 100+ wash cycles.

Both fabrics are OEKO-TEX certified and available with custom finishes. We can provide sample yardage within 5 working days.

Would you be open to reviewing technical data sheets and receiving a sample set? Happy to arrange a call to discuss your specific requirements.

Best regards,
[Your Name]
Textile Sourcing Specialist
[Company]
[Email] | [Phone]

---
Now write the email for {brand_name}:"""


def build_few_shot_user_prompt(
    brand_name: str,
    brand_type: str,
    fabrics_info: list[dict],
    company_info: Optional[dict] = None,
) -> str:
    """构建带 few-shot 示例的 User Prompt"""
    base = build_user_prompt(brand_name, brand_type, fabrics_info, company_info)
    return base + "\n\n" + FEW_SHOT_EXAMPLE.replace("{brand_name}", brand_name)
