"""
面料外贸客户开发 Agent — Streamlit 主入口

功能：
1. 输入品牌名 → 自动匹配推荐面料 → 生成英文开发邮件
2. 知识库浏览、公司信息配置、API Key 管理

后端 LLM：DeepSeek（兼容 OpenAI 接口）
"""

import os
import json
import streamlit as st
import streamlit.components.v1 as components

# 页面配置必须在最前面
st.set_page_config(
    page_title="面料外贸客户开发 Agent",
    page_icon="🧵",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# 简易密码保护
# ============================================================
APP_PASSWORD = os.getenv("APP_PASSWORD", "")

# 隐藏 Streamlit 默认 UI 元素（右上角菜单、footer、header）
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppDeployButton {visibility: hidden;}
div[data-testid="stDecoration"] {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 密码校验
if APP_PASSWORD:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 面料外贸客户开发 Agent")
        st.markdown("请输入密码以继续使用")
        password_input = st.text_input("密码", type="password", placeholder="请输入访问密码")
        col1, _ = st.columns([1, 3])
        with col1:
            if st.button("确认", use_container_width=True, type="primary"):
                if password_input == APP_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("密码错误，请重试")
        st.stop()

from dotenv import load_dotenv
from knowledge_base.fabric_loader import load_all_fabrics
from knowledge_base.brand_profiles import (
    get_all_brand_types,
    lookup_brand,
)
from matching_engine.brand_analyzer import identify_brand_type
from matching_engine.matcher import match_fabrics, get_match_score_label
from email_generator.generator import generate_email, regenerate_email

load_dotenv()

# ============================================================
# Session 状态初始化
# ============================================================
_DEFAULT_COMPANY = {
    "company_name": "",
    "advantages": "",
    "certifications": "",
    "contact": "",
}

for key, default in {
    "brand_name": "",
    "brand_type": None,
    "brand_type_source": None,
    "matched_fabrics": [],
    "generated_email": "",
    "company_info": _DEFAULT_COMPANY.copy(),
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "use_llm_analysis": True,
    "selected_brand_type": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.title("⚙️ 设置")

    # --- API Key 配置 ---
    with st.expander("🔑 API Key 配置", expanded=not st.session_state.api_key):
        api_key = st.text_input(
            "DeepSeek API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-...",
            help="输入 DeepSeek API Key（可在 platform.deepseek.com 获取）",
        )
        if api_key:
            st.session_state.api_key = api_key
        if not st.session_state.api_key:
            st.warning("⚠️ 请先配置 API Key 以使用邮件生成功能")
        else:
            st.success("✅ API Key 已配置")

    # --- 公司信息 ---
    with st.expander("🏭 公司信息（可选）", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.company_info["company_name"] = st.text_input(
                "公司名称",
                value=st.session_state.company_info.get("company_name", ""),
            )
            st.session_state.company_info["advantages"] = st.text_area(
                "工厂优势",
                value=st.session_state.company_info.get("advantages", ""),
                placeholder="如：15年面料生产经验、月产能50万米...",
                height=80,
            )
        with col2:
            st.session_state.company_info["certifications"] = st.text_area(
                "认证信息",
                value=st.session_state.company_info.get("certifications", ""),
                placeholder="如：OEKO-TEX, GRS, ISO 9001...",
                height=80,
            )
            st.session_state.company_info["contact"] = st.text_input(
                "联系方式",
                value=st.session_state.company_info.get("contact", ""),
                placeholder="如：info@company.com / +86-...",
            )
        if st.button("💾 保存公司信息", use_container_width=True):
            st.success("✅ 公司信息已保存")

    # --- 面料知识库浏览 ---
    with st.expander("📂 面料知识库（参考）", expanded=False):
        try:
            df_all = load_all_fabrics()
            st.dataframe(
                df_all[
                    [
                        "fabric_id",
                        "name",
                        "category",
                        "features",
                        "applications",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
        except Exception as e:
            st.error(f"读取面料库失败: {e}")

    # --- 使用说明 ---
    with st.expander("📖 使用说明", expanded=False):
        st.markdown("""
**使用方法：**
1. 先配置 DeepSeek API Key
2. （可选）填写公司信息，邮件中会自动引用
3. 输入目标品牌名称（英文）
4. 选择或自动识别品牌类型
5. 点击【开始匹配】
6. 查看推荐面料，生成开发邮件

**支持的品牌类型：**
- 🏔️ 户外 (Outdoor)
- 🏃 运动休闲 (Athleisure)
- 👗 时尚快消 (Fast Fashion)
- 👶 童装 (Childrenswear)
- 👷 工装/防护 (Workwear)
- 🏠 内衣/家居 (Intimate & Home)

**API Key 获取：**
→ [platform.deepseek.com](https://platform.deepseek.com)
        """)

    st.divider()

# ============================================================
# 主界面
# ============================================================
st.title("🧵 面料外贸客户开发 Agent")
st.markdown(
    "输入海外品牌名称，自动推荐最匹配的功能性面料，并生成专业英文开发邮件。"
)

# --- 输入区 ---
with st.container(border=True):
    col1, col2 = st.columns([3, 1])

    with col1:
        brand_name = st.text_input(
            "目标品牌名称",
            placeholder="例如：Patagonia, Lululemon, Zara...",
            value=st.session_state.brand_name,
            key="brand_input",
        )

    with col2:
        # 品牌类型选择
        all_types = get_all_brand_types()
        brand_type_options = ["自动识别"] + all_types
        selected = st.selectbox(
            "品牌类型",
            options=brand_type_options,
            index=0,
            key="brand_type_selector",
            help="选择「自动识别」将由系统判断品牌类型",
        )

    # LLM 分析开关 & 操作按钮
    col_a, col_b = st.columns([2, 1])
    with col_a:
        use_llm = st.checkbox(
            "使用 AI 分析未知品牌",
            value=st.session_state.use_llm_analysis,
            help="开启后，内置列表未覆盖的品牌将通过 AI 自动识别类型",
        )
        st.session_state.use_llm_analysis = use_llm

    with col_b:
        run_clicked = st.button(
            "🔍 开始匹配", use_container_width=True, type="primary"
        )

# --- 处理匹配逻辑 ---
if run_clicked:
    brand_name = brand_name or st.session_state.brand_name
    st.session_state.brand_name = brand_name

    if not brand_name.strip():
        st.warning("请输入品牌名称")
        st.stop()

    with st.status("🔄 正在分析...", expanded=True) as status:
        # 1. 识别品牌类型
        status.update(label="🔍 识别品牌类型...", state="running")

        # 手动选择 vs 自动识别
        if selected and selected != "自动识别":
            brand_type = selected
            source = "manual"
        else:
            st.session_state.selected_brand_type = None
            # 先本地查找
            local_result = lookup_brand(brand_name)
            if local_result:
                brand_type = local_result
                source = "local"
                st.write(f"✅ 内置库匹配: {brand_type}")
            elif use_llm and st.session_state.api_key:
                # LLM 分析（DeepSeek）
                result = identify_brand_type(
                    brand_name,
                    use_llm=True,
                    api_key=st.session_state.api_key,
                )
                brand_type = result["brand_type"]
                source = result.get("source", "llm")
                if brand_type:
                    st.write(f"✅ AI 分析结果: {brand_type}")
                else:
                    st.warning("⚠️ AI 无法确定品牌类型，请在下方手动选择")
                    status.update(label="⚠️ 需要手动选择品牌类型", state="error")
                    st.stop()
            else:
                st.warning(
                    "⚠️ 未找到该品牌信息，请手动选择品牌类型，"
                    "或开启「使用 AI 分析未知品牌」并配置 API Key"
                )
                status.update(label="⚠️ 需要手动选择品牌类型", state="error")
                st.stop()

        st.session_state.brand_type = brand_type
        st.session_state.brand_type_source = source

        # 2. 匹配面料
        status.update(label="🧶 匹配面料...", state="running")
        matched = match_fabrics(brand_type, top_n=5)

        if not matched:
            st.warning("未找到匹配的面料，请尝试其他品牌或调整品牌类型")
            status.update(label="❌ 未找到匹配", state="error")
            st.stop()

        st.session_state.matched_fabrics = matched
        status.update(label="✅ 匹配完成!", state="complete")

# ============================================================
# 匹配结果展示
# ============================================================
if st.session_state.matched_fabrics:
    brand_type = st.session_state.brand_type
    matched = st.session_state.matched_fabrics

    st.markdown("---")
    st.subheader(f"📊 匹配结果 — {st.session_state.brand_name}")

    source_map = {
        "local": "内置库",
        "llm": "AI 分析",
        "manual": "手动选择",
    }
    source_label = source_map.get(
        st.session_state.brand_type_source, st.session_state.brand_type_source
    )
    st.caption(f"品牌类型: {brand_type}（来源: {source_label}）")

    # 展示前 3 条作为主推
    st.markdown("#### ⭐ 主推面料")
    cols = st.columns(3)
    for i, fb in enumerate(matched[:3]):
        fabric = fb["fabric"]
        score = fb["score"]
        stars, pct = get_match_score_label(score)

        with cols[i]:
            with st.container(border=True):
                st.markdown(f"**{fabric['fabric_id']}**")
                st.markdown(f"##### {fabric['name']}")
                st.markdown(f"匹配度: **{stars}** ({pct}%)")
                st.markdown(
                    f"`{fabric['category']}`   |   重量: {fabric['weight']}"
                )
                st.caption(f"✅ {fb['match_reason']}")

    # 完整列表
    with st.expander("📋 查看全部匹配面料"):
        for i, fb in enumerate(matched, 1):
            fabric = fb["fabric"]
            score = fb["score"]
            stars, pct = get_match_score_label(score)

            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f"**{stars}**")
                st.markdown(f"`{pct}%`")
            with col2:
                st.markdown(
                    f"**{fabric['fabric_id']} - {fabric['name']}**"
                )
                st.markdown(f"*{fabric['features']}*")
                st.markdown(
                    f"📌 适用: {fabric['applications']}  "
                    f"💡 卖点: {fabric['selling_points']}"
                )
                st.caption(f"✅ {fb['match_reason']}")
            if i < len(matched):
                st.divider()

    # ============================================================
    # 邮件生成区
    # ============================================================
    st.markdown("---")
    st.subheader("📧 英文开发邮件")

    # 邮件生成按钮
    gen_col1, gen_col2 = st.columns([3, 1])
    with gen_col1:
        generate_clicked = st.button(
            "✍️ 生成开发邮件",
            use_container_width=True,
            type="primary",
        )
    with gen_col2:
        if st.session_state.generated_email:
            regenerate_clicked = st.button(
                "🔄 重新生成",
                use_container_width=True,
            )
        else:
            regenerate_clicked = False

    # 生成邮件
    if generate_clicked or regenerate_clicked:
        if not st.session_state.api_key:
            st.error("⚠️ 请先在侧边栏配置 DeepSeek API Key")
            st.stop()

        try:
            with st.spinner("✍️ AI 正在撰写邮件..."):
                email = generate_email(
                    api_key=st.session_state.api_key,
                    brand_name=st.session_state.brand_name,
                    brand_type=st.session_state.brand_type,
                    fabrics_info=st.session_state.matched_fabrics,
                    company_info=st.session_state.company_info,
                )
                st.session_state.generated_email = email
        except Exception as e:
            st.error(f"邮件生成失败: {e}")

    # 展示邮件
    if st.session_state.generated_email:
        email_text = st.session_state.generated_email
        # 使用 json.dumps 做安全转义，避免特殊字符破坏 JavaScript
        email_json = json.dumps(email_text)

        # 邮件主体 — 清爽展示
        with st.container(border=True):
            st.markdown("**📧 邮件预览**")
            st.text_area(
                "",
                value=email_text,
                height=400,
                label_visibility="collapsed",
            )

        # 复制按钮 — 用 components.html 确保 JavaScript 正确执行
        copy_html = f"""
        <div style="display: flex; gap: 8px;">
            <button onclick="navigator.clipboard.writeText({email_json})"
                    style="padding: 8px 20px; border-radius: 8px; border: 1px solid #ccc;
                           background: white; cursor: pointer; font-size: 14px;
                           display: inline-flex; align-items: center; gap: 6px;">
                📋 复制邮件
            </button>
        </div>
        """
        components.html(copy_html, height=50)

        # 反馈重生成区域
        with st.expander("🔄 修改邮件内容"):
            feedback = st.text_area(
                "修改意见（可选）",
                placeholder="如：语气更正式一些、突出环保认证、缩短开头段落...",
                height=80,
            )
            if st.button("按意见重新生成", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("⚠️ 请先配置 DeepSeek API Key")
                else:
                    with st.spinner("✍️ 根据反馈重新生成..."):
                        try:
                            new_email = regenerate_email(
                                api_key=st.session_state.api_key,
                                previous_email=st.session_state.generated_email,
                                feedback=feedback,
                            )
                            st.session_state.generated_email = new_email
                        except Exception as e:
                            st.error(f"重新生成失败: {e}")
