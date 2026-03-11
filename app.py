import streamlit as st
import pandas as pd
from datetime import datetime
import io
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

# --- 2. 全新視覺設計 CSS ---
st.markdown("""
<style>
    /* ===== 字體引入 ===== */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700;900&family=DM+Mono:wght@400;500&display=swap');

    /* ===== CSS 變數 (淺色系) ===== */
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
        --grade-s:       #D94F7A;
        --grade-a:       #6C4FD4;
        --grade-b+:      #3B6FE8;
        --grade-b:       #0EAFA0;
        --grade-c:       #D4820A;
        --grade-d:       #8B93B0;
    }

    /* ===== 全域重置 ===== */
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', sans-serif;
        color: var(--text-primary);
    }
    .stApp {
        background-color: var(--bg-base);
    }
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 97%;
    }

    /* ===== 側邊欄 ===== */
    [data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--border) !important;
        margin: 12px 0 16px 0;
    }

    /* 側邊欄 Logo 區 */
    .sidebar-logo {
        background: linear-gradient(135deg, #EBF0FF 0%, #F7F8FC 100%);
        padding: 28px 20px 22px;
        border-bottom: 1px solid var(--border);
        text-align: center;
    }
    .sidebar-logo-icon {
        font-size: 44px;
        line-height: 1;
        filter: drop-shadow(0 0 10px rgba(59,111,232,0.25));
    }
    .sidebar-logo-title {
        color: var(--text-primary);
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 3px;
        margin: 12px 0 4px 0;
    }
    .sidebar-logo-sub {
        color: var(--text-muted);
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* 隱藏 Radio 原始圓點與白色外框容器 */
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }
    [data-testid="stSidebar"] .stRadio > div[data-baseweb="radio-group"] {
        background: transparent !important; border: none !important;
        box-shadow: none !important; padding: 0 !important;
    }
    /* 導覽項目樣式 */
    [data-testid="stSidebar"] .stRadio label {
        color: var(--text-secondary) !important;
        font-size: 14px !important; font-weight: 500 !important;
        padding: 10px 16px !important; border-radius: 8px !important;
        margin: 2px 0 !important; transition: all 0.15s ease !important;
        cursor: pointer; display: block !important; width: 100% !important;
        border-left: 3px solid transparent !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: var(--bg-hover) !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"][aria-checked="true"] label {
        background: rgba(59,111,232,0.08) !important;
        color: var(--accent-blue) !important;
        border-left: 3px solid var(--accent-blue) !important;
        font-weight: 700 !important; padding-left: 13px !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 2px !important; padding: 0 12px !important;
        background: transparent !important; border: none !important;
    }

    /* ===== 頂部頁面標題列 ===== */
    .page-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px 24px;
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .page-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-teal));
    }
    .page-header-icon {
        font-size: 28px;
        line-height: 1;
        opacity: 0.85;
    }
    .page-header h2 {
        margin: 0;
        color: var(--text-primary);
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .page-header-sub {
        color: var(--text-muted);
        font-size: 12px;
        margin: 0;
    }

    /* ===== 通用卡片 ===== */
    .card {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
    }

    /* ===== 區塊標題 ===== */
    .section-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 11px;
        font-weight: 700;
        color: var(--text-muted);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 20px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border);
    }
    .section-label span {
        display: inline-block;
        width: 20px;
        height: 20px;
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: 5px;
        text-align: center;
        line-height: 20px;
        font-size: 10px;
        color: var(--text-secondary);
    }

    /* ===== 評分區塊標題 ===== */
    .score-section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 0 0 16px 0;
        border: 1px solid;
    }
    .ssh-a {
        background: rgba(61,217,186,0.06);
        border-color: rgba(61,217,186,0.2) !important;
    }
    .ssh-b {
        background: rgba(77,124,254,0.06);
        border-color: rgba(77,124,254,0.2) !important;
    }
    .ssh-c {
        background: rgba(245,166,35,0.06);
        border-color: rgba(245,166,35,0.2) !important;
    }
    .ssh-title { font-weight: 700; font-size: 13px; }
    .ssh-title-a { color: var(--accent-teal); }
    .ssh-title-b { color: var(--accent-blue); }
    .ssh-title-c { color: var(--accent-amber); }
    .ssh-badge {
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        font-family: 'DM Mono', monospace;
    }
    .ssh-badge-a { background: rgba(61,217,186,0.12); color: var(--accent-teal); }
    .ssh-badge-b { background: rgba(77,124,254,0.12); color: var(--accent-blue); }
    .ssh-badge-c { background: rgba(245,166,35,0.12); color: var(--accent-amber); }

    /* ===== 評分項目列 ===== */
    .score-item {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        transition: border-color 0.15s;
    }
    .score-item:hover {
        border-color: var(--border-light);
    }
    .score-item-name {
        font-weight: 600;
        font-size: 13px;
        color: var(--text-primary);
    }
    .score-item-weight {
        font-size: 11px;
        color: var(--text-muted);
        font-family: 'DM Mono', monospace;
        margin-left: 6px;
    }
    .score-item-help {
        font-size: 11px;
        color: var(--text-muted);
        margin-top: 4px;
        line-height: 1.4;
    }
    .score-item-help.warning {
        color: var(--accent-amber);
        opacity: 0.9;
    }

    /* ===== 結果看板 ===== */
    .result-panel {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 28px 24px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .result-panel::after {
        content: '';
        position: absolute;
        bottom: -40px; right: -40px;
        width: 120px; height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(59,111,232,0.06) 0%, transparent 70%);
    }
    .result-score-label {
        font-size: 11px;
        font-weight: 700;
        color: var(--text-muted);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .result-score-value {
        font-size: 56px;
        font-weight: 900;
        color: var(--text-primary);
        line-height: 1;
        font-family: 'DM Mono', monospace;
        margin-bottom: 14px;
    }
    .result-grade-badge {
        display: inline-block;
        padding: 6px 20px;
        border-radius: 24px;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    .result-bonus-text {
        font-size: 13px;
        color: var(--text-secondary);
        margin-top: 6px;
    }

    /* ===== 歷史卡片 ===== */
    .history-card {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
        cursor: default;
    }
    .history-card:hover {
        border-color: var(--accent-blue);
        background: var(--bg-elevated);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59,111,232,0.10);
    }
    .history-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }
    .history-card-name {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
    }
    .history-card-dept {
        font-size: 11px;
        color: var(--text-muted);
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        padding: 2px 8px;
        border-radius: 6px;
    }
    .history-card-score {
        font-size: 28px;
        font-weight: 900;
        color: var(--text-primary);
        font-family: 'DM Mono', monospace;
        line-height: 1;
    }
    .history-card-grade {
        font-size: 11px;
        font-weight: 600;
        margin-left: 6px;
        color: var(--text-muted);
    }
    .history-card-meta {
        font-size: 11px;
        color: var(--text-muted);
        margin-top: 8px;
    }
    .history-card-comment {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid var(--border);
        line-height: 1.5;
        font-style: italic;
    }

    /* ===== 獎金等級標記 ===== */
    .grade-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }

    /* ===== Streamlit 元件覆蓋 ===== */
    /* 輸入框 */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Noto Sans TC', sans-serif !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(77,124,254,0.15) !important;
    }
    .stTextInput label, .stNumberInput label, .stTextArea label,
    .stSelectbox label, .stDateInput label {
        color: var(--text-secondary) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
    }

    /* 按鈕 */
    .stButton > button {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-light) !important;
        color: var(--text-secondary) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.15s !important;
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
    .stButton > button[kind="primary"]:hover {
        background: #2C5ED4 !important;
        box-shadow: 0 4px 12px rgba(59,111,232,0.3) !important;
    }

    /* Form submit button */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-violet) 100%) !important;
        border: none !important;
        color: white !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        padding: 14px !important;
        border-radius: 10px !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 14px rgba(59,111,232,0.25) !important;
        transition: all 0.2s !important;
    }
    .stFormSubmitButton > button:hover {
        box-shadow: 0 6px 20px rgba(59,111,232,0.38) !important;
        transform: translateY(-1px) !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary {
        color: var(--text-secondary) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    /* 表格 */
    .stDataFrame, [data-testid="stDataEditor"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-elevated) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1px solid var(--border) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important;
    }

    /* Info / Error / Success */
    .stInfo, .stAlert {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-secondary) !important;
    }
    .stSuccess {
        background: rgba(61,217,186,0.08) !important;
        border: 1px solid rgba(61,217,186,0.2) !important;
        border-radius: 10px !important;
        color: var(--accent-teal) !important;
    }
    .stError {
        background: rgba(240,98,146,0.08) !important;
        border: 1px solid rgba(240,98,146,0.2) !important;
        border-radius: 10px !important;
        color: var(--accent-rose) !important;
    }

    /* Caption */
    .stCaption, small, caption {
        color: var(--text-muted) !important;
        font-size: 11px !important;
    }

    /* Divider */
    hr {
        border-color: var(--border) !important;
        margin: 16px 0 !important;
    }

    /* Number input 上下箭頭 */
    input[type=number]::-webkit-inner-spin-button,
    input[type=number]::-webkit-outer-spin-button {
        opacity: 0.5;
    }

    /* 統計徽章 */
    .stat-badge {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    .stat-badge-val {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'DM Mono', monospace;
        line-height: 1;
    }
    .stat-badge-lbl {
        font-size: 10px;
        color: var(--text-muted);
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* 待上傳 badge */
    .upload-pending {
        background: rgba(245,166,35,0.1);
        border: 1px solid rgba(245,166,35,0.25);
        border-radius: 8px;
        padding: 10px 16px;
        color: var(--accent-amber);
        font-size: 13px;
        font-weight: 600;
        margin-top: 12px;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    /* Date input */
    [data-testid="stDateInput"] input {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    /* ===== 滾動條美化 ===== */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--border-light); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心功能：動態獎金計算 ---
def calculate_dynamic_bonus(score, rules_data):
    sorted_rules = sorted(rules_data, key=lambda x: x['min_score'], reverse=True)
    for rule in sorted_rules:
        if score >= rule['min_score']:
            return rule['grade'], rule['months'], rule['color']
    return "N/A", 0.0, "#545D7A"

def update_target_content(dept, section, idx, key):
    new_value = st.session_state[key]
    st.session_state.config_data[dept][section][idx]['content'] = new_value

# --- 共用連線函式 ---
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
    if not spreadsheet_url: return None, "未設定網址"

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
    except Exception as e: return None, str(e)

# --- 4. 初始化資料 ---
if 'bonus_rules' not in st.session_state:
    st.session_state.bonus_rules = [
        {"grade": "S (特優)",   "min_score": 90, "months": 1.5, "color": "#F06292"},
        {"grade": "A (優良)",   "min_score": 80, "months": 1.0, "color": "#9C7AF7"},
        {"grade": "B+ (甲上)",  "min_score": 75, "months": 0.8, "color": "#4D7CFE"},
        {"grade": "B- (甲)",    "min_score": 70, "months": 0.6, "color": "#3DD9BA"},
        {"grade": "C (待改善)", "min_score": 60, "months": 0.5, "color": "#F5A623"},
        {"grade": "D (不合格)", "min_score": 0,  "months": 0.0, "color": "#545D7A"},
    ]

if 'config_data' not in st.session_state:
    ECOMMERCE_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "訂單處理正確率", "weight": 0.30, "help": "【法遵紅線】不可扣底薪。\n100分: 0%錯誤; 85分: <0.5%"},
            {"item": "客服聊聊響應",   "weight": 0.30, "help": "【法遵紅線】僅限上班時間計入。"},
            {"item": "商城活動參與",   "weight": 0.20, "help": "主動提報與執行力。"},
            {"item": "上架與庫存準確", "weight": 0.20, "help": "【法遵紅線】標錯價屬重大疏失。"}
        ],
        "excellent": [
            {"item": "KR1: 滯銷品去化", "weight": 0.33, "help": ""},
            {"item": "KR2: 價盤監控",   "weight": 0.33, "help": ""},
            {"item": "KR3: 客單價提升", "weight": 0.34, "help": ""}
        ],
        "threshold": 80,
        "text_a": [{"title": "O (目標): 維持優選賣家資格", "content": "1. 確保出貨零失誤\n2. 聊聊回應率維持 95% 以上"}],
        "text_b": [{"title": "O (目標): 提升賣場獲利結構", "content": "1. 降低庫存週轉天數\n2. 提高組合商品銷售比重"}]
    }
    MEDIA_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "短影音產出成效", "weight": 0.30, "help": "100分: 12支+觀看破萬; 85分: 準時12支"},
            {"item": "官網SEO文章撰寫","weight": 0.30, "help": "【法遵紅線】抄襲涉及著作權法。"},
            {"item": "社群互動維護",   "weight": 0.20, "help": "【法遵紅線】禁止下班要求回覆。"},
            {"item": "導流貢獻(ROAS)", "weight": 0.20, "help": "100分: >50筆詢單"}
        ],
        "excellent": [
            {"item": "KR1: 爆款影片",     "weight": 0.33, "help": ""},
            {"item": "KR2: 關鍵字排名",   "weight": 0.33, "help": ""},
            {"item": "KR3: 時事跟風速度", "weight": 0.34, "help": ""}
        ],
        "threshold": 80,
        "text_a": [{"title": "O (目標): 建立流量護城河", "content": "1. 穩定產出高品質內容"}],
        "text_b": [{"title": "O (目標): 擴大品牌心佔率", "content": "讓馬尼成為台南 3C 資訊首選"}]
    }
    DESIGN_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "素材完成時效", "weight": 0.30, "help": "100分: 提前1天完成; 85分: 準時"},
            {"item": "設計修改次數", "weight": 0.30, "help": "100分: 一次過稿; 85分: 修改2次內"},
            {"item": "版權與品牌規範","weight": 0.20, "help": "【法遵紅線】盜版致侵權負賠償責任。"},
            {"item": "點擊率(CTR)",  "weight": 0.20, "help": "100分: 高於平均20%"}
        ],
        "excellent": [
            {"item": "KR1: A/B Test提案", "weight": 0.33, "help": ""},
            {"item": "KR2: AI工具應用",   "weight": 0.33, "help": ""},
            {"item": "KR3: 視覺優化",     "weight": 0.34, "help": ""}
        ],
        "threshold": 85,
        "text_a": [{"title": "O (目標): 視覺傳達精準化", "content": "1. 提升素材點擊率"}],
        "text_b": [{"title": "O (目標): 品牌視覺升級",   "content": "導入新工具提升質感"}]
    }
    GENERAL_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "作業準確度",     "weight": 0.25, "help": "【法遵紅線】導致政府罰款連動績效。"},
            {"item": "電商撥款對帳",   "weight": 0.35, "help": "防舞弊核心。100分: 完全一致"},
            {"item": "專案/發薪時效",  "weight": 0.20, "help": "【法遵紅線】遲發薪水具勞檢風險。"},
            {"item": "跨部門協作",     "weight": 0.20, "help": "90分: 產出SOP無投訴"}
        ],
        "excellent": [
            {"item": "KR1: 流程優化", "weight": 0.33, "help": ""},
            {"item": "KR2: 成本控制", "weight": 0.33, "help": ""},
            {"item": "KR3: 團隊支援", "weight": 0.34, "help": ""}
        ],
        "threshold": 80,
        "text_a": [{"title": "O (目標): 營運零失誤", "content": "確保帳務/人事/行政流程順暢無誤"}],
        "text_b": [{"title": "O (目標): 提升組織效率", "content": "優化現有流程，降低溝通成本"}]
    }
    st.session_state.config_data = {
        "電商專員":    ECOMMERCE_TEMPLATE,
        "自媒體/行銷": MEDIA_TEMPLATE,
        "社群編輯/美編": DESIGN_TEMPLATE,
        "會計/行政":   GENERAL_TEMPLATE,
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

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST   = list(st.session_state.config_data.keys())

# ==========================================
# 側邊欄
# ==========================================
with st.sidebar:
    lc = st.session_state.logo_config
    if lc["use_image"] and lc["image_b64"]:
        logo_html = f'<img src="data:image/png;base64,{lc["image_b64"]}" style="width:72px; height:72px; object-fit:contain; border-radius:12px;">'
    else:
        logo_html = f'<div class="sidebar-logo-icon">{lc["emoji"]}</div>'

    st.markdown(f"""
    <div class="sidebar-logo">
        {logo_html}
        <div class="sidebar-logo-title">{lc["company_name"]}</div>
        <div class="sidebar-logo-sub">{lc["system_name"]}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    menu = st.radio(
        "導覽選單",
        ["📝 新增評核", "📋 雲端紀錄", "⚙️ 參數設定"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.batch_queue:
        st.markdown(f"""
        <div class="upload-pending">
            ⏳ 待上傳 {len(st.session_state.batch_queue)} 筆紀錄
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 頁面 1：新增人員評核
# ==========================================
if menu == "📝 新增評核":
    st.markdown("""
    <div class="page-header">
        <div class="page-header-icon">📝</div>
        <div>
            <h2>新增人員評核</h2>
            <p class="page-header-sub">填寫基本資料與各維度評分，完成後執行計算</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1.15, 2], gap="large")

    with col_l:
        # 基本資料
        st.markdown('<div class="section-label"><span>1</span>基本資料</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        input_name       = st.text_input("受評人姓名", placeholder="輸入姓名...")
        input_supervisor = st.text_input("評分主管",   placeholder="直屬主管姓名...")
        col_d1, col_d2   = st.columns(2)
        with col_d1:
            input_dept   = st.selectbox("所屬部門", options=DEPT_LIST)
        with col_d2:
            input_level  = st.selectbox("職稱職等", options=JOB_LEVELS)
        input_date = st.date_input("評核月份", value=datetime.now())
        st.markdown('</div>', unsafe_allow_html=True)

        # 職務目標
        st.markdown('<div class="section-label"><span>2</span>職務目標設定</div>', unsafe_allow_html=True)
        current_config = st.session_state.config_data[input_dept]
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px; font-weight:700; color:#3DD9BA; margin-bottom:10px; letter-spacing:1px;">▸ A. 基礎目標 (KPI)</div>', unsafe_allow_html=True)
        for i, row in enumerate(current_config['text_a']):
            st.text_area(
                row['title'], value=row['content'], height=80,
                key=f"t_a_{input_dept}_{i}",
                on_change=update_target_content,
                args=(input_dept, 'text_a', i, f"t_a_{input_dept}_{i}")
            )
        st.markdown('<div style="font-size:12px; font-weight:700; color:#4D7CFE; margin:14px 0 10px; letter-spacing:1px;">▸ B. 挑戰目標 (OKR)</div>', unsafe_allow_html=True)
        for i, row in enumerate(current_config['text_b']):
            st.text_area(
                row['title'], value=row['content'], height=80,
                key=f"t_b_{input_dept}_{i}",
                on_change=update_target_content,
                args=(input_dept, 'text_b', i, f"t_b_{input_dept}_{i}")
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-label"><span>3</span>績效評分維度</div>', unsafe_allow_html=True)
        wa, wb, wc = current_config['section_weights']

        with st.form("score_form_v4", border=False):
            st.markdown('<div class="card">', unsafe_allow_html=True)

            # ── A 區 ──
            st.markdown(f"""
            <div class="score-section-header ssh-a">
                <span class="ssh-title ssh-title-a">A &nbsp;職務基本標準 (KPI)</span>
                <span class="ssh-badge ssh-badge-a">權重 {int(wa*100)}%</span>
            </div>
            """, unsafe_allow_html=True)
            scores_a = []
            for i, row in enumerate(current_config['basic']):
                is_warning = '法遵' in row.get('help', '')
                help_cls   = 'warning' if is_warning else ''
                st.markdown(f"""
                <div class="score-item">
                    <div>
                        <span class="score-item-name">{row['item']}</span>
                        <span class="score-item-weight">×{int(row['weight']*100)}%</span>
                    </div>
                    {'<div class="score-item-help ' + help_cls + '">' + ("⚠ " if is_warning else "ℹ ") + row["help"] + '</div>' if row.get('help') else ''}
                </div>
                """, unsafe_allow_html=True)
                val = st.number_input(
                    f"分數 ({row['item']})", -100, 100, 80, 5,
                    key=f"va_{i}", label_visibility="collapsed"
                )
                scores_a.append(val * row['weight'])

            st.markdown("<br>", unsafe_allow_html=True)

            # ── B 區 ──
            st.markdown(f"""
            <div class="score-section-header ssh-b">
                <span class="ssh-title ssh-title-b">B &nbsp;OKR 關鍵結果 (挑戰)</span>
                <span class="ssh-badge ssh-badge-b">權重 {int(wb*100)}%</span>
            </div>
            """, unsafe_allow_html=True)
            scores_b = []
            for i, row in enumerate(current_config['excellent']):
                st.markdown(f"""
                <div class="score-item">
                    <span class="score-item-name">{row['item']}</span>
                    <span class="score-item-weight">×{int(row['weight']*100)}%</span>
                </div>
                """, unsafe_allow_html=True)
                val = st.number_input(
                    f"分數 ({row['item']})", 0, 100, 80, 5,
                    key=f"vb_{i}", label_visibility="collapsed"
                )
                scores_b.append(val * row['weight'])

            st.markdown("<br>", unsafe_allow_html=True)

            # ── C 區 ──
            st.markdown(f"""
            <div class="score-section-header ssh-c">
                <span class="ssh-title ssh-title-c">C &nbsp;主管綜合評核</span>
                <span class="ssh-badge ssh-badge-c">權重 {int(wc*100)}%</span>
            </div>
            """, unsafe_allow_html=True)
            col_c1, col_c2 = st.columns([1, 2])
            with col_c1:
                st.markdown('<div style="font-size:12px; color:#8B92A9; margin-bottom:4px;">綜合給分 (1–10)</div>', unsafe_allow_html=True)
                c_mgr_score = st.selectbox("綜合給分", options=range(1, 11), index=7, label_visibility="collapsed")
            with col_c2:
                st.markdown('<div style="font-size:12px; color:#8B92A9; margin-bottom:4px;">主管反饋建議（必填）</div>', unsafe_allow_html=True)
                c_mgr_comment = st.text_area("主管反饋建議", placeholder="請輸入評價與改善建議...", height=100, label_visibility="collapsed")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("⚖ 執行計算並鎖定分數", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not input_name:
                st.error("⚠ 請輸入受評人姓名！")
            else:
                final_score = (sum(scores_a) * wa) + (sum(scores_b) * wb) + (c_mgr_score * 10 * wc)
                a_details = [f"✓ {row['item']}: {st.session_state[f'va_{i}']}" for i, row in enumerate(current_config['basic'])]
                b_details = [f"✓ {row['item']}: {st.session_state[f'vb_{i}']}" for i, row in enumerate(current_config['excellent'])]
                text_records = [f"【{row['title']}】\n{st.session_state.get(f't_a_{input_dept}_{i}', row['content'])}" for i, row in enumerate(current_config['text_a'])]
                text_records += [f"【{row['title']}】\n{st.session_state.get(f't_b_{input_dept}_{i}', row['content'])}" for i, row in enumerate(current_config['text_b'])]
                st.session_state.calculated_score_data = {
                    "score": final_score,
                    "meta": {
                        "name": input_name, "dept": input_dept, "supervisor": input_supervisor,
                        "date": str(input_date), "level": input_level, "comment": c_mgr_comment,
                        "a_detail_str": "\n".join(a_details),
                        "b_detail_str": "\n".join(b_details),
                        "text_record_str": "\n\n".join(text_records)
                    }
                }
                st.toast("✅ 計算完成，請確認下方結果")

        # ── 結果區 ──
        if st.session_state.calculated_score_data:
            st.markdown('<div class="section-label"><span>4</span>核定結果與上傳</div>', unsafe_allow_html=True)
            res = st.session_state.calculated_score_data
            grade_t, grade_m, grade_c = calculate_dynamic_bonus(res['score'], st.session_state.bonus_rules)

            col_res1, col_res2 = st.columns([1, 1], gap="medium")

            with col_res1:
                st.markdown(f"""
                <div class="result-panel">
                    <div class="result-score-label">最終核定總分</div>
                    <div class="result-score-value">{res['score']:.1f}</div>
                    <div class="result-grade-badge" style="background:{grade_c}22; color:{grade_c}; border:1px solid {grade_c}44;">{grade_t}</div>
                    <div class="result-bonus-text">建議核發獎金 <strong style="color:#E8EBF4;">{grade_m}</strong> 個月</div>
                </div>
                """, unsafe_allow_html=True)

            with col_res2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                base      = st.number_input("本薪基數（元）", 0, 200000, 30000, 1000)
                final_amt = st.number_input("確認實發金額（元）", 0, 500000, int(base * grade_m))
                st.markdown("<br>", unsafe_allow_html=True)
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
                st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 頁面 2：雲端評核紀錄
# ==========================================
elif menu == "📋 雲端紀錄":
    st.markdown("""
    <div class="page-header">
        <div class="page-header-icon">📋</div>
        <div>
            <h2>雲端評核紀錄資料庫</h2>
            <p class="page-header-sub">查詢歷史評核資料，管理待上傳佇列</p>
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
                        if isinstance(df, pd.DataFrame):
                            st.session_state.cloud_data_cache = df.dropna(how='all')
                        else:
                            st.session_state.cloud_data_cache = pd.DataFrame()
                        st.success("同步完成")
                    except Exception as e:
                        st.error(f"讀取錯誤: {e}")
            else:
                st.error(tp)

    # 待傳緩衝區
    if st.session_state.batch_queue:
        st.markdown('<div class="section-label"><span>↑</span>上傳緩衝區</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.batch_queue)[['受評姓名', '部門', '總分', '評等', '實得獎金']])
        col_up1, col_up2, _ = st.columns([1, 1, 2])
        with col_up1:
            if st.button("🚀 正式上傳", use_container_width=True, type="primary"):
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
                            st.session_state.batch_queue   = []
                            st.session_state.cloud_data_cache = new
                            st.success("寫入成功！")
                            st.balloons()
                        except Exception as e:
                            st.error(f"寫入錯誤: {e}")
                else:
                    st.error(tp)
        with col_up2:
            if st.button("🗑 清空暫存", use_container_width=True):
                st.session_state.batch_queue = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 歷史資料
    st.markdown('<div class="section-label"><span>◈</span>歷史資料檢視</div>', unsafe_allow_html=True)

    if st.session_state.cloud_data_cache is not None and not st.session_state.cloud_data_cache.empty:
        df = st.session_state.cloud_data_cache

        # 統計列
        s_cols = st.columns(4)
        with s_cols[0]:
            st.markdown(f'<div class="stat-badge"><div class="stat-badge-val">{len(df)}</div><div class="stat-badge-lbl">總評核人數</div></div>', unsafe_allow_html=True)
        with s_cols[1]:
            avg = pd.to_numeric(df.get('總分', pd.Series()), errors='coerce').mean()
            st.markdown(f'<div class="stat-badge"><div class="stat-badge-val">{avg:.1f}</div><div class="stat-badge-lbl">平均分數</div></div>', unsafe_allow_html=True)
        with s_cols[2]:
            top_cnt = (pd.to_numeric(df.get('總分', pd.Series()), errors='coerce') >= 80).sum()
            st.markdown(f'<div class="stat-badge"><div class="stat-badge-val">{top_cnt}</div><div class="stat-badge-lbl">A 級以上</div></div>', unsafe_allow_html=True)
        with s_cols[3]:
            m_list = ["全部"] + list(df['評分日期'].astype(str).str[:7].unique())
            s_m    = st.selectbox("過濾月份", m_list, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        if s_m != "全部":
            df = df[df['評分日期'].astype(str).str.startswith(s_m)]
        st.caption(f"顯示 {len(df)} 筆")

        cols = st.columns(3)
        for i, row in df.iterrows():
            score_val = row.get('總分', '—')
            grade_val = row.get('評等', '')
            # 找對應顏色
            rule_color = "#545D7A"
            for r in st.session_state.bonus_rules:
                if r['grade'] == grade_val:
                    rule_color = r['color']
                    break
            comment_preview = str(row.get('主管評語', ''))[:40] + '…' if len(str(row.get('主管評語', ''))) > 40 else str(row.get('主管評語', ''))
            with cols[i % 3]:
                st.markdown(f"""
                <div class="history-card">
                    <div class="history-card-header">
                        <span class="history-card-name">👤 {row.get('受評姓名', '')}</span>
                        <span class="history-card-dept">{row.get('部門', '')}</span>
                    </div>
                    <div>
                        <span class="history-card-score">{score_val}</span>
                        <span class="history-card-grade" style="color:{rule_color};">{grade_val}</span>
                    </div>
                    <div class="history-card-meta">主管：{row.get('評分主管', '')} &nbsp;|&nbsp; 日期：{row.get('評分日期', '')}</div>
                    <div class="history-card-comment">"{comment_preview}"</div>
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
    <div class="page-header">
        <div class="page-header-icon">⚙️</div>
        <div>
            <h2>系統參數維護</h2>
            <p class="page-header-sub">調整獎金級距、部門考核項目與品牌識別</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["💰 獎金級距設定", "📋 部門考核項目", "🎨 品牌 LOGO 設定"])

    with tab1:
        st.caption("修改各等級的最低分門檻、獎金月數與 Hex 顏色碼（建議搭配系統色票）")
        df_b  = pd.DataFrame(st.session_state.bonus_rules)
        ed_b  = st.data_editor(df_b, num_rows="dynamic", use_container_width=True)
        st.session_state.bonus_rules = ed_b.to_dict('records')

    with tab2:
        edit_dept = st.selectbox("選擇要修改的部門", options=DEPT_LIST)
        conf      = st.session_state.config_data[edit_dept]
        st.caption(f"目前 {edit_dept} 三區權重配置：A={int(conf['section_weights'][0]*100)}% / B={int(conf['section_weights'][1]*100)}% / C={int(conf['section_weights'][2]*100)}%")
        st.markdown('<div style="font-size:12px; color:#0EAFA0; font-weight:700; margin: 12px 0 8px;">A 區細項 (KPI 基礎)</div>', unsafe_allow_html=True)
        ed_a = st.data_editor(pd.DataFrame(conf['basic']), num_rows="dynamic", use_container_width=True)
        st.session_state.config_data[edit_dept]['basic'] = ed_a.to_dict('records')

    with tab3:
        st.caption("自訂顯示在側邊欄的品牌識別，支援上傳圖片或使用 Emoji 圖示。")
        lc = st.session_state.logo_config
        col_lg1, col_lg2 = st.columns([1, 1], gap="large")
        with col_lg1:
            new_company = st.text_input("公司名稱", value=lc["company_name"])
            new_sysname = st.text_input("系統名稱", value=lc["system_name"])
            new_emoji   = st.text_input("Emoji 圖示（無上傳圖片時顯示）", value=lc["emoji"])
        with col_lg2:
            st.markdown('<div style="font-size:12px; color:var(--text-secondary); font-weight:600; margin-bottom:8px;">上傳 LOGO 圖片（PNG / JPG，建議正方形）</div>', unsafe_allow_html=True)
            uploaded_logo = st.file_uploader("上傳 LOGO", type=["png","jpg","jpeg"], label_visibility="collapsed")
            if uploaded_logo:
                import base64
                b64 = base64.b64encode(uploaded_logo.read()).decode()
                st.session_state.logo_config["image_b64"] = b64
                st.session_state.logo_config["use_image"] = True
                st.success("✅ 圖片已上傳，儲存後生效")
            if lc["use_image"] and lc["image_b64"]:
                st.markdown(f'<img src="data:image/png;base64,{lc["image_b64"]}" style="width:80px; height:80px; object-fit:contain; border-radius:12px; border:1px solid var(--border); margin-top:8px;">', unsafe_allow_html=True)
                if st.button("🗑 移除圖片，改用 Emoji"):
                    st.session_state.logo_config["use_image"] = False
                    st.session_state.logo_config["image_b64"] = None
                    st.rerun()
        st.session_state.logo_config["company_name"] = new_company
        st.session_state.logo_config["system_name"]  = new_sysname
        st.session_state.logo_config["emoji"]        = new_emoji

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 儲存並套用設定", type="primary"):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
