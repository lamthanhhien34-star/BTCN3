
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. CẤU HÌNH ỨNG DỤNG
# ============================================================

st.set_page_config(
    page_title="Amazon Baby Product Intelligence",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. GIAO DIỆN
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top right, rgba(99,102,241,.07), transparent 28%),
            linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #172554 100%);
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }

    .hero {
        padding: 26px 30px;
        border-radius: 24px;
        background: linear-gradient(135deg, #3730a3 0%, #4f46e5 48%, #7c3aed 100%);
        color: white;
        box-shadow: 0 16px 38px rgba(79, 70, 229, .18);
        margin-bottom: 18px;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.05rem;
        font-weight: 850;
    }

    .hero p {
        margin: 8px 0 0;
        opacity: .94;
        font-size: 1rem;
    }

    .kpi {
        background: rgba(255,255,255,.97);
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 16px 18px;
        min-height: 116px;
        box-shadow: 0 8px 22px rgba(15,23,42,.05);
    }

    .kpi-label {
        color: #64748b;
        font-size: .76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .05em;
    }

    .kpi-value {
        color: #0f172a;
        font-size: 1.68rem;
        font-weight: 850;
        margin-top: 6px;
    }

    .kpi-note {
        color: #64748b;
        font-size: .78rem;
        margin-top: 4px;
    }

    .section-title {
        font-size: 1.20rem;
        font-weight: 850;
        color: #0f172a;
        margin: 10px 0 8px;
    }

    .insight {
        background: white;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #6366f1;
        border-radius: 15px;
        padding: 14px 16px;
        margin: 10px 0 16px;
        box-shadow: 0 6px 16px rgba(15,23,42,.04);
    }

    .decision {
        background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%);
        border: 1px solid #c7d2fe;
        border-radius: 18px;
        padding: 16px 18px;
        margin: 10px 0 14px;
        box-shadow: 0 8px 22px rgba(79,70,229,.06);
    }

    .decision-title {
        font-size: .78rem;
        color: #4338ca;
        font-weight: 850;
        letter-spacing: .05em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .decision-main {
        font-size: 1.06rem;
        color: #111827;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .decision-note {
        font-size: .86rem;
        color: #475569;
    }

    .risk-note {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-left: 5px solid #f97316;
        border-radius: 14px;
        padding: 13px 15px;
        margin: 8px 0 15px;
        color: #7c2d12;
    }

    .method-note {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 14px;
        padding: 13px 15px;
        margin: 8px 0 15px;
        color: #334155;
    }

    .footer {
        text-align:center;
        color:#64748b;
        font-size:.80rem;
        padding:24px 0 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. HẰNG SỐ VIỆT HÓA
# ============================================================

ASPECT_VI = {
    "Quality & Durability": "Chất lượng & độ bền",
    "Safety-related": "Phản hồi liên quan an toàn",
    "Ease of Use": "Dễ sử dụng",
    "Comfort": "Sự thoải mái",
    "Cleaning": "Vệ sinh",
    "Leakage & Sealing": "Rò rỉ & độ kín",
    "Material & Odor": "Chất liệu & mùi",
    "Size & Fit": "Kích thước & độ vừa vặn",
    "Price & Value": "Giá & giá trị",
    "Delivery & Packaging": "Giao hàng & đóng gói",
}

RISK_VI = {
    "Critical": "Rất cao",
    "High": "Cao",
    "Medium": "Trung bình",
    "Low": "Thấp",
}

SIGNAL_VI = RISK_VI.copy()

SENTIMENT_VI = {
    "Positive": "Tích cực",
    "Neutral": "Trung lập",
    "Negative": "Tiêu cực",
}

EXPERIENCE_VI = {
    "Mostly confirmed": "Phần lớn được xác nhận",
    "Mixed": "Trải nghiệm trái chiều",
    "Frequently contradicted": "Thường xuyên bị phản bác",
    "Insufficient evidence": "Chưa đủ bằng chứng",
}

ACTION_BY_ASPECT = {
    "Quality & Durability":
        "Rà soát các review mô tả lỗi, hư hỏng hoặc độ bền; đối chiếu với đặc tính sản phẩm và phản hồi hậu mãi.",
    "Safety-related":
        "Ưu tiên chuyển các phản hồi liên quan an toàn cho nhóm chất lượng/sản phẩm để kiểm tra chi tiết từng review và bằng chứng liên quan.",
    "Ease of Use":
        "Kiểm tra hướng dẫn sử dụng, mô tả listing và nội dung minh họa để giảm khó khăn trong quá trình sử dụng.",
    "Comfort":
        "Rà soát phản hồi về độ thoải mái, thiết kế và nhóm người dùng gặp vấn đề để xác định điểm cần cải thiện.",
    "Cleaning":
        "Kiểm tra hướng dẫn vệ sinh/bảo quản và các phản hồi về khó làm sạch hoặc khó bảo trì.",
    "Leakage & Sealing":
        "Rà soát phản hồi về rò rỉ/độ kín, điều kiện sử dụng và khả năng liên quan đến thiết kế hoặc cách dùng.",
    "Material & Odor":
        "Kiểm tra review về chất liệu/mùi, phân loại trường hợp lặp lại và chuyển nhóm chất lượng xem xét khi cần.",
    "Size & Fit":
        "Rà soát thông tin kích thước, hướng dẫn chọn size và những nhóm khách hàng thường gặp vấn đề về độ vừa vặn.",
    "Price & Value":
        "Đánh giá lại mức giá, giá trị cảm nhận và thông điệp lợi ích so với kỳ vọng được thể hiện trong review.",
    "Delivery & Packaging":
        "Tách phản hồi do sản phẩm khỏi phản hồi do giao hàng/đóng gói; ưu tiên kiểm tra quy trình fulfillment nếu vấn đề lặp lại.",
}


# ============================================================
# 4. TỰ ĐỘNG TÌM THƯ MỤC DỮ LIỆU
# ============================================================

ROOT = Path(__file__).resolve().parent

def find_data_dir():
    candidates = [
        ROOT / "data",
        ROOT / "web_bundle",
        ROOT / "amazon_baby_web_bundle",
        ROOT,
    ]
    for folder in candidates:
        if (folder / "overview.json").exists():
            return folder

    found = list(ROOT.rglob("overview.json"))
    if found:
        return found[0].parent

    return ROOT / "data"

DATA_DIR = find_data_dir()


# ============================================================
# 5. HÀM ĐỌC DỮ LIỆU
# ============================================================

@st.cache_data(show_spinner=False)
def read_json(name):
    path = DATA_DIR / name
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def read_csv(name):
    path = DATA_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def read_parquet(name):
    path = DATA_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)

def parse_date(df, column):
    if df.empty or column not in df.columns:
        return df
    out = df.copy()
    out[column] = pd.to_datetime(out[column], errors="coerce")
    return out


# ============================================================
# 6. HÀM HIỂN THỊ / TIỆN ÍCH
# ============================================================

def safe_float(x, default=np.nan):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default

def fmt_int(x):
    x = safe_float(x)
    return "—" if pd.isna(x) else f"{int(round(x)):,}"

def fmt_num(x, n=2):
    x = safe_float(x)
    return "—" if pd.isna(x) else f"{x:.{n}f}"

def fmt_pct(x, n=1):
    x = safe_float(x)
    return "—" if pd.isna(x) else f"{x * 100:.{n}f}%"

def fmt_money(x):
    x = safe_float(x)
    return "—" if pd.isna(x) else f"${x:,.2f}"

def shorten(text, max_chars=50):
    if text is None or pd.isna(text):
        return "Không rõ sản phẩm"
    text = " ".join(str(text).split())
    if len(text) <= max_chars:
        return text
    short = text[:max_chars].rsplit(" ", 1)[0]
    return short + "..."

def clean_text(x, fallback="Không rõ"):
    if x is None or pd.isna(x):
        return fallback
    x = str(x).strip()
    return x if x else fallback

def product_label(row, max_chars=58):
    title = shorten(row.get("product_title"), max_chars)
    store = clean_text(row.get("store"), "Không rõ store")
    return f"{title} · {store}"

def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def kpi(label, value, note=""):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def decision_card(title, main, note):
    st.markdown(
        f"""
        <div class="decision">
            <div class="decision-title">{title}</div>
            <div class="decision-main">{main}</div>
            <div class="decision-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def evidence_level(review_count):
    n = safe_float(review_count, 0)
    if n >= 500:
        return "Bằng chứng mạnh", "Nhiều review hỗ trợ việc ưu tiên theo dõi."
    if n >= 100:
        return "Bằng chứng khá", "Có lượng review tương đối đủ để diễn giải xu hướng."
    if n >= 30:
        return "Bằng chứng hạn chế", "Nên xem thêm review chi tiết trước khi đưa ra quyết định lớn."
    return "Chưa đủ bằng chứng", "Số review thấp; chỉ nên xem đây là tín hiệu tham khảo."

def bool_vi(x):
    if pd.isna(x):
        return "Không rõ"
    return "Có" if bool(x) else "Không"


# ============================================================
# 7. ĐỌC TOÀN BỘ WEB BUNDLE
# ============================================================

overview = read_json("overview.json")
pipeline = read_json("pipeline_metrics.json")
nlp_validation = read_json("nlp_validation.json")

product_summary = read_parquet("product_summary.parquet")
monthly_trend = parse_date(read_parquet("monthly_trend.parquet"), "review_month")
subcategory_summary = read_parquet("subcategory_summary.parquet")
product_monthly = parse_date(read_parquet("product_monthly.parquet"), "review_month")
aspect_summary = read_parquet("aspect_summary.parquet")
aspect_product_summary = read_parquet("aspect_product_summary.parquet")
representative_reviews = parse_date(read_parquet("representative_reviews.parquet"), "review_date")
complaint_monthly = parse_date(read_parquet("complaint_monthly.parquet"), "review_month")
emerging_issues = parse_date(read_parquet("emerging_issues.parquet"), "review_month")
risk_scores = read_parquet("risk_scores.parquet")
claim_experience = read_parquet("claim_experience.parquet")
nlp_sample = parse_date(read_parquet("nlp_sentiment_sample.parquet"), "review_date")
spark_benchmark = read_csv("spark_benchmark.csv")
data_quality = read_csv("data_quality.csv")


# ============================================================
# 8. KIỂM TRA DỮ LIỆU
# ============================================================

required_files = [
    "overview.json",
    "pipeline_metrics.json",
    "product_summary.parquet",
    "monthly_trend.parquet",
    "subcategory_summary.parquet",
    "product_monthly.parquet",
    "aspect_summary.parquet",
    "aspect_product_summary.parquet",
    "representative_reviews.parquet",
    "complaint_monthly.parquet",
    "emerging_issues.parquet",
    "risk_scores.parquet",
    "claim_experience.parquet",
    "nlp_sentiment_sample.parquet",
    "nlp_validation.json",
    "spark_benchmark.csv",
    "data_quality.csv",
]

missing_files = [x for x in required_files if not (DATA_DIR / x).exists()]

if missing_files:
    st.error("Ứng dụng chưa tìm thấy đầy đủ dữ liệu đầu ra của pipeline.")
    st.write("Thư mục dữ liệu đang nhận diện:", str(DATA_DIR))
    st.write("Các file còn thiếu:")
    for name in missing_files:
        st.code(name)
    st.stop()


# ============================================================
# 9. ENRICH DỮ LIỆU THEO SẢN PHẨM
# ============================================================

lookup_fields = [
    c for c in [
        "parent_asin",
        "product_title",
        "store",
        "subcategory",
        "price",
        "reviews",
        "avg_rating",
        "negative_rate",
        "verified_rate",
        "helpful_votes",
    ]
    if c in product_summary.columns
]

product_lookup = (
    product_summary[lookup_fields]
    .drop_duplicates("parent_asin")
    .copy()
)

def enrich_product(df):
    if df.empty or "parent_asin" not in df.columns:
        return df.copy()

    base = df.copy()
    add_cols = ["parent_asin"]

    for c in ["product_title", "store", "subcategory", "price"]:
        if c in product_lookup.columns and c not in base.columns:
            add_cols.append(c)

    if len(add_cols) == 1:
        return base

    return base.merge(
        product_lookup[add_cols],
        on="parent_asin",
        how="left",
    )

risk_full = enrich_product(risk_scores)
emerging_full = enrich_product(emerging_issues)
aspect_product_full = enrich_product(aspect_product_summary)
complaint_full = enrich_product(complaint_monthly)
claim_full = enrich_product(claim_experience)

for df in [product_summary, risk_full, emerging_full, aspect_product_full, complaint_full, claim_full]:
    if not df.empty and "product_title" in df.columns:
        df["product_name_short"] = df["product_title"].apply(lambda x: shorten(x, 52))


# ============================================================
# 10. DECISION SUPPORT ENGINE
# ============================================================

def top_issue_for_product(asin):
    # Ưu tiên emerging signal mạnh; nếu không có thì dùng aspect có negative rate cao nhất
    if not emerging_full.empty:
        temp = emerging_full[emerging_full["parent_asin"].astype(str) == str(asin)].copy()
        if not temp.empty and "signal_score" in temp.columns:
            temp = temp.sort_values(["signal_score", "complaint_rate"], ascending=[False, False])
            r = temp.iloc[0]
            return {
                "aspect": r.get("aspect"),
                "signal_score": safe_float(r.get("signal_score")),
                "signal_level": r.get("signal_level"),
                "growth_pct": safe_float(r.get("growth_pct")),
                "complaint_rate": safe_float(r.get("complaint_rate")),
                "source": "emerging",
            }

    if not aspect_product_full.empty:
        temp = aspect_product_full[
            aspect_product_full["parent_asin"].astype(str) == str(asin)
        ].copy()
        if not temp.empty and "negative_rate" in temp.columns:
            temp = temp.sort_values(["negative_rate", "mentions"], ascending=[False, False])
            r = temp.iloc[0]
            return {
                "aspect": r.get("aspect"),
                "negative_rate": safe_float(r.get("negative_rate")),
                "mentions": safe_float(r.get("mentions")),
                "source": "aspect",
            }

    return {
        "aspect": None,
        "source": "none",
    }

def risk_components(row):
    # Các cột n_* được pipeline chuẩn hóa về 0-1.
    neg = safe_float(row.get("n_negative"), 0)
    sig = safe_float(row.get("n_signal"), 0)
    low = safe_float(row.get("low_rating_component"), 0)
    helpful = safe_float(row.get("n_helpful"), 0)

    return {
        "Review tiêu cực": max(0, min(35, neg * 35)),
        "Tín hiệu bất thường": max(0, min(35, sig * 35)),
        "Rating thấp": max(0, min(20, low * 20)),
        "Helpful votes": max(0, min(10, helpful * 10)),
    }

def decision_for_product(row):
    asin = str(row.get("parent_asin", ""))
    risk_score = safe_float(row.get("risk_score"), 0)
    risk_level = row.get("risk_level", "Low")
    negative_rate = safe_float(row.get("negative_rate"), 0)
    avg_rating = safe_float(row.get("avg_rating"), np.nan)
    reviews = safe_float(row.get("reviews"), 0)

    issue = top_issue_for_product(asin)
    aspect = issue.get("aspect")
    aspect_vi = ASPECT_VI.get(aspect, aspect) if aspect else "Chưa xác định chủ đề nổi bật"

    if risk_level == "Critical" or risk_score >= 75:
        priority = "Ưu tiên kiểm tra ngay"
    elif risk_level == "High" or risk_score >= 55:
        priority = "Ưu tiên cao trong kỳ gần nhất"
    elif risk_level == "Medium" or risk_score >= 35:
        priority = "Theo dõi có chủ đích"
    else:
        priority = "Duy trì theo dõi định kỳ"

    reasons = []

    if negative_rate >= 0.20:
        reasons.append(f"Tỷ lệ review tiêu cực cao ({fmt_pct(negative_rate)}).")
    elif negative_rate >= 0.12:
        reasons.append(f"Tỷ lệ review tiêu cực đáng theo dõi ({fmt_pct(negative_rate)}).")

    sig_score = safe_float(issue.get("signal_score"), np.nan)
    sig_level = issue.get("signal_level")

    if not pd.isna(sig_score) and (sig_level in ["Critical", "High"] or sig_score >= 60):
        reasons.append(
            f"Có tín hiệu phản hồi tăng bất thường ở chủ đề “{aspect_vi}” "
            f"(điểm tín hiệu {fmt_num(sig_score, 1)})."
        )

    if not pd.isna(avg_rating) and avg_rating < 3.5:
        reasons.append(f"Điểm đánh giá trung bình tương đối thấp ({fmt_num(avg_rating, 2)}★).")

    if not reasons:
        if aspect:
            reasons.append(f"Chủ đề nổi bật cần tiếp tục quan sát: “{aspect_vi}”.")
        else:
            reasons.append("Chưa xuất hiện tín hiệu nổi bật theo các tiêu chí hiện tại.")

    if aspect in ACTION_BY_ASPECT:
        action = ACTION_BY_ASPECT[aspect]
    elif risk_score >= 55:
        action = (
            "Mở các review tiêu cực có helpful vote cao, xác định nguyên nhân lặp lại "
            "và theo dõi complaint rate ở kỳ tiếp theo trước khi đưa ra hành động lớn."
        )
    else:
        action = (
            "Tiếp tục theo dõi rating, tỷ lệ tiêu cực và chủ đề phản hồi theo thời gian; "
            "chưa cần can thiệp mạnh nếu xu hướng vẫn ổn định."
        )

    evidence_name, evidence_note = evidence_level(reviews)

    return {
        "priority": priority,
        "reason": " ".join(reasons),
        "action": action,
        "aspect": aspect,
        "aspect_vi": aspect_vi,
        "evidence": evidence_name,
        "evidence_note": evidence_note,
    }

def build_action_table(df, top_n=15):
    if df.empty:
        return pd.DataFrame()

    temp = df.sort_values("risk_score", ascending=False).head(top_n).copy()
    rows = []

    for _, r in temp.iterrows():
        d = decision_for_product(r)
        rows.append({
            "Sản phẩm": shorten(r.get("product_title"), 56),
            "Cửa hàng / thương hiệu": clean_text(r.get("store")),
            "Mức ưu tiên": RISK_VI.get(r.get("risk_level"), r.get("risk_level")),
            "Điểm ưu tiên": safe_float(r.get("risk_score"), 0),
            "Tỷ lệ tiêu cực": fmt_pct(r.get("negative_rate")),
            "Vấn đề chính": d["aspect_vi"],
            "Vì sao": d["reason"],
            "Hành động đề xuất": d["action"],
            "Mức bằng chứng": d["evidence"],
            "Parent ASIN": r.get("parent_asin"),
        })

    return pd.DataFrame(rows)


# ============================================================
# 11. THANH ĐIỀU HƯỚNG
# ============================================================

with st.sidebar:
    st.markdown("## 🧸 BABY PRODUCT INTELLIGENCE")
    st.caption("Decision Support từ tiếng nói khách hàng")

    page = st.radio(
        "Nội dung",
        [
            "1. Tổng quan điều hành",
            "2. Sản phẩm cần chú ý",
            "3. Chi tiết sản phẩm",
            "4. Tiếng nói khách hàng",
            "5. Big Data & phương pháp",
        ],
    )

    st.markdown("---")
    st.markdown("### Bộ lọc")

    all_categories = []
    if not product_summary.empty and "subcategory" in product_summary.columns:
        all_categories = sorted(
            product_summary["subcategory"].dropna().astype(str).unique().tolist()
        )

    selected_categories = st.multiselect(
        "Danh mục con",
        all_categories,
        placeholder="Tất cả danh mục",
    )

    min_reviews = st.slider(
        "Số review tối thiểu",
        min_value=0,
        max_value=500,
        value=30,
        step=10,
        help="Giúp tránh ưu tiên quá mạnh cho sản phẩm có quá ít review.",
    )

    st.markdown("---")
    st.caption(
        f"Chế độ: {pipeline.get('analysis_mode', overview.get('analysis_mode', 'FAST'))}"
    )
    st.caption(
        f"Phạm vi: {fmt_int(pipeline.get('analysis_reviews', overview.get('reviews')))} review đã xử lý"
    )


# ============================================================
# 12. BỘ LỌC CHUNG
# ============================================================

filtered_products = product_summary.copy()

if selected_categories and "subcategory" in filtered_products.columns:
    filtered_products = filtered_products[
        filtered_products["subcategory"].isin(selected_categories)
    ]

if "reviews" in filtered_products.columns:
    filtered_products = filtered_products[
        filtered_products["reviews"] >= min_reviews
    ]

filtered_asins = set(
    filtered_products["parent_asin"].astype(str)
) if not filtered_products.empty else set()

filtered_risk = risk_full.copy()

if selected_categories and "subcategory" in filtered_risk.columns:
    filtered_risk = filtered_risk[
        filtered_risk["subcategory"].isin(selected_categories)
    ]

if "reviews" in filtered_risk.columns:
    filtered_risk = filtered_risk[
        filtered_risk["reviews"] >= min_reviews
    ]


# ============================================================
# PAGE 1 - TỔNG QUAN ĐIỀU HÀNH
# ============================================================

if page == "1. Tổng quan điều hành":

    hero(
        "Tổng quan điều hành",
        "Từ dữ liệu review đến ưu tiên hành động: sản phẩm nào cần chú ý, vì sao và nên làm gì tiếp theo.",
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi("Review đã phân tích", fmt_int(overview.get("reviews")), "Sau làm sạch")
    with c2:
        kpi("Số sản phẩm", fmt_int(overview.get("products")), "Trong tập phân tích")
    with c3:
        kpi("Điểm trung bình", f"{fmt_num(overview.get('avg_rating'))} ★", "Thang điểm 1–5")
    with c4:
        kpi("Tỷ lệ tiêu cực", fmt_pct(overview.get("negative_rate")), "Review 1–2 sao")
    with c5:
        kpi("Mua hàng xác minh", fmt_pct(overview.get("verified_rate")), "Verified Purchase")

    st.markdown('<div class="section-title">3 ưu tiên hành động</div>', unsafe_allow_html=True)

    if filtered_risk.empty:
        st.info("Không có sản phẩm phù hợp với bộ lọc hiện tại.")
    else:
        action_top3 = filtered_risk.sort_values("risk_score", ascending=False).head(3)

        cols = st.columns(3)
        for col, (_, r) in zip(cols, action_top3.iterrows()):
            with col:
                d = decision_for_product(r)
                decision_card(
                    f"{RISK_VI.get(r.get('risk_level'), r.get('risk_level'))} · {fmt_num(r.get('risk_score'), 1)}/100",
                    shorten(r.get("product_title"), 52),
                    f"<b>Vấn đề:</b> {d['aspect_vi']}<br>"
                    f"<b>Vì sao:</b> {d['reason']}<br>"
                    f"<b>Đề xuất:</b> {d['action']}",
                )

    # Insight tự động
    highest_negative_aspect = None
    highest_positive_aspect = None

    if not aspect_summary.empty:
        if "negative_rate" in aspect_summary.columns:
            rr = aspect_summary.sort_values(
                ["negative_rate", "mentions"],
                ascending=[False, False]
            ).iloc[0]
            highest_negative_aspect = ASPECT_VI.get(rr["aspect"], rr["aspect"])

        if "positive_rate" in aspect_summary.columns:
            rr = aspect_summary.sort_values(
                ["positive_rate", "mentions"],
                ascending=[False, False]
            ).iloc[0]
            highest_positive_aspect = ASPECT_VI.get(rr["aspect"], rr["aspect"])

    newest_signal_text = "Chưa có tín hiệu nổi bật"
    if not emerging_full.empty:
        em = emerging_full.copy()
        if filtered_asins:
            em = em[em["parent_asin"].astype(str).isin(filtered_asins)]
        if not em.empty:
            rr = em.sort_values("signal_score", ascending=False).iloc[0]
            newest_signal_text = (
                f"{ASPECT_VI.get(rr.get('aspect'), rr.get('aspect'))} · "
                f"{shorten(rr.get('product_title'), 36)}"
            )

    i1, i2, i3 = st.columns(3)

    with i1:
        decision_card(
            "Khách hàng không hài lòng nhất",
            highest_negative_aspect or "Chưa đủ dữ liệu",
            "Ưu tiên mở các sản phẩm có negative rate cao trong chủ đề này để xác định nguyên nhân lặp lại."
        )

    with i2:
        decision_card(
            "Điểm mạnh nổi bật",
            highest_positive_aspect or "Chưa đủ dữ liệu",
            "Có thể dùng nhóm phản hồi tích cực này để củng cố thông điệp sản phẩm, nhưng vẫn cần kiểm tra theo từng sản phẩm."
        )

    with i3:
        decision_card(
            "Tín hiệu cần theo dõi",
            newest_signal_text,
            "Đây là tín hiệu phân tích từ complaint trend, không phải kết luận rằng sản phẩm có lỗi hay không an toàn."
        )

    st.markdown('<div class="section-title">Danh sách ưu tiên xử lý</div>', unsafe_allow_html=True)

    action_table = build_action_table(filtered_risk, top_n=12)

    if not action_table.empty:
        st.dataframe(
            action_table[
                [
                    "Sản phẩm",
                    "Mức ưu tiên",
                    "Điểm ưu tiên",
                    "Vấn đề chính",
                    "Vì sao",
                    "Hành động đề xuất",
                    "Mức bằng chứng",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=430,
        )

    left, right = st.columns([1.3, 1])

    with left:
        st.markdown('<div class="section-title">Xu hướng review toàn tập dữ liệu</div>', unsafe_allow_html=True)

        if not monthly_trend.empty:
            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=monthly_trend["review_month"],
                    y=monthly_trend["reviews"],
                    name="Số review",
                    marker_color="#6366f1",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=monthly_trend["review_month"],
                    y=monthly_trend["negative_rate"],
                    name="Tỷ lệ tiêu cực",
                    yaxis="y2",
                    mode="lines+markers",
                    line=dict(color="#dc2626", width=3),
                )
            )

            fig.update_layout(
                height=420,
                hovermode="x unified",
                legend=dict(orientation="h", y=1.08),
                margin=dict(l=10, r=10, t=20, b=10),
                yaxis=dict(title="Số review"),
                yaxis2=dict(
                    title="Tỷ lệ tiêu cực",
                    overlaying="y",
                    side="right",
                    tickformat=".0%",
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section-title">Khía cạnh phản hồi</div>', unsafe_allow_html=True)

        if not aspect_summary.empty:
            temp = aspect_summary.copy()
            temp["Khía cạnh"] = temp["aspect"].map(ASPECT_VI).fillna(temp["aspect"])
            temp = temp.sort_values("negative_rate", ascending=True)

            fig = px.bar(
                temp,
                x="negative_rate",
                y="Khía cạnh",
                orientation="h",
                color="mentions",
                labels={
                    "negative_rate": "Tỷ lệ tiêu cực",
                    "mentions": "Lượt đề cập",
                },
            )
            fig.update_xaxes(tickformat=".0%")
            fig.update_layout(height=420, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        <div class="method-note">
            <b>Cách sử dụng trang này:</b> bắt đầu từ 3 ưu tiên hành động, sau đó mở trang
            <b>Sản phẩm cần chú ý</b> để sàng lọc danh sách và vào <b>Chi tiết sản phẩm</b>
            để xem nguyên nhân, xu hướng, review bằng chứng trước khi ra quyết định.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE 2 - SẢN PHẨM CẦN CHÚ Ý
# ============================================================

elif page == "2. Sản phẩm cần chú ý":

    hero(
        "Sản phẩm cần chú ý",
        "Sàng lọc danh sách ưu tiên theo mức rủi ro phân tích, bằng chứng review và hành động đề xuất.",
    )

    st.markdown(
        """
        <div class="risk-note">
            <b>Quan trọng:</b> “Điểm ưu tiên” là chỉ số hỗ trợ sắp xếp thứ tự kiểm tra
            dựa trên tiếng nói khách hàng. Chỉ số này không phải chứng nhận an toàn,
            không xác nhận sản phẩm có lỗi và không thay thế đánh giá chuyên môn.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if filtered_risk.empty:
        st.info("Không có sản phẩm phù hợp với bộ lọc.")
    else:
        f1, f2 = st.columns([1, 2])

        with f1:
            risk_filter_vi = st.selectbox(
                "Mức ưu tiên",
                ["Tất cả", "Rất cao", "Cao", "Trung bình", "Thấp"],
            )

        with f2:
            query = st.text_input(
                "Tìm sản phẩm / cửa hàng / Parent ASIN",
                placeholder="Ví dụ: bottle, diaper, Fisher-Price..."
            )

        temp = filtered_risk.copy()

        if risk_filter_vi != "Tất cả":
            risk_reverse = {v: k for k, v in RISK_VI.items()}
            temp = temp[temp["risk_level"] == risk_reverse[risk_filter_vi]]

        if query.strip():
            q = query.strip().lower()
            mask = pd.Series(False, index=temp.index)

            for col in ["product_title", "store", "parent_asin"]:
                if col in temp.columns:
                    mask = mask | (
                        temp[col]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                        .str.contains(q, regex=False)
                    )

            temp = temp[mask]

        if temp.empty:
            st.info("Không có sản phẩm phù hợp.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Sản phẩm", fmt_int(len(temp)))
            c2.metric("Rất cao", fmt_int((temp["risk_level"] == "Critical").sum()))
            c3.metric("Cao", fmt_int((temp["risk_level"] == "High").sum()))
            c4.metric("Điểm ưu tiên trung vị", fmt_num(temp["risk_score"].median(), 1))

            chart_df = temp.sort_values("risk_score", ascending=False).head(20).copy()
            chart_df["Tên sản phẩm"] = chart_df["product_title"].apply(lambda x: shorten(x, 42))

            fig = px.bar(
                chart_df.sort_values("risk_score"),
                x="risk_score",
                y="Tên sản phẩm",
                orientation="h",
                color="risk_level",
                color_discrete_map={
                    "Critical": "#dc2626",
                    "High": "#f97316",
                    "Medium": "#eab308",
                    "Low": "#16a34a",
                },
                labels={
                    "risk_score": "Điểm ưu tiên",
                    "risk_level": "Mức ưu tiên",
                },
                hover_data={
                    "product_title": True,
                    "store": True,
                    "subcategory": True,
                    "reviews": True,
                    "avg_rating": ":.2f",
                    "negative_rate": ":.1%",
                    "Tên sản phẩm": False,
                },
            )
            fig.update_layout(height=650)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Bảng hỗ trợ quyết định")

            actions = build_action_table(temp, top_n=min(30, len(temp)))

            st.dataframe(
                actions,
                use_container_width=True,
                hide_index=True,
                height=560,
            )

            st.download_button(
                "⬇️ Tải danh sách ưu tiên CSV",
                data=actions.to_csv(index=False).encode("utf-8-sig"),
                file_name="danh_sach_uu_tien_san_pham.csv",
                mime="text/csv",
            )


# ============================================================
# PAGE 3 - CHI TIẾT SẢN PHẨM
# ============================================================

elif page == "3. Chi tiết sản phẩm":

    hero(
        "Chi tiết sản phẩm",
        "Drill-down từ cảnh báo đến nguyên nhân, mức độ bằng chứng, xu hướng và review gốc.",
    )

    if filtered_products.empty:
        st.info("Không có sản phẩm phù hợp với bộ lọc.")
    else:
        choices = filtered_products.sort_values("reviews", ascending=False).head(1000).copy()

        q = st.text_input(
            "🔎 Tìm sản phẩm",
            placeholder="Nhập tên sản phẩm, store hoặc Parent ASIN"
        ).strip().lower()

        if q:
            mask = pd.Series(False, index=choices.index)
            for col in ["product_title", "store", "parent_asin"]:
                if col in choices.columns:
                    mask = mask | (
                        choices[col]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                        .str.contains(q, regex=False)
                    )
            choices = choices[mask]

        if choices.empty:
            st.info("Không tìm thấy sản phẩm.")
        else:
            choices["label"] = choices.apply(lambda r: product_label(r, 62), axis=1)

            selected_label = st.selectbox(
                "Chọn sản phẩm",
                choices["label"].tolist(),
            )

            row = choices[choices["label"] == selected_label].iloc[0]
            asin = str(row.get("parent_asin"))

            st.markdown(f"## {clean_text(row.get('product_title'), 'Không rõ tên sản phẩm')}")
            st.caption(
                f"Cửa hàng / thương hiệu: {clean_text(row.get('store'))} · "
                f"Danh mục: {clean_text(row.get('subcategory'))} · "
                f"Parent ASIN: {asin}"
            )

            risk_row = pd.DataFrame()
            if not risk_full.empty:
                risk_row = risk_full[risk_full["parent_asin"].astype(str) == asin]

            # Nếu sản phẩm không nằm trong risk table, tạo row kết hợp tối thiểu từ product_summary
            if risk_row.empty:
                effective_risk_row = row.copy()
                effective_risk_row["risk_score"] = np.nan
                effective_risk_row["risk_level"] = "Low"
            else:
                effective_risk_row = risk_row.iloc[0]

            d = decision_for_product(effective_risk_row)

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Điểm trung bình", f"{fmt_num(row.get('avg_rating'))} ★")
            c2.metric("Số review", fmt_int(row.get("reviews")))
            c3.metric("Tỷ lệ tiêu cực", fmt_pct(row.get("negative_rate")))
            c4.metric("Verified Purchase", fmt_pct(row.get("verified_rate")))
            c5.metric("Giá", fmt_money(row.get("price")))
            c6.metric(
                "Điểm ưu tiên",
                fmt_num(effective_risk_row.get("risk_score"), 1)
            )

            st.markdown("### Kết luận quản trị")

            dc1, dc2, dc3 = st.columns(3)

            with dc1:
                decision_card(
                    "Ưu tiên",
                    d["priority"],
                    f"Mức phân tích: {RISK_VI.get(effective_risk_row.get('risk_level'), effective_risk_row.get('risk_level', 'Không rõ'))}"
                )

            with dc2:
                decision_card(
                    "Vấn đề chính",
                    d["aspect_vi"],
                    d["reason"],
                )

            with dc3:
                decision_card(
                    "Mức bằng chứng",
                    d["evidence"],
                    d["evidence_note"],
                )

            st.success(f"**Hành động đề xuất:** {d['action']}")

            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                [
                    "Tổng quan nguyên nhân",
                    "Xu hướng",
                    "Review bằng chứng",
                    "Lời hứa & trải nghiệm",
                    "So sánh sản phẩm",
                ]
            )

            # ----------------------------------------------------
            # TAB 1 - BREAKDOWN RISK + ASPECT
            # ----------------------------------------------------
            with tab1:
                left, right = st.columns([1, 1.15])

                with left:
                    st.markdown("#### Điểm ưu tiên được tạo từ đâu?")

                    if not risk_row.empty:
                        comp = risk_components(effective_risk_row)
                        comp_df = pd.DataFrame({
                            "Thành phần": list(comp.keys()),
                            "Điểm đóng góp": list(comp.values()),
                            "Trọng số tối đa": [35, 35, 20, 10],
                        })

                        fig = px.bar(
                            comp_df,
                            x="Điểm đóng góp",
                            y="Thành phần",
                            orientation="h",
                            text="Điểm đóng góp",
                            labels={"Điểm đóng góp": "Điểm đóng góp vào Risk Score"},
                        )
                        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                        fig.update_xaxes(range=[0, 35])
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)

                        st.caption(
                            "Risk Score = 35% tỷ lệ review tiêu cực + 35% tín hiệu bất thường "
                            "+ 20% thành phần rating thấp + 10% helpful votes. "
                            "Các thành phần được chuẩn hóa trong pipeline."
                        )
                    else:
                        st.info("Sản phẩm này không có bản ghi Risk Score trong web bundle.")

                with right:
                    st.markdown("#### Khía cạnh trải nghiệm")

                    asp = aspect_product_full[
                        aspect_product_full["parent_asin"].astype(str) == asin
                    ].copy() if not aspect_product_full.empty else pd.DataFrame()

                    if not asp.empty:
                        asp["Khía cạnh"] = asp["aspect"].map(ASPECT_VI).fillna(asp["aspect"])
                        asp = asp.sort_values("negative_rate", ascending=True)

                        fig = px.bar(
                            asp,
                            x="negative_rate",
                            y="Khía cạnh",
                            orientation="h",
                            color="mentions",
                            labels={
                                "negative_rate": "Tỷ lệ tiêu cực",
                                "mentions": "Lượt đề cập",
                            },
                        )
                        fig.update_xaxes(tickformat=".0%")
                        fig.update_layout(height=350, coloraxis_showscale=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Chưa có dữ liệu khía cạnh cho sản phẩm này.")

                st.markdown("#### Tín hiệu phản hồi đang tăng")

                em = emerging_full[
                    emerging_full["parent_asin"].astype(str) == asin
                ].copy() if not emerging_full.empty else pd.DataFrame()

                if not em.empty:
                    em["Khía cạnh"] = em["aspect"].map(ASPECT_VI).fillna(em["aspect"])
                    em["Mức tín hiệu"] = em["signal_level"].map(SIGNAL_VI).fillna(em["signal_level"])

                    em_show = em.sort_values("signal_score", ascending=False).head(12).copy()

                    cols = [
                        c for c in [
                            "Khía cạnh",
                            "review_month",
                            "complaints",
                            "complaint_rate",
                            "growth_pct",
                            "z_score",
                            "signal_score",
                            "Mức tín hiệu",
                        ]
                        if c in em_show.columns
                    ]

                    em_show = em_show[cols].rename(columns={
                        "review_month": "Tháng",
                        "complaints": "Số khiếu nại",
                        "complaint_rate": "Tỷ lệ khiếu nại",
                        "growth_pct": "Mức tăng",
                        "z_score": "Z-score",
                        "signal_score": "Điểm tín hiệu",
                    })

                    st.dataframe(em_show, use_container_width=True, hide_index=True)

                    st.caption(
                        "Complaint rate được ưu tiên hơn số khiếu nại tuyệt đối để tránh "
                        "nhầm sản phẩm có nhiều review với sản phẩm có vấn đề tăng bất thường."
                    )
                else:
                    st.info("Chưa phát hiện tín hiệu complaint tăng bất thường cho sản phẩm này.")

            # ----------------------------------------------------
            # TAB 2 - TREND
            # ----------------------------------------------------
            with tab2:
                trend = product_monthly[
                    product_monthly["parent_asin"].astype(str) == asin
                ].copy() if not product_monthly.empty else pd.DataFrame()

                if trend.empty:
                    st.info("Sản phẩm này không nằm trong tập product-monthly được xuất cho dashboard.")
                else:
                    trend = trend.sort_values("review_month")

                    fig = go.Figure()

                    fig.add_trace(
                        go.Bar(
                            x=trend["review_month"],
                            y=trend["reviews"],
                            name="Số review",
                            marker_color="#6366f1",
                        )
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=trend["review_month"],
                            y=trend["negative_rate"],
                            name="Tỷ lệ tiêu cực",
                            yaxis="y2",
                            mode="lines+markers",
                            line=dict(color="#dc2626", width=3),
                        )
                    )

                    fig.update_layout(
                        height=470,
                        hovermode="x unified",
                        legend=dict(orientation="h", y=1.08),
                        yaxis=dict(title="Số review"),
                        yaxis2=dict(
                            title="Tỷ lệ tiêu cực",
                            overlaying="y",
                            side="right",
                            tickformat=".0%",
                        ),
                    )

                    st.plotly_chart(fig, use_container_width=True)

            # ----------------------------------------------------
            # TAB 3 - REVIEWS
            # ----------------------------------------------------
            with tab3:
                rv = representative_reviews[
                    representative_reviews["parent_asin"].astype(str) == asin
                ].copy() if not representative_reviews.empty else pd.DataFrame()

                if rv.empty:
                    st.info("Không có review đại diện được xuất cho sản phẩm này.")
                else:
                    f1, f2 = st.columns(2)

                    with f1:
                        sent_choice = st.selectbox(
                            "Cảm xúc theo rating",
                            ["Tất cả", "Tiêu cực", "Trung lập", "Tích cực"],
                            key="review_sentiment_filter",
                        )

                    with f2:
                        verified_only = st.checkbox(
                            "Chỉ review Verified Purchase",
                            value=False,
                        )

                    if sent_choice != "Tất cả":
                        reverse_sent = {v: k for k, v in SENTIMENT_VI.items()}
                        rv = rv[rv["rating_sentiment"] == reverse_sent[sent_choice]]

                    if verified_only and "verified_purchase" in rv.columns:
                        rv = rv[rv["verified_purchase"] == True]

                    rv = rv.sort_values(
                        ["helpful_vote", "review_date"],
                        ascending=[False, False]
                    )

                    for _, rr in rv.head(20).iterrows():
                        rating = safe_float(rr.get("rating"), 0)
                        sentiment = SENTIMENT_VI.get(
                            rr.get("rating_sentiment"),
                            rr.get("rating_sentiment", "")
                        )

                        with st.expander(
                            f"{rating:.0f}★ · {sentiment} · Helpful: {fmt_int(rr.get('helpful_vote'))}"
                        ):
                            if clean_text(rr.get("title"), ""):
                                st.markdown(f"**{clean_text(rr.get('title'), '')}**")

                            st.write(clean_text(rr.get("text"), "Không có nội dung"))

                            st.caption(
                                f"Ngày review: {rr.get('review_date')} · "
                                f"Verified Purchase: {bool_vi(rr.get('verified_purchase'))}"
                            )

            # ----------------------------------------------------
            # TAB 4 - CLAIM VS EXPERIENCE
            # ----------------------------------------------------
            with tab4:
                cl = claim_full[
                    claim_full["parent_asin"].astype(str) == asin
                ].copy() if not claim_full.empty else pd.DataFrame()

                if cl.empty:
                    st.info("Chưa có dữ liệu đối chiếu lời hứa và trải nghiệm cho sản phẩm này.")
                else:
                    cl["Khía cạnh"] = cl["aspect"].map(ASPECT_VI).fillna(cl["aspect"])
                    cl["Kết luận"] = cl["experience_label"].map(EXPERIENCE_VI).fillna(cl["experience_label"])

                    show = cl[
                        [
                            c for c in [
                                "Khía cạnh",
                                "mentions",
                                "positive_rate",
                                "negative_rate",
                                "Kết luận",
                            ]
                            if c in cl.columns
                        ]
                    ].rename(columns={
                        "mentions": "Lượt đề cập",
                        "positive_rate": "Tỷ lệ tích cực",
                        "negative_rate": "Tỷ lệ tiêu cực",
                    })

                    st.dataframe(
                        show.sort_values("Lượt đề cập", ascending=False),
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.caption(
                        "Kết quả này phản ánh mức độ tương thích giữa các đặc tính được theo dõi "
                        "và trải nghiệm trong review; không phải kiểm định kỹ thuật của sản phẩm."
                    )

            # ----------------------------------------------------
            # TAB 5 - PRODUCT COMPARISON
            # ----------------------------------------------------
            with tab5:
                compare_pool = filtered_products.copy()
                compare_pool["label"] = compare_pool.apply(
                    lambda r: product_label(r, 48),
                    axis=1
                )

                default_labels = [selected_label]

                compare_labels = st.multiselect(
                    "Chọn 2–4 sản phẩm để so sánh",
                    compare_pool["label"].tolist(),
                    default=default_labels,
                    max_selections=4,
                )

                if len(compare_labels) < 2:
                    st.info("Chọn thêm ít nhất 1 sản phẩm để so sánh.")
                else:
                    comp = compare_pool[
                        compare_pool["label"].isin(compare_labels)
                    ].copy()

                    comp["Tên sản phẩm"] = comp["product_title"].apply(
                        lambda x: shorten(x, 45)
                    )

                    metric_df = comp[
                        [
                            c for c in [
                                "Tên sản phẩm",
                                "avg_rating",
                                "negative_rate",
                                "verified_rate",
                                "reviews",
                                "price",
                            ]
                            if c in comp.columns
                        ]
                    ].rename(columns={
                        "avg_rating": "Điểm TB",
                        "negative_rate": "Tỷ lệ tiêu cực",
                        "verified_rate": "Verified Purchase",
                        "reviews": "Số review",
                        "price": "Giá",
                    })

                    st.dataframe(metric_df, use_container_width=True, hide_index=True)

                    selected_compare_asins = comp["parent_asin"].astype(str).tolist()

                    asp_comp = aspect_product_full[
                        aspect_product_full["parent_asin"].astype(str).isin(selected_compare_asins)
                    ].copy() if not aspect_product_full.empty else pd.DataFrame()

                    if not asp_comp.empty:
                        title_map = dict(
                            zip(
                                comp["parent_asin"].astype(str),
                                comp["Tên sản phẩm"]
                            )
                        )
                        asp_comp["Sản phẩm"] = (
                            asp_comp["parent_asin"]
                            .astype(str)
                            .map(title_map)
                        )
                        asp_comp["Khía cạnh"] = asp_comp["aspect"].map(ASPECT_VI).fillna(asp_comp["aspect"])

                        fig = px.bar(
                            asp_comp,
                            x="Khía cạnh",
                            y="negative_rate",
                            color="Sản phẩm",
                            barmode="group",
                            labels={"negative_rate": "Tỷ lệ tiêu cực"},
                        )
                        fig.update_yaxes(tickformat=".0%")
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PAGE 4 - TIẾNG NÓI KHÁCH HÀNG
# ============================================================

elif page == "4. Tiếng nói khách hàng":

    hero(
        "Tiếng nói khách hàng",
        "Tự động tóm tắt khách hàng đang thích gì, không hài lòng gì và chủ đề nào đang tăng.",
    )

    if aspect_summary.empty:
        st.info("Chưa có dữ liệu khía cạnh.")
    else:
        asp = aspect_summary.copy()
        asp["Khía cạnh"] = asp["aspect"].map(ASPECT_VI).fillna(asp["aspect"])

        most_mentioned = asp.sort_values("mentions", ascending=False).iloc[0]
        most_negative = asp.sort_values(
            ["negative_rate", "mentions"],
            ascending=[False, False]
        ).iloc[0]
        most_positive = asp.sort_values(
            ["positive_rate", "mentions"],
            ascending=[False, False]
        ).iloc[0]

        fastest = None
        if not emerging_full.empty:
            em = emerging_full.copy()
            if filtered_asins:
                em = em[em["parent_asin"].astype(str).isin(filtered_asins)]
            if not em.empty:
                fastest = em.sort_values("signal_score", ascending=False).iloc[0]

        i1, i2, i3, i4 = st.columns(4)

        with i1:
            decision_card(
                "Được nhắc nhiều nhất",
                most_mentioned["Khía cạnh"],
                f"{fmt_int(most_mentioned.get('mentions'))} lượt đề cập"
            )

        with i2:
            decision_card(
                "Phàn nàn cao nhất",
                most_negative["Khía cạnh"],
                f"Tỷ lệ tiêu cực {fmt_pct(most_negative.get('negative_rate'))}"
            )

        with i3:
            decision_card(
                "Được đánh giá tích cực nhất",
                most_positive["Khía cạnh"],
                f"Tỷ lệ tích cực {fmt_pct(most_positive.get('positive_rate'))}"
            )

        with i4:
            if fastest is not None:
                decision_card(
                    "Tín hiệu tăng mạnh nhất",
                    ASPECT_VI.get(fastest.get("aspect"), fastest.get("aspect")),
                    shorten(fastest.get("product_title"), 38)
                )
            else:
                decision_card(
                    "Tín hiệu tăng mạnh nhất",
                    "Chưa đủ dữ liệu",
                    "Không có emerging issue phù hợp bộ lọc."
                )

        tab1, tab2, tab3 = st.tabs(
            [
                "Bản đồ phản hồi",
                "Vấn đề đang tăng",
                "NLP & sai lệch rating-text",
            ]
        )

        with tab1:
            left, right = st.columns(2)

            with left:
                fig = px.bar(
                    asp.sort_values("mentions"),
                    x="mentions",
                    y="Khía cạnh",
                    orientation="h",
                    color="negative_rate",
                    color_continuous_scale="RdYlGn_r",
                    labels={
                        "mentions": "Lượt đề cập",
                        "negative_rate": "Tỷ lệ tiêu cực",
                    },
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

            with right:
                fig = px.scatter(
                    asp,
                    x="mentions",
                    y="negative_rate",
                    size="helpful_votes",
                    hover_name="Khía cạnh",
                    color="verified_rate",
                    labels={
                        "mentions": "Lượt đề cập",
                        "negative_rate": "Tỷ lệ tiêu cực",
                        "verified_rate": "Verified Purchase",
                        "helpful_votes": "Helpful votes",
                    },
                )
                fig.update_yaxes(tickformat=".0%")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                f"""
                <div class="insight">
                    <b>Diễn giải:</b> “{most_negative['Khía cạnh']}” đang có tỷ lệ phản hồi tiêu cực
                    cao nhất trong các khía cạnh được theo dõi. Tuy nhiên, cần mở sản phẩm và review
                    cụ thể trước khi kết luận nguyên nhân vì chỉ số tổng hợp có thể trộn nhiều sản phẩm khác nhau.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with tab2:
            if emerging_full.empty:
                st.info("Chưa có dữ liệu vấn đề đang tăng.")
            else:
                em = emerging_full.copy()

                if filtered_asins:
                    em = em[em["parent_asin"].astype(str).isin(filtered_asins)]

                em["Khía cạnh"] = em["aspect"].map(ASPECT_VI).fillna(em["aspect"])
                em["Mức tín hiệu"] = em["signal_level"].map(SIGNAL_VI).fillna(em["signal_level"])

                top_em = em.sort_values("signal_score", ascending=False).head(40).copy()

                show = top_em[
                    [
                        c for c in [
                            "product_name_short",
                            "store",
                            "Khía cạnh",
                            "review_month",
                            "complaints",
                            "complaint_rate",
                            "growth_pct",
                            "signal_score",
                            "Mức tín hiệu",
                        ]
                        if c in top_em.columns
                    ]
                ].rename(columns={
                    "product_name_short": "Sản phẩm",
                    "store": "Cửa hàng / thương hiệu",
                    "review_month": "Tháng",
                    "complaints": "Số khiếu nại",
                    "complaint_rate": "Tỷ lệ khiếu nại",
                    "growth_pct": "Mức tăng",
                    "signal_score": "Điểm tín hiệu",
                })

                st.dataframe(show, use_container_width=True, hide_index=True, height=520)

        with tab3:
            c1, c2, c3 = st.columns(3)
            c1.metric("Review NLP", fmt_int(nlp_validation.get("sample_rows")))
            c2.metric("Rating-text mismatch", fmt_int(nlp_validation.get("mismatch_rows")))
            c3.metric("Tỷ lệ mismatch", fmt_pct(nlp_validation.get("mismatch_rate")))

            st.caption(
                f"Mô hình: {nlp_validation.get('model', 'Không rõ')} · "
                f"Thiết bị: {nlp_validation.get('device', 'Không rõ')}"
            )

            st.info(
                "Rating-text mismatch dùng để tìm review cần đọc lại, không phải bằng chứng rằng "
                "rating hoặc mô hình NLP chắc chắn sai."
            )

            if not nlp_sample.empty and "rating_text_mismatch" in nlp_sample.columns:
                mm = nlp_sample[nlp_sample["rating_text_mismatch"] == True].copy()

                if not mm.empty:
                    mm["Sản phẩm"] = mm["product_title"].apply(lambda x: shorten(x, 48))
                    mm["Cảm xúc rating"] = mm["rating_sentiment"].map(SENTIMENT_VI).fillna(mm["rating_sentiment"])
                    mm["Cảm xúc văn bản"] = mm["text_sentiment"].map(SENTIMENT_VI).fillna(mm["text_sentiment"])

                    show = mm[
                        [
                            c for c in [
                                "Sản phẩm",
                                "rating",
                                "Cảm xúc rating",
                                "Cảm xúc văn bản",
                                "text_sentiment_score",
                                "text",
                            ]
                            if c in mm.columns
                        ]
                    ].rename(columns={
                        "rating": "Số sao",
                        "text_sentiment_score": "Độ tin cậy NLP",
                        "text": "Nội dung review",
                    })

                    st.dataframe(show.head(100), use_container_width=True, hide_index=True)


# ============================================================
# PAGE 5 - BIG DATA & PHƯƠNG PHÁP
# ============================================================

elif page == "5. Big Data & phương pháp":

    hero(
        "Big Data & phương pháp",
        "Minh chứng vai trò trung tâm của Apache Spark, quy trình phân tích, NLP và các giới hạn cần lưu ý.",
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Spark", str(pipeline.get("spark_version", "—")))
    c2.metric("Dòng phân tích", fmt_int(pipeline.get("analysis_reviews")))
    c3.metric("Metadata match", fmt_pct(pipeline.get("metadata_match_rate")))
    c4.metric("Aspect events", fmt_int(pipeline.get("aspect_events")))
    c5.metric("NLP sample", fmt_int(pipeline.get("nlp_sample_rows")))

    st.markdown("### Quy trình Big Data")

    st.code(
        """
Amazon Reviews + Product Metadata
                ↓
          Google Drive
                ↓
          Apache Spark
                ↓
      Schema + Clean + Filter
                ↓
     Join Review ↔ Metadata
                ↓
   Aggregation / Spark SQL / Window
                ↓
      Aspect & Complaint Mining
                ↓
     Emerging Issue Detection
                ↓
       Risk Prioritization
                ↓
        Transformer NLP
                ↓
   Parquet / JSON Web Bundle
                ↓
       Streamlit Dashboard
                ↓
        Decision Support
        """,
        language="text",
    )

    st.markdown("### Phạm vi thực nghiệm")

    st.markdown(
        f"""
        <div class="method-note">
            <b>Dataset phân tích:</b> {fmt_int(pipeline.get('analysis_reviews'))} review sau làm sạch /
            join, từ bounded workload tối đa {fmt_int(pipeline.get('configured_max_reviews'))} review.<br>
            <b>Aspect mining:</b> tối đa {fmt_int(pipeline.get('max_aspect_reviews'))} review.<br>
            <b>Negative complaint workload:</b> tối đa {fmt_int(pipeline.get('max_negative_complaint_reviews'))} review tiêu cực.<br>
            <b>Transformer NLP:</b> {fmt_int(pipeline.get('nlp_sample_rows'))} review.<br><br>
            Các chỉ số dashboard phản ánh <b>tập dữ liệu thực nghiệm đã xử lý</b>,
            không được diễn giải là thống kê đầy đủ của toàn bộ Amazon Baby Products.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Risk Score minh bạch")

    risk_formula = pd.DataFrame({
        "Thành phần": [
            "Tỷ lệ review tiêu cực",
            "Tín hiệu phản hồi tăng bất thường",
            "Thành phần rating thấp",
            "Helpful votes",
        ],
        "Trọng số": [35, 35, 20, 10],
        "Ý nghĩa": [
            "Sản phẩm có nhiều review 1–2 sao tương đối hơn.",
            "Complaint rate xuất hiện xu hướng bất thường theo thời gian.",
            "Điểm rating trung bình thấp làm tăng mức ưu tiên.",
            "Phản hồi được nhiều người đánh dấu hữu ích có trọng số bổ sung.",
        ],
    })

    st.dataframe(risk_formula, use_container_width=True, hide_index=True)

    st.warning(
        "Risk Score là chỉ số ưu tiên phân tích 0–100, không phải xác suất sản phẩm lỗi, "
        "không phải chứng nhận an toàn và không thay thế đánh giá chuyên môn."
    )

    left, right = st.columns([1.05, 1])

    with left:
        st.markdown("### Benchmark Apache Spark")

        if not spark_benchmark.empty:
            fig = px.bar(
                spark_benchmark,
                x="target_rows",
                y="seconds",
                text="seconds",
                labels={
                    "target_rows": "Số dòng mục tiêu",
                    "seconds": "Thời gian (giây)",
                },
            )
            fig.update_traces(
                texttemplate="%{text:.3f}s",
                textposition="outside",
            )
            fig.update_layout(height=390)
            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                "Các phép đo benchmark là thời gian quan sát trong phiên chạy thực nghiệm. "
                "Không nên diễn giải tuyến tính vì JVM warm-up, cache và Adaptive Query Execution "
                "có thể ảnh hưởng kết quả."
            )

    with right:
        st.markdown("### Chất lượng dữ liệu")

        if not data_quality.empty:
            st.dataframe(
                data_quality,
                use_container_width=True,
                hide_index=True,
                height=390,
            )

    st.markdown("### Các giới hạn quan trọng")

    st.markdown(
        """
        - Bounded workload giúp pipeline chạy phù hợp với tài nguyên Colab nhưng có thể chịu ảnh hưởng bởi thứ tự dữ liệu nguồn.
        - Emerging issue dựa trên complaint rate và baseline theo các quan sát thời gian có sẵn; đây là tín hiệu cảnh báo phân tích.
        - Transformer NLP chỉ chạy trên mẫu để kiểm soát chi phí tính toán.
        - Verified Purchase không đồng nghĩa review “đúng hơn”; đây chỉ là một thuộc tính bổ sung.
        - Các phản hồi liên quan an toàn chỉ được xem là “safety-related review signals”, không phải kết luận sản phẩm không an toàn.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Ứng dụng Apache Spark và NLP trong khai phá tiếng nói khách hàng
        và hỗ trợ ưu tiên quyết định đối với Baby Products trên Amazon
    </div>
    """,
    unsafe_allow_html=True,
)
