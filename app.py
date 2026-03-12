import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# 嘗試載入 Google Sheets 連線套件
try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="馬尼通訊 | 人員評核系統",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS：完全不碰 sidebar、header、toolbar 的 DOM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700;900&family=DM+Mono:wght@400;500&display=swap');

    :root {
        --bg-base:       #F0F2F7;
        --bg-surface:    #FFFFFF;
        --bg-elevated:   #F7F8FC;
        --bg-hover:      #EEF0F8;
        --border:        #DDE1EE;
        --border-light:  #C8CEDE;
        --text-primary:  #1A1F36;
        --text-secondary:#4A5178;
        --text-muted:    #8B93B0;
        --accent-blue:   #3B6FE8;
        --accent-teal:   #0EAFA0;
        --accent-amber:  #D4820A;
        --accent-rose:   #D94F7A;
        --accent-violet: #6C4FD4;
    }

    /* ===== 主體背景 ===== */
    .stApp { background-color: var(--bg-base) !important; }
    .stApp * { font-family: 'Noto Sans TC', sans-serif; }

    /* ===== 主內容區 ===== */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 96%;
    }

    /* ===== 側邊欄樣式（只美化，不控制顯示） ===== */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* ===== 側邊欄 Radio 美化 ===== */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 4px !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        cursor: pointer !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        transition: background 0.15s !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: var(--bg-hover) !important;
    }

    /* ===== 原生容器卡片 ===== */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 24px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.02) !important;
        margin-bottom: 16px !important;
    }

    /* ===== 頁面大標題 ===== */
    .page-header-inner {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 22px 28px 22px 34px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(59,111,232,0.06);
        position: relative;
        margin-bottom: 24px;
        overflow: hidden;
    }
    .page-header-inner::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, var(--accent-blue) 0%, var(--accent-teal) 100%);
        border-radius: 16px 0 0 16px;
    }
    .page-header-icon-wrap {
        width: 54px; height: 54px; flex-shrink: 0;
        background: linear-gradient(135deg, rgba(59,111,232,0.10) 0%, rgba(14,175,160,0.07) 100%);
        border: 1px solid rgba(59,111,232,0.16);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px;
    }
    .page-header-text h2 {
        margin: 0 0 5px 0;
        color: var(--text-primary);
        font-size: 22px; font-weight: 800;
        line-height: 1.2;
    }
    .page-header-text p {
        margin: 0;
        color: var(--text-muted);
        font-size: 13px;
    }

    /* ===== 步驟標籤 ===== */
    .section-label {
        display: flex; align-items: center; gap: 10px;
        font-size: 14px; font-weight: 800;
        color: var(--text-primary); letter-spacing: 1px;
        margin: 0 0 20px 0; padding-bottom: 14px;
        border-bottom: 2px solid var(--bg-hover);
    }
    .section-label span {
        display: inline-flex; align-items: center; justify-content: center;
        width: 24px; height: 24px;
        background: var(--accent-blue);
        border-radius: 6px; font-size: 12px; font-weight: 800;
        color: white; flex-shrink: 0;
    }

    /* ===== 評分區塊標題 ===== */
    .score-section-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 13px 18px; border-radius: 10px; margin: 0 0 14px 0; border: 1px solid;
    }
    .ssh-a { background: rgba(14,175,160,0.05); border-color: rgba(14,175,160,0.22) !important; }
    .ssh-b { background: rgba(59,111,232,0.05); border-color: rgba(59,111,232,0.22) !important; }
    .ssh-c { background: rgba(212,130,10,0.05); border-color: rgba(212,130,10,0.22) !important; }
    .ssh-title { font-weight: 800; font-size: 13px; }
    .ssh-title-a { color: var(--accent-teal); }
    .ssh-title-b { color: var(--accent-blue); }
    .ssh-title-c { color: var(--accent-amber); }
    .ssh-badge { font-size: 11px; font-weight: 700; padding: 3px 12px; border-radius: 20px; font-family: 'DM Mono', monospace; }
    .ssh-badge-a { background: rgba(14,175,160,0.11); color: var(--accent-teal); }
    .ssh-badge-b { background: rgba(59,111,232,0.11); color: var(--accent-blue); }
    .ssh-badge-c { background: rgba(212,130,10,0.11); color: var(--accent-amber); }

    /* ===== 評分項目列 ===== */
    .score-item-container {
        background: var(--bg-surface); border: 1px solid var(--border);
        border-radius: 10px; padding: 14px 16px; margin-bottom: 12px;
    }
    .score-title-wrap { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
    .score-title { font-weight: 700; font-size: 14px; color: var(--text-primary); }
    .score-weight {
        font-size: 11px; color: var(--accent-blue);
        background: rgba(59,111,232,0.1); padding: 2px 6px;
        border-radius: 4px; font-family: 'DM Mono', monospace;
    }
    .score-help { font-size: 11px; color: var(--text-muted); line-height: 1.4; }
    .score-help-warn {
        font-size: 11px; color: #D4820A;
        background: rgba(212,130,10,0.08); padding: 3px 8px;
        border-radius: 4px; display: inline-block;
    }

    /* ===== 結果看板 ===== */
    .result-panel {
        background: var(--bg-surface); border: 1px solid var(--border);
        border-radius: 14px; padding: 28px 24px; text-align: center;
    }
    .result-score-label {
        font-size: 11px; font-weight: 700; color: var(--text-muted);
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;
    }
    .result-score-value {
        font-size: 56px; font-weight: 900; color: var(--text-primary);
        line-height: 1; font-family: 'DM Mono', monospace; margin-bottom: 14px;
    }
    .result-grade-badge {
        display: inline-block; padding: 6px 20px; border-radius: 24px;
        font-size: 14px; font-weight: 700; margin-bottom: 10px;
    }

    /* ===== 歷史卡片 ===== */
    .history-card {
        background: var(--bg-surface); border: 1px solid var(--border);
        border-radius: 12px; padding: 18px; margin-bottom: 12px;
    }
    .history-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
    .history-card-name { font-size: 16px; font-weight: 700; color: var(--text-primary); }
    .history-card-dept {
        font-size: 11px; color: var(--text-muted);
        background: var(--bg-elevated); border: 1px solid var(--border);
        padding: 2px 8px; border-radius: 6px;
    }
    .history-card-score {
        font-size: 28px; font-weight: 900;
        color: var(--text-primary); font-family: 'DM Mono', monospace;
    }

    /* ===== Streamlit 元件 ===== */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-size: 14px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(59,111,232,0.10) !important;
    }
    .stButton > button {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-light) !important;
        color: var(--text-secondary) !important;
        border-radius: 8px !important; font-weight: 600 !important;
        font-size: 13px !important; transition: all 0.15s !important;
    }
    .stButton > button:hover {
        background: var(--bg-hover) !important;
        border-color: var(--accent-blue) !important;
        color: var(--text-primary) !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--accent-blue) !important;
        border-color: var(--accent-blue) !important;
        color: white !important;
    }
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-violet) 100%) !important;
        border: none !important; color: white !important;
        font-size: 15px !important; font-weight: 700 !important;
        padding: 14px !important; border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(59,111,232,0.25) !important;
        width: 100% !important; margin-top: 10px;
    }
    [data-testid="stExpander"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* ===== 側邊欄 Logo 區 ===== */
    .sidebar-logo {
        background: linear-gradient(135deg, #EBF0FF 0%, #F7F8FC 100%);
        padding: 28px 20px 22px; border-bottom: 1px solid var(--border); text-align: center;
    }
    .sidebar-logo-icon { font-size: 44px; line-height: 1; }
    .sidebar-logo-title {
        color: var(--text-primary); font-size: 18px; font-weight: 700;
        letter-spacing: 3px; margin: 12px 0 4px 0;
    }
    .sidebar-logo-sub { color: var(--text-muted); font-size: 11px; letter-spacing: 1.5px; }

    /* ===== Footer ===== */
    .system-footer {
        text-align: center; padding: 30px 0; color: var(--text-muted);
        font-size: 12px; margin-top: 40px; border-top: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)


# --- 3. 核心功能 ---
def calculate_dynamic_bonus(score, rules_data):
    sorted_rules = sorted(rules_data, key=lambda x: x['min_score'], reverse=True)
    for rule in sorted_rules:
        if score >= rule['min_score']:
            return rule['grade'], rule['months'], rule['color']
    return "N/A", 0.0, "#8B93B0"

def update_target_content(dept, section, idx, key):
    new_value = st.session_state[key]
    st.session_state.config_data[dept][section][idx]['content'] = new_value

def get_gsheets_connection():
    spreadsheet_url = None
    json_str = None
    if st.secrets.get("connections") and st.secrets["connections"].get("gsheets"):
        spreadsheet_url = st.secrets["connections"]["gsheets"].get("spreadsheet")
    if st.secrets.get("gcp_service_account_json"):
        json_str = st.secrets.get("gcp_service_account_json")
    is_legacy = False
    if not json_str and st.secrets.get("connections") and st.secrets["connections"].get("gsheets") and "client_email" in st.secrets["connections"]["gsheets"]:
        is_legacy = True
    if not spreadsheet_url:
        return None, "未設定網址"
    temp_key_path = "/tmp/gsheets_key.json"
    os.makedirs("/tmp", exist_ok=True)
    try:
        if is_legacy:
            legacy = dict(st.secrets["connections"]["gsheets"])
            legacy.pop("spreadsheet", None)
            with open(temp_key_path, "w") as f: json.dump(legacy, f)
        else:
            with open(temp_key_path, "w") as f: json.dump(json.loads(json_str), f)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_key_path
        return st.connection("gsheets", type=GSheetsConnection), temp_key_path
    except Exception as e:
        return None, str(e)


# --- 4. 初始化資料 ---
if 'bonus_rules' not in st.session_state:
    st.session_state.bonus_rules = [
        {"grade": "S (特優)",   "min_score": 90, "months": 1.5, "color": "#D94F7A"},
        {"grade": "A (優良)",   "min_score": 80, "months": 1.0, "color": "#6C4FD4"},
        {"grade": "B+ (甲上)",  "min_score": 75, "months": 0.8, "color": "#3B6FE8"},
        {"grade": "B- (甲)",    "min_score": 70, "months": 0.6, "color": "#0EAFA0"},
        {"grade": "C (待改善)", "min_score": 60, "months": 0.5, "color": "#D4820A"},
        {"grade": "D (不合格)", "min_score": 0,  "months": 0.0, "color": "#8B93B0"},
    ]

if 'config_data' not in st.session_state:
    ECOMMERCE_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "訂單處理正確率", "weight": 0.30, "help": "【法遵紅線】不可扣底薪。100分: 0%錯誤; 85分: <0.5%"},
            {"item": "客服聊聊響應",   "weight": 0.30, "help": "【法遵紅線】僅限上班時間計入。"},
            {"item": "商城活動參與",   "weight": 0.20, "help": "主動提報與執行力。"},
            {"item": "上架與庫存準確", "weight": 0.20, "help": "【法遵紅線】標錯價屬重大疏失。"}
        ],
        "excellent": [
            {"item": "KR1: 滯銷品去化", "weight": 0.33, "help": "具體行動與成效"},
            {"item": "KR2: 價盤監控",   "weight": 0.33, "help": "市場價格敏銳度"},
            {"item": "KR3: 客單價提升", "weight": 0.34, "help": "組合銷售或加購推廣"}
        ],
        "threshold": 80,
        "text_a": [{"title": "O (目標): 維持優選賣家資格", "content": "1. 確保出貨零失誤\n2. 聊聊回應率維持 95% 以上"}],
        "text_b": [{"title": "O (目標): 提升賣場獲利結構", "content": "1. 降低庫存週轉天數\n2. 提高組合商品銷售比重"}]
    }
    MEDIA_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "短影音產出成效",  "weight": 0.30, "help": "100分: 12支+觀看破萬; 85分: 準時12支"},
            {"item": "官網SEO文章撰寫", "weight": 0.30, "help": "【法遵紅線】抄襲涉及著作權法。"},
            {"item": "社群互動維護",    "weight": 0.20, "help": "【法遵紅線】禁止下班要求回覆。"},
            {"item": "導流貢獻(ROAS)",  "weight": 0.20, "help": "100分: >50筆詢單"}
        ],
        "excellent": [
            {"item": "KR1: 爆款影片",     "weight": 0.33, "help": "流量突破性指標"},
            {"item": "KR2: 關鍵字排名",   "weight": 0.33, "help": "搜尋引擎首頁佔有率"},
            {"item": "KR3: 時事跟風速度", "weight": 0.34, "help": "社群熱度反應能力"}
        ],
        "threshold": 80,
        "text_a": [{"title": "O (目標): 建立流量護城河", "content": "1. 穩定產出高品質內容"}],
        "text_b": [{"title": "O (目標): 擴大品牌心佔率", "content": "讓馬尼成為台南 3C 資訊首選"}]
    }
    DESIGN_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "素材完成時效",  "weight": 0.30, "help": "100分: 提前1天完成; 85分: 準時"},
            {"item": "設計修改次數",  "weight": 0.30, "help": "100分: 一次過稿; 85分: 修改2次內"},
            {"item": "版權與品牌規範","weight": 0.20, "help": "【法遵紅線】盜版致侵權負賠償責任。"},
            {"item": "點擊率(CTR)",   "weight": 0.20, "help": "100分: 高於平均20%"}
        ],
        "excellent": [
            {"item": "KR1: A/B Test提案", "weight": 0.33, "help": "主動測試素材成效"},
            {"item": "KR2: AI工具應用",   "weight": 0.33, "help": "導入新工具提升效率"},
            {"item": "KR3: 視覺優化",     "weight": 0.34, "help": "品牌質感升級貢獻"}
        ],
        "threshold": 85,
        "text_a": [{"title": "O (目標): 視覺傳達精準化", "content": "1. 提升素材點擊率"}],
        "text_b": [{"title": "O (目標): 品牌視覺升級",   "content": "導入新工具提升質感"}]
    }
    GENERAL_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "作業準確度",    "weight": 0.25, "help": "【法遵紅線】導致政府罰款連動績效。"},
            {"item": "電商撥款對帳",  "weight": 0.35, "help": "防舞弊核心。100分: 完全一致"},
            {"item": "專案/發薪時效", "weight": 0.20, "help": "【法遵紅線】遲發薪水具勞檢風險。"},
            {"item": "跨部門協作",    "weight": 0.20, "help": "90分: 產出SOP無投訴"}
        ],
        "excellent": [
            {"item": "KR1: 流程優化", "weight": 0.33, "help": "簡化跨部門溝通成本"},
            {"item": "KR2: 成本控制", "weight": 0.33, "help": "減少非必要行政支出"},
            {"item": "KR3: 團隊支援", "weight": 0.34, "help": "突發事件支援度"}
        ],
        "threshold": 80,
        "text_a": [{"title": "O (目標): 營運零失誤", "content": "確保帳務/人事/行政流程順暢無誤"}],
        "text_b": [{"title": "O (目標): 提升組織效率", "content": "優化現有流程，降低溝通成本"}]
    }
    st.session_state.config_data = {
        "電商專員":      ECOMMERCE_TEMPLATE,
        "自媒體/行銷":   MEDIA_TEMPLATE,
        "社群編輯/美編": DESIGN_TEMPLATE,
        "會計/行政":     GENERAL_TEMPLATE,
    }

if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []
if 'calculated_score_data' not in st.session_state:
    st.session_state.calculated_score_data = None
if 'cloud_data_cache' not in st.session_state:
    st.session_state.cloud_data_cache = None
if 'logo_config' not in st.session_state:
    st.session_state.logo_config = {
        "use_image": False, "image_b64": None,
        "emoji": "💠", "company_name": "馬尼通訊", "system_name": "績效管理系統"
    }
if 'confirm_clear' not in st.session_state:
    st.session_state.confirm_clear = False

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST  = list(st.session_state.config_data.keys())


# ==========================================
# 側邊欄
# ==========================================
with st.sidebar:
    lc = st.session_state.logo_config
    if lc["use_image"] and lc["image_b64"]:
        logo_html = f'<img src="data:image/png;base64,{lc["image_b64"]}" style="width:72px;height:72px;object-fit:contain;border-radius:12px;">'
    else:
        logo_html = f'<div class="sidebar-logo-icon">{lc["emoji"]}</div>'

    st.markdown(f"""
    <div class="sidebar-logo">
        {logo_html}
        <div class="sidebar-logo-title">{lc["company_name"]}</div>
        <div class="sidebar-logo-sub">{lc["system_name"]}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    menu = st.radio(
        "導覽選單",
        ["📝 新增評核", "📋 雲端紀錄", "⚙️ 參數設定"],
        index=0,
        label_visibility="collapsed"
    )

    st.write("")

    if st.session_state.batch_queue:
        st.info(f"⏳ 待上傳 {len(st.session_state.batch_queue)} 筆紀錄")


# ==========================================
# 頁面 1：新增人員評核
# ==========================================
if menu == "📝 新增評核":
    st.markdown("""
    <div class="page-header-inner">
        <div class="page-header-icon-wrap">📝</div>
        <div class="page-header-text">
            <h2>新增人員評核</h2>
            <p>填寫基本資料與各維度評分，完成後執行計算</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1.15, 2], gap="large")

    with col_l:
        with st.container(border=True):
            st.markdown('<div class="section-label"><span>1</span>基本資料</div>', unsafe_allow_html=True)
            input_name       = st.text_input("受評人姓名", placeholder="輸入姓名...")
            input_supervisor = st.text_input("評分主管",   placeholder="直屬主管姓名...")
            col_d1, col_d2   = st.columns(2)
            with col_d1:
                input_dept  = st.selectbox("所屬部門", options=DEPT_LIST)
            with col_d2:
                input_level = st.selectbox("職稱職等", options=JOB_LEVELS)
            input_date = st.date_input("評核月份", value=datetime.now())

        current_config = st.session_state.config_data[input_dept]

        with st.container(border=True):
            st.markdown('<div class="section-label"><span>2</span>職務目標設定</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:12px;font-weight:700;color:#0EAFA0;margin-bottom:10px;">▸ A. 基礎目標 (KPI)</div>', unsafe_allow_html=True)
            for i, row in enumerate(current_config['text_a']):
                st.text_area(
                    row['title'], value=row['content'], height=80,
                    key=f"t_a_{input_dept}_{i}",
                    on_change=update_target_content,
                    args=(input_dept, 'text_a', i, f"t_a_{input_dept}_{i}")
                )
            st.markdown('<div style="font-size:12px;font-weight:700;color:#3B6FE8;margin:14px 0 10px;">▸ B. 挑戰目標 (OKR)</div>', unsafe_allow_html=True)
            for i, row in enumerate(current_config['text_b']):
                st.text_area(
                    row['title'], value=row['content'], height=80,
                    key=f"t_b_{input_dept}_{i}",
                    on_change=update_target_content,
                    args=(input_dept, 'text_b', i, f"t_b_{input_dept}_{i}")
                )

    with col_r:
        wa, wb, wc = current_config['section_weights']

        with st.form("score_form_v38", border=True):
            st.markdown('<div class="section-label"><span>3</span>績效評分維度</div>', unsafe_allow_html=True)

            # ── A 區 ──
            st.markdown(f"""
            <div class="score-section-header ssh-a">
                <span class="ssh-title ssh-title-a">A &nbsp;職務基本標準 (KPI)</span>
                <span class="ssh-badge ssh-badge-a">權重 {int(wa*100)}%</span>
            </div>
            """, unsafe_allow_html=True)

            scores_a = []
            for i, row in enumerate(current_config['basic']):
                is_warn = '法遵' in row.get('help', '')
                st.markdown('<div class="score-item-container">', unsafe_allow_html=True)
                c_lbl, c_val = st.columns([2.5, 1])
                with c_lbl:
                    help_block = ""
                    if row.get('help'):
                        cls    = "score-help-warn" if is_warn else "score-help"
                        prefix = "⚠ " if is_warn else "ℹ "
                        help_block = f'<div class="{cls}">{prefix}{row["help"]}</div>'
                    st.markdown(f"""
                    <div class="score-title-wrap">
                        <span class="score-title">{row['item']}</span>
                        <span class="score-weight">×{int(row['weight']*100)}%</span>
                    </div>
                    {help_block}
                    """, unsafe_allow_html=True)
                with c_val:
                    val = st.number_input(f"A{i}", -100, 100, 80, 5, key=f"va_{i}", label_visibility="collapsed")
                    scores_a.append(val * row['weight'])
                st.markdown('</div>', unsafe_allow_html=True)

            st.write("")

            # ── B 區 ──
            st.markdown(f"""
            <div class="score-section-header ssh-b">
                <span class="ssh-title ssh-title-b">B &nbsp;OKR 關鍵結果 (挑戰)</span>
                <span class="ssh-badge ssh-badge-b">權重 {int(wb*100)}%</span>
            </div>
            """, unsafe_allow_html=True)

            scores_b = []
            for i, row in enumerate(current_config['excellent']):
                is_warn = '法遵' in row.get('help', '')
                st.markdown('<div class="score-item-container">', unsafe_allow_html=True)
                c_lbl, c_val = st.columns([2.5, 1])
                with c_lbl:
                    help_block = ""
                    if row.get('help'):
                        cls    = "score-help-warn" if is_warn else "score-help"
                        prefix = "⚠ " if is_warn else "ℹ "
                        help_block = f'<div class="{cls}">{prefix}{row["help"]}</div>'
                    st.markdown(f"""
                    <div class="score-title-wrap">
                        <span class="score-title">{row['item']}</span>
                        <span class="score-weight">×{int(row['weight']*100)}%</span>
                    </div>
                    {help_block}
                    """, unsafe_allow_html=True)
                with c_val:
                    val = st.number_input(f"B{i}", 0, 100, 80, 5, key=f"vb_{i}", label_visibility="collapsed")
                    scores_b.append(val * row['weight'])
                st.markdown('</div>', unsafe_allow_html=True)

            st.write("")

            # ── C 區 ──
            st.markdown(f"""
            <div class="score-section-header ssh-c">
                <span class="ssh-title ssh-title-c">C &nbsp;主管綜合評核</span>
                <span class="ssh-badge ssh-badge-c">權重 {int(wc*100)}%</span>
            </div>
            """, unsafe_allow_html=True)

            col_c1, col_c2 = st.columns([1, 2.5])
            with col_c1:
                st.caption("綜合給分 (1–10)")
                c_mgr_score = st.selectbox("給分", options=range(1, 11), index=7, label_visibility="collapsed")
            with col_c2:
                st.caption("主管反饋建議（必填）")
                c_mgr_comment = st.text_area("反饋", placeholder="請輸入評價與改善建議...", height=100, label_visibility="collapsed")

            st.write("")
            submitted = st.form_submit_button("⚖ 執行計算並鎖定分數", use_container_width=True)

        if submitted:
            if not input_name:
                st.error("⚠ 請輸入受評人姓名！")
            else:
                raw_score   = (sum(scores_a) * wa) + (sum(scores_b) * wb) + (c_mgr_score * 10 * wc)
                final_score = max(0.0, min(100.0, raw_score))

                a_details    = [f"✓ {row['item']}: {st.session_state[f'va_{i}']}" for i, row in enumerate(current_config['basic'])]
                b_details    = [f"✓ {row['item']}: {st.session_state[f'vb_{i}']}" for i, row in enumerate(current_config['excellent'])]
                text_records = [f"【{row['title']}】\n{st.session_state.get(f't_a_{input_dept}_{i}', row['content'])}" for i, row in enumerate(current_config['text_a'])]
                text_records += [f"【{row['title']}】\n{st.session_state.get(f't_b_{input_dept}_{i}', row['content'])}" for i, row in enumerate(current_config['text_b'])]

                st.session_state.calculated_score_data = {
                    "score": final_score,
                    "meta": {
                        "name": input_name, "dept": input_dept,
                        "supervisor": input_supervisor, "date": str(input_date),
                        "level": input_level, "comment": c_mgr_comment,
                        "a_detail_str": "\n".join(a_details),
                        "b_detail_str": "\n".join(b_details),
                        "text_record_str": "\n\n".join(text_records)
                    }
                }
                st.toast("✅ 計算完成，請確認下方結果")

        # ── 結果區 ──
        if st.session_state.calculated_score_data:
            st.write("")
            res = st.session_state.calculated_score_data
            grade_t, grade_m, grade_c = calculate_dynamic_bonus(res['score'], st.session_state.bonus_rules)

            col_res1, col_res2 = st.columns(2, gap="large")

            with col_res1:
                with st.container(border=True):
                    st.markdown('<div class="section-label" style="margin-top:0;"><span>4</span>核定結果</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="result-panel">
                        <div class="result-score-label">最終核定總分</div>
                        <div class="result-score-value">{res['score']:.2f}</div>
                        <div class="result-grade-badge" style="background:{grade_c}22;color:{grade_c};border:1px solid {grade_c}44;">{grade_t}</div>
                        <div style="font-size:13px;color:var(--text-muted);">建議核發獎金 <strong style="color:var(--text-primary);font-size:16px;">{grade_m}</strong> 個月</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_res2:
                with st.container(border=True):
                    st.markdown('<div class="section-label" style="margin-top:0;"><span>5</span>獎金確認與上傳</div>', unsafe_allow_html=True)
                    base      = st.number_input("本薪基數（元）", 0, 200000, 30000, 1000)
                    final_amt = st.number_input("確認實發金額（元）", 0, 500000, int(base * grade_m))
                    st.write("")
                    if st.button("➕ 加入待傳清單", use_container_width=True):
                        meta = res['meta']
                        full_data = {
                            "評分日期": meta["date"], "評分主管": meta["supervisor"],
                            "受評姓名": meta["name"], "部門": meta["dept"], "職等": meta["level"],
                            "總分": f"{res['score']:.2f}", "評等": grade_t, "實得獎金": final_amt,
                            "主管評語": meta["comment"],
                            "A區_基礎評分明細": meta["a_detail_str"],
                            "B區_挑戰評分明細": meta["b_detail_str"],
                            "OKR_目標設定與內容": meta["text_record_str"]
                        }
                        st.session_state.batch_queue.append(full_data)
                        st.toast(f"✅ 已暫存 {meta['name']} 的紀錄")


# ==========================================
# 頁面 2：雲端評核紀錄
# ==========================================
elif menu == "📋 雲端紀錄":
    st.markdown("""
    <div class="page-header-inner">
        <div class="page-header-icon-wrap">📋</div>
        <div class="page-header-text">
            <h2>雲端評核紀錄資料庫</h2>
            <p>查詢歷史評核資料，管理待上傳佇列</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_ctrl1, _ = st.columns([1, 4])
    with col_ctrl1:
        if st.button("🔄 同步最新資料", use_container_width=True):
            conn, tp = get_gsheets_connection()
            if conn:
                with st.spinner("同步中..."):
                    try:
                        df = conn.read(worksheet="評核紀錄")
                        st.session_state.cloud_data_cache = df.dropna(how='all') if isinstance(df, pd.DataFrame) else pd.DataFrame()
                        st.success("同步完成")
                    except Exception as e:
                        st.error(f"讀取錯誤: {e}")
            else:
                st.error(tp)

    if st.session_state.batch_queue:
        with st.container(border=True):
            st.markdown('<div class="section-label" style="margin-top:0;"><span>↑</span>上傳緩衝區</div>', unsafe_allow_html=True)
            st.dataframe(
                pd.DataFrame(st.session_state.batch_queue)[['受評姓名', '部門', '總分', '評等', '實得獎金']],
                hide_index=True, use_container_width=True
            )
            col_up1, col_up2, _ = st.columns([1, 1, 2])
            with col_up1:
                if st.button("🚀 正式上傳雲端", use_container_width=True, type="primary"):
                    conn, tp = get_gsheets_connection()
                    if conn:
                        with st.spinner("安全寫入中..."):
                            try:
                                try:
                                    old = conn.read(worksheet="評核紀錄")
                                    old = old.dropna(how='all') if isinstance(old, pd.DataFrame) else pd.DataFrame()
                                except:
                                    old = pd.DataFrame()
                                new = pd.concat([old, pd.DataFrame(st.session_state.batch_queue)], ignore_index=True)
                                conn.update(worksheet="評核紀錄", data=new)
                                st.session_state.batch_queue      = []
                                st.session_state.cloud_data_cache = new
                                st.success("寫入成功！")
                                st.balloons()
                            except Exception as e:
                                st.error(f"寫入錯誤: {e}")
                    else:
                        st.error(tp)
            with col_up2:
                if not st.session_state.confirm_clear:
                    if st.button("🗑 清空暫存", use_container_width=True):
                        st.session_state.confirm_clear = True
                        st.rerun()
                else:
                    c_y, c_n = st.columns(2)
                    if c_y.button("⚠ 確定刪除", use_container_width=True):
                        st.session_state.batch_queue   = []
                        st.session_state.confirm_clear = False
                        st.rerun()
                    if c_n.button("取消", use_container_width=True):
                        st.session_state.confirm_clear = False
                        st.rerun()

    with st.container(border=True):
        st.markdown('<div class="section-label" style="margin-top:0;"><span>◈</span>歷史資料檢視</div>', unsafe_allow_html=True)

        if st.session_state.cloud_data_cache is not None and not st.session_state.cloud_data_cache.empty:
            df = st.session_state.cloud_data_cache

            s_cols = st.columns(4)
            with s_cols[0]:
                st.metric("總評核人數", len(df))
            with s_cols[1]:
                avg = pd.to_numeric(df.get('總分', pd.Series()), errors='coerce').mean()
                st.metric("平均分數", f"{avg:.1f}")
            with s_cols[2]:
                top_cnt = (pd.to_numeric(df.get('總分', pd.Series()), errors='coerce') >= 80).sum()
                st.metric("A 級以上人數", top_cnt)
            with s_cols[3]:
                m_list = ["全部"] + list(df['評分日期'].astype(str).str[:7].unique())
                s_m    = st.selectbox("過濾月份", m_list, label_visibility="collapsed")

            st.write("")

            if s_m != "全部":
                df = df[df['評分日期'].astype(str).str.startswith(s_m)]
            st.caption(f"顯示 {len(df)} 筆")

            cols = st.columns(3)
            for i, row in df.iterrows():
                score_val  = row.get('總分', '—')
                grade_val  = row.get('評等', '')
                rule_color = "#8B93B0"
                for r in st.session_state.bonus_rules:
                    if r['grade'] == grade_val:
                        rule_color = r['color']
                        break
                raw_comment     = str(row.get('主管評語', ''))
                comment_preview = raw_comment[:35] + '…' if len(raw_comment) > 35 else raw_comment
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="history-card">
                        <div class="history-card-header">
                            <span class="history-card-name">👤 {row.get('受評姓名', '')}</span>
                            <span class="history-card-dept">{row.get('部門', '')}</span>
                        </div>
                        <div>
                            <span class="history-card-score">{score_val}</span>
                            <span style="color:{rule_color};background:{rule_color}11;padding:2px 8px;border-radius:10px;font-size:12px;">{grade_val}</span>
                        </div>
                        <div style="font-size:11px;color:var(--text-muted);margin-top:8px;">
                            主管：{row.get('評分主管', '')} &nbsp;|&nbsp; 日期：{row.get('評分日期', '')}
                        </div>
                        <div style="font-size:12px;color:var(--text-secondary);margin-top:6px;">"{comment_preview}"</div>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("查看詳情"):
                        st.write(row.get('主管評語', '無評語'))
                        bonus_val = row.get('實得獎金', 0)
                        try:
                            st.caption(f"核定獎金：${int(bonus_val):,}")
                        except:
                            st.caption(f"核定獎金：{bonus_val}")

        elif st.session_state.cloud_data_cache is not None and st.session_state.cloud_data_cache.empty:
            st.info("雲端資料庫目前為空。")
        else:
            st.info("請點擊上方按鈕同步雲端紀錄。")


# ==========================================
# 頁面 3：參數設定
# ==========================================
elif menu == "⚙️ 參數設定":
    st.markdown("""
    <div class="page-header-inner">
        <div class="page-header-icon-wrap">⚙️</div>
        <div class="page-header-text">
            <h2>系統參數維護</h2>
            <p>調整獎金級距、部門考核項目與品牌識別</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        tab1, tab2, tab3 = st.tabs(["💰 獎金級距設定", "📋 部門考核項目", "🎨 品牌 LOGO 設定"])

        with tab1:
            st.caption("修改各等級的最低分門檻、獎金月數與 Hex 顏色碼")
            df_b = pd.DataFrame(st.session_state.bonus_rules)
            ed_b = st.data_editor(df_b, num_rows="dynamic", use_container_width=True)
            st.session_state.bonus_rules = ed_b.to_dict('records')

        with tab2:
            edit_dept = st.selectbox("選擇要修改的部門", options=DEPT_LIST)
            conf      = st.session_state.config_data[edit_dept]

            total_w = sum(conf['section_weights'])
            if abs(total_w - 1.0) > 0.01:
                st.error(f"⚠ 注意：目前三區權重總和為 {total_w*100:.0f}%，建議調整為 100%。")

            col_w1, col_w2, col_w3 = st.columns(3)
            nw_a = col_w1.number_input("A區權重 (KPI)",  value=conf['section_weights'][0], step=0.05)
            nw_b = col_w2.number_input("B區權重 (OKR)",  value=conf['section_weights'][1], step=0.05)
            nw_c = col_w3.number_input("C區權重 (主管)", value=conf['section_weights'][2], step=0.05)
            st.session_state.config_data[edit_dept]['section_weights'] = [nw_a, nw_b, nw_c]

            st.markdown('<div style="font-size:14px;color:#0EAFA0;font-weight:700;margin:20px 0 8px;">A 區細項 (KPI 基礎)</div>', unsafe_allow_html=True)
            ed_a = st.data_editor(pd.DataFrame(conf['basic']),     num_rows="dynamic", use_container_width=True, key=f"edit_a_{edit_dept}")
            st.session_state.config_data[edit_dept]['basic'] = ed_a.to_dict('records')

            st.markdown('<div style="font-size:14px;color:#3B6FE8;font-weight:700;margin:20px 0 8px;">B 區細項 (OKR 挑戰)</div>', unsafe_allow_html=True)
            ed_b = st.data_editor(pd.DataFrame(conf['excellent']), num_rows="dynamic", use_container_width=True, key=f"edit_b_{edit_dept}")
            st.session_state.config_data[edit_dept]['excellent'] = ed_b.to_dict('records')

        with tab3:
            st.caption("自訂顯示在側邊欄的品牌識別，支援上傳圖片或使用 Emoji 圖示。")
            lc = st.session_state.logo_config
            col_lg1, col_lg2 = st.columns(2, gap="large")
            with col_lg1:
                new_company = st.text_input("公司名稱", value=lc["company_name"])
                new_sysname = st.text_input("系統名稱", value=lc["system_name"])
                new_emoji   = st.text_input("Emoji 圖示", value=lc["emoji"])
            with col_lg2:
                st.caption("上傳 LOGO 圖片（PNG / JPG，建議正方形）")
                uploaded_logo = st.file_uploader("上傳 LOGO", type=["png","jpg","jpeg"], label_visibility="collapsed")
                if uploaded_logo:
                    import base64
                    b64 = base64.b64encode(uploaded_logo.read()).decode()
                    st.session_state.logo_config["image_b64"] = b64
                    st.session_state.logo_config["use_image"] = True
                    st.success("✅ 圖片已上傳，儲存後生效")
                if lc["use_image"] and lc["image_b64"]:
                    st.markdown(f'<img src="data:image/png;base64,{lc["image_b64"]}" style="width:80px;height:80px;object-fit:contain;border-radius:12px;border:1px solid #DDE1EE;margin-top:8px;">', unsafe_allow_html=True)
                    if st.button("🗑 移除圖片，改用 Emoji"):
                        st.session_state.logo_config["use_image"] = False
                        st.session_state.logo_config["image_b64"] = None
                        st.rerun()
            st.session_state.logo_config["company_name"] = new_company
            st.session_state.logo_config["system_name"]  = new_sysname
            st.session_state.logo_config["emoji"]        = new_emoji

        st.write("")
        if st.button("💾 儲存並套用設定", type="primary"):
            st.rerun()


# --- Footer ---
st.markdown("""
<div class="system-footer">
    <p>馬尼行動通訊總管理處 | 數位化管理系統 © 2026</p>
    <p style="font-size:10px;">系統版本 v38.0 - Sidebar 穩固修復版</p>
</div>
""", unsafe_allow_html=True)
