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

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700;900&family=DM+Mono:wght@400;500&display=swap');

    :root {
        --bg-base:        #F5F7FA;
        --bg-surface:     #FFFFFF;
        --bg-elevated:    #F7F9FC;
        --bg-hover:       #EEF1F6;
        --border:         #E2E6EE;
        --border-light:   #ECEEF3;
        --text-primary:   #2D3340;
        --text-secondary: #5A6375;
        --text-muted:     #9AA3B2;
        --accent-blue:    #5B77CC;
        --accent-teal:    #3D9C80;
        --accent-amber:   #C49A35;
        --zone-a-bg:      #EEF2FF;
        --zone-a-border:  #C4CAEA;
        --zone-a-text:    #3D5299;
        --zone-b-bg:      #EDF7F4;
        --zone-b-border:  #B0DDD0;
        --zone-b-text:    #2E7A64;
        --zone-c-bg:      #FDF6EC;
        --zone-c-border:  #EDD890;
        --zone-c-text:    #8A6020;
        --warn-bg:        #FDF0F0;
        --warn-text:      #B05050;
        --warn-border:    #F0C4C4;
    }

    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', sans-serif !important;
        background-color: var(--bg-base) !important;
        color: var(--text-primary) !important;
    }
    .stApp { background-color: var(--bg-base) !important; }
    .stDeployButton, [data-testid="stMainMenu"] { display: none !important; }
    [data-testid="stHeader"] { background-color: transparent !important; }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 96% !important;
    }

    /* ===== 側邊欄 ===== */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border-light) !important;
        box-shadow: 2px 0 16px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {
        background: transparent !important; border: none !important;
        box-shadow: none !important; padding: 0 10px !important; gap: 3px !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
        cursor: pointer !important; width: 100% !important; margin: 0 !important; background: transparent !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child {
        position: absolute !important; opacity: 0 !important; width: 0 !important; height: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:last-child {
        color: var(--text-secondary) !important; font-size: 14px !important; font-weight: 600 !important;
        padding: 11px 16px !important; border-radius: 9px !important; margin: 2px 0 !important;
        transition: all 0.18s ease !important; display: block !important; width: 100% !important;
        border-left: 3px solid transparent !important; background: transparent !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover > div:last-child {
        background: #EEF2FF !important; color: var(--accent-blue) !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"][aria-checked="true"] > div:last-child {
        background: var(--text-primary) !important; color: #FFFFFF !important;
        border-left: 3px solid var(--accent-blue) !important; font-weight: 700 !important;
        box-shadow: 0 3px 10px rgba(45,51,64,0.15) !important;
    }

    .sidebar-logo { padding: 30px 18px 18px; text-align: center; border-bottom: 1px solid var(--border-light); }
    .sidebar-logo-icon { font-size: 36px; line-height: 1; }
    .sidebar-logo-title { color: var(--text-primary); font-size: 17px; font-weight: 900; letter-spacing: 2px; margin: 10px 0 3px; }
    .sidebar-logo-sub { color: var(--text-muted); font-size: 11px; }

    /* ===== 卡片 ===== */
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 13px !important;
        padding: 20px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
        margin-bottom: 16px !important;
        transition: box-shadow 0.2s !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 4px 18px rgba(0,0,0,0.07) !important;
    }

    /* 巢狀評分列 */
    [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--bg-elevated) !important;
        padding: 12px 16px !important;
        border-radius: 9px !important;
        box-shadow: none !important;
        margin-bottom: 8px !important;
        border: 1px solid var(--border) !important;
    }
    [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--accent-blue) !important;
        background-color: #FAFBFF !important;
    }
    [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"] {
        padding-top: 0 !important; padding-bottom: 0 !important;
    }

    /* ===== 頁面標題 ===== */
    .page-header-inner {
        display: flex; align-items: center; gap: 16px;
        padding: 0 0 18px; margin-bottom: 20px;
        border-bottom: 1px solid var(--border);
    }
    .page-header-icon-wrap {
        width: 48px; height: 48px; flex-shrink: 0;
        background: var(--bg-surface); border: 1px solid var(--border);
        border-radius: 12px; display: flex; align-items: center;
        justify-content: center; font-size: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .page-header-text h2 { margin: 0 0 3px; color: var(--text-primary); font-size: 24px; font-weight: 900; }
    .page-header-text p  { margin: 0; color: var(--text-muted); font-size: 13px; }

    /* ===== Step 標籤 ===== */
    .step-label {
        font-size: 11px; font-weight: 800; color: var(--text-muted);
        letter-spacing: 1.5px; text-transform: uppercase;
        margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
    }
    .step-label::after {
        content: ''; flex: 1; height: 1px; background: var(--border);
    }

    .section-label {
        display: flex; align-items: center; gap: 9px;
        font-size: 15px; font-weight: 800; color: var(--text-primary);
        margin: -4px 0 16px; padding-bottom: 12px;
        border-bottom: 1px dashed var(--border);
    }
    .section-label span {
        display: inline-flex; align-items: center; justify-content: center;
        width: 22px; height: 22px; background: var(--text-primary);
        border-radius: 6px; font-size: 11px; font-weight: 900; color: white; flex-shrink: 0;
    }

    /* ===== 評分區塊標題 ===== */
    .score-section-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 11px 16px; border-radius: 9px; margin: 0 0 12px;
    }
    .ssh-a { background: var(--zone-a-bg); border: 1px solid var(--zone-a-border); }
    .ssh-b { background: var(--zone-b-bg); border: 1px solid var(--zone-b-border); }
    .ssh-c { background: var(--zone-c-bg); border: 1px solid var(--zone-c-border); }
    .ssh-title { font-weight: 800; font-size: 13px; }
    .ssh-title-a { color: var(--zone-a-text); }
    .ssh-title-b { color: var(--zone-b-text); }
    .ssh-title-c { color: var(--zone-c-text); }
    .ssh-badge {
        font-size: 11px; font-weight: 800; padding: 4px 11px;
        border-radius: 18px; font-family: 'DM Mono', monospace;
        background: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .ssh-badge-a { color: var(--zone-a-text); }
    .ssh-badge-b { color: var(--zone-b-text); }
    .ssh-badge-c { color: var(--zone-c-text); }

    /* ===== 評分項目文字 ===== */
    .score-title-wrap { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
    .score-title { font-weight: 700; font-size: 14px; color: var(--text-primary); }
    .score-weight {
        font-size: 11px; color: var(--accent-blue);
        background: #EEF2FF; padding: 2px 8px;
        border-radius: 5px; font-family: 'DM Mono', monospace; font-weight: 700;
    }
    .score-help { font-size: 12px; color: var(--text-muted); line-height: 1.5; }
    .score-help-warn {
        font-size: 11px; color: var(--warn-text);
        background: var(--warn-bg); border: 1px solid var(--warn-border);
        padding: 3px 9px; border-radius: 6px;
        display: inline-block; margin-top: 3px; font-weight: 600;
    }

    /* ===== 核定結果面板 (深色強調) ===== */
    .result-dark-panel {
        background: var(--text-primary);
        border-radius: 14px; padding: 26px 20px;
        text-align: center;
    }
    .rdp-label {
        font-size: 11px; font-weight: 700; color: #9AA3B2;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;
    }
    .rdp-score {
        font-size: 60px; font-weight: 900; color: #FFFFFF;
        line-height: 1; font-family: 'DM Mono', monospace;
        letter-spacing: -2px; margin-bottom: 14px;
    }
    .rdp-grade {
        display: inline-block; padding: 6px 20px; border-radius: 20px;
        font-size: 14px; font-weight: 800; margin-bottom: 16px;
    }
    .rdp-divider { border: none; border-top: 1px solid #3D4555; margin: 12px 0; }
    .rdp-info-row {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 7px;
    }
    .rdp-info-label { font-size: 12px; color: #9AA3B2; font-weight: 600; }
    .rdp-info-val   { font-size: 13px; color: #FFFFFF; font-weight: 700; font-family: 'DM Mono', monospace; }
    .rdp-bonus-box {
        background: #3D4555; border-radius: 10px;
        padding: 13px 15px; margin-top: 14px; text-align: left;
    }
    .rdp-bonus-label { font-size: 10px; color: #9AA3B2; font-weight: 700; letter-spacing: 1px; margin-bottom: 5px; }
    .rdp-bonus-val   { font-size: 24px; font-weight: 900; color: #F9C74F; font-family: 'DM Mono', monospace; }
    .rdp-bonus-sub   { font-size: 11px; color: #9AA3B2; margin-top: 3px; }

    /* ===== 歷史卡片 ===== */
    .history-card {
        background: var(--bg-surface); border: 1px solid var(--border);
        border-radius: 11px; padding: 16px; margin-bottom: 12px;
        transition: all 0.18s;
    }
    .history-card:hover { border-color: var(--accent-blue); box-shadow: 0 3px 14px rgba(91,119,204,0.08); }
    .history-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
    .history-card-name   { font-size: 16px; font-weight: 800; color: var(--text-primary); }
    .history-card-dept   { font-size: 11px; font-weight: 600; color: var(--text-muted); background: var(--bg-elevated); border: 1px solid var(--border); padding: 3px 9px; border-radius: 6px; }
    .history-card-score  { font-size: 28px; font-weight: 900; color: var(--text-primary); font-family: 'DM Mono', monospace; }

    /* ===== 輸入元件 ===== */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-size: 14px !important;
        padding: 10px 13px !important;
        transition: all 0.18s !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(91,119,204,0.15) !important;
        background-color: var(--bg-surface) !important;
    }

    /* ===== 下拉選單完整修正 ===== */
    [data-testid="stSelectbox"] > div > div {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    /* 已選值文字顏色 — 多層選擇器覆蓋 */
    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] div,
    [data-testid="stSelectbox"] [data-baseweb="select"] p,
    [data-testid="stSelectbox"] [data-baseweb="select"] [class*="singleValue"],
    [data-testid="stSelectbox"] [data-baseweb="select"] [class*="ValueContainer"] > div,
    [data-testid="stSelectbox"] [class*="valueContainer"] div {
        color: var(--text-primary) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    /* Placeholder */
    [data-testid="stSelectbox"] [data-baseweb="select"] [class*="placeholder"] {
        color: var(--text-muted) !important;
    }
    /* 展開的選項清單 */
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="menu"] ul {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10) !important;
    }
    [role="option"],
    [data-baseweb="option"] {
        color: var(--text-primary) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        background-color: transparent !important;
    }
    [role="option"]:hover,
    [data-baseweb="option"]:hover {
        background-color: #EEF2FF !important;
        color: var(--accent-blue) !important;
    }
    [aria-selected="true"] {
        background-color: var(--text-primary) !important;
        color: #FFFFFF !important;
    }

    /* Label 統一 */
    .stTextInput label, .stNumberInput label,
    .stTextArea label, .stSelectbox label,
    .stDateInput label, [data-testid="stDateInput"] label {
        font-size: 13px !important; font-weight: 700 !important;
        color: var(--text-secondary) !important; margin-bottom: 5px !important;
    }

    /* Date input */
    [data-testid="stDateInput"] input {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-size: 14px !important;
    }

    /* ===== 按鈕 ===== */
    .stButton > button {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-secondary) !important;
        border-radius: 9px !important;
        font-weight: 700 !important; font-size: 13px !important;
        padding: 10px 16px !important;
        transition: all 0.18s !important;
    }
    .stButton > button:hover {
        border-color: var(--accent-blue) !important;
        color: var(--accent-blue) !important;
        background: #EEF2FF !important;
        box-shadow: 0 3px 10px rgba(91,119,204,0.12) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"] {
        background: var(--text-primary) !important;
        border-color: var(--text-primary) !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #1A1D24 !important; color: white !important;
    }

    /* 表單送出按鈕 */
    .stFormSubmitButton > button {
        background: var(--text-primary) !important;
        border: none !important; color: white !important;
        font-size: 14px !important; font-weight: 700 !important;
        padding: 14px !important; border-radius: 11px !important;
        box-shadow: 0 5px 16px rgba(45,51,64,0.18) !important;
        width: 100% !important; margin-top: 14px;
        transition: all 0.18s !important; letter-spacing: 0.5px;
    }
    .stFormSubmitButton > button:hover {
        background: #1A1D24 !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(45,51,64,0.25) !important;
    }
    /* 停用的表單按鈕 (B/C區同步提示) */
    .stFormSubmitButton > button:disabled {
        background: var(--bg-hover) !important;
        color: var(--text-muted) !important;
        box-shadow: none !important;
        cursor: default !important;
        transform: none !important;
    }

    .stCaption, small { font-size: 12px !important; color: var(--text-muted) !important; font-weight: 500 !important; }
    [data-testid="stAlert"] { border-radius: 9px !important; font-size: 13px !important; font-weight: 600 !important; }

    .system-footer {
        text-align: center; padding: 32px 0 16px;
        color: var(--text-muted); font-size: 12px;
        margin-top: 36px; font-weight: 500;
        border-top: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)


# --- 3. 核心功能 ---
def calculate_dynamic_bonus(score, rules_data):
    sorted_rules = sorted(rules_data, key=lambda x: x['min_score'], reverse=True)
    for rule in sorted_rules:
        if score >= rule['min_score']:
            return rule['grade'], rule['months'], rule['color']
    return "N/A", 0.0, "#9AA3B2"

def update_target_content(dept, section, idx, key):
    st.session_state.config_data[dept][section][idx]['content'] = st.session_state[key]

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
        {"grade": "S (特優)",   "min_score": 90, "months": 1.5, "color": "#C47080"},
        {"grade": "A (優良)",   "min_score": 80, "months": 1.0, "color": "#7A6DBE"},
        {"grade": "B+ (甲上)",  "min_score": 75, "months": 0.8, "color": "#5B77CC"},
        {"grade": "B- (甲)",    "min_score": 70, "months": 0.6, "color": "#3D9C80"},
        {"grade": "C (待改善)", "min_score": 60, "months": 0.5, "color": "#C49A35"},
        {"grade": "D (不合格)", "min_score": 0,  "months": 0.0, "color": "#9AA3B2"},
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
            {"item": "素材完成時效",   "weight": 0.30, "help": "100分: 提前1天完成; 85分: 準時"},
            {"item": "設計修改次數",   "weight": 0.30, "help": "100分: 一次過稿; 85分: 修改2次內"},
            {"item": "版權與品牌規範", "weight": 0.20, "help": "【法遵紅線】盜版致侵權負賠償責任。"},
            {"item": "點擊率(CTR)",    "weight": 0.20, "help": "100分: 高於平均20%"}
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
        "text_a": [{"title": "O (目標): 營運零失誤",  "content": "確保帳務/人事/行政流程順暢無誤"}],
        "text_b": [{"title": "O (目標): 提升組織效率", "content": "優化現有流程，降低溝通成本"}]
    }
    st.session_state.config_data = {
        "電商專員":      ECOMMERCE_TEMPLATE,
        "自媒體/行銷":   MEDIA_TEMPLATE,
        "社群編輯/美編": DESIGN_TEMPLATE,
        "會計/行政":     GENERAL_TEMPLATE,
    }

if 'batch_queue'           not in st.session_state: st.session_state.batch_queue = []
if 'calculated_score_data' not in st.session_state: st.session_state.calculated_score_data = None
if 'cloud_data_cache'      not in st.session_state: st.session_state.cloud_data_cache = None
if 'logo_config'           not in st.session_state:
    st.session_state.logo_config = {
        "use_image": False, "image_b64": None,
        "emoji": "💠", "company_name": "馬尼通訊", "system_name": "總管理處考核系統"
    }
if 'confirm_clear' not in st.session_state: st.session_state.confirm_clear = False

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST  = list(st.session_state.config_data.keys())


# ==========================================
# 側邊欄
# ==========================================
with st.sidebar:
    lc = st.session_state.logo_config
    logo_html = (
        f'<img src="data:image/png;base64,{lc["image_b64"]}" '
        f'style="width:72px;height:72px;object-fit:contain;border-radius:11px;">'
        if lc["use_image"] and lc["image_b64"]
        else f'<div class="sidebar-logo-icon">{lc["emoji"]}</div>'
    )
    st.markdown(f"""
    <div class="sidebar-logo">
        {logo_html}
        <div class="sidebar-logo-title">{lc["company_name"]}</div>
        <div class="sidebar-logo-sub">{lc["system_name"]}</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    menu = st.radio("導覽選單", ["📝 新增評核", "📋 雲端紀錄", "⚙️ 參數設定"],
                    index=0, label_visibility="collapsed")
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
            <p>填寫基本資料、設定目標、完成各維度評分後執行計算</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STEP 1：基本資料 橫排五欄 ──
    st.markdown('<div class="step-label">STEP 1 &nbsp;&nbsp;基本資料</div>', unsafe_allow_html=True)
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.1, 1.1, 1])
        with c1: input_name       = st.text_input("受評人姓名", placeholder="輸入姓名...")
        with c2: input_supervisor = st.text_input("評分主管",   placeholder="直屬主管姓名...")
        with c3: input_dept       = st.selectbox("所屬部門", options=DEPT_LIST)
        with c4: input_level      = st.selectbox("職稱職等", options=JOB_LEVELS)
        with c5: input_date       = st.date_input("評核月份", value=datetime.now())

    current_config = st.session_state.config_data[input_dept]

    # ── STEP 2：目標設定 左右兩欄 ──
    st.markdown('<div class="step-label">STEP 2 &nbsp;&nbsp;職務目標設定</div>', unsafe_allow_html=True)
    col_ta, col_tb = st.columns(2, gap="medium")
    with col_ta:
        with st.container(border=True):
            st.markdown('<div style="font-size:13px;font-weight:800;color:#2E7A64;margin-bottom:10px;">▸ A. 基礎目標 (KPI)</div>', unsafe_allow_html=True)
            for i, row in enumerate(current_config['text_a']):
                st.text_area(row['title'], value=row['content'], height=90,
                             key=f"t_a_{input_dept}_{i}",
                             on_change=update_target_content,
                             args=(input_dept, 'text_a', i, f"t_a_{input_dept}_{i}"))
    with col_tb:
        with st.container(border=True):
            st.markdown('<div style="font-size:13px;font-weight:800;color:#3D5299;margin-bottom:10px;">▸ B. 挑戰目標 (OKR)</div>', unsafe_allow_html=True)
            for i, row in enumerate(current_config['text_b']):
                st.text_area(row['title'], value=row['content'], height=90,
                             key=f"t_b_{input_dept}_{i}",
                             on_change=update_target_content,
                             args=(input_dept, 'text_b', i, f"t_b_{input_dept}_{i}"))

    # ── STEP 3：評分三區 + 結果面板 四欄並排 ──
    st.markdown('<div class="step-label">STEP 3 &nbsp;&nbsp;績效評分 &amp; 核定結果</div>', unsafe_allow_html=True)

    wa, wb, wc = current_config['section_weights']
    col_a, col_b, col_c, col_res = st.columns([1, 1, 1, 1.05], gap="medium")

    # ── A 區（含計算按鈕）──
    with col_a:
        with st.form("form_zone_a", border=True):
            st.markdown(f"""
            <div class="score-section-header ssh-a">
                <span class="ssh-title ssh-title-a">A &nbsp;KPI 基本標準</span>
                <span class="ssh-badge ssh-badge-a">{int(wa*100)}%</span>
            </div>
            """, unsafe_allow_html=True)
            scores_a = []
            for i, row in enumerate(current_config['basic']):
                is_warn = '法遵' in row.get('help', '')
                with st.container(border=True):
                    c_lbl, c_val = st.columns([2, 1])
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
                        </div>{help_block}
                        """, unsafe_allow_html=True)
                    with c_val:
                        val = st.number_input(f"A{i}", -100, 100, 80, 5, key=f"va_{i}", label_visibility="collapsed")
                        scores_a.append(val * row['weight'])
            submitted_a = st.form_submit_button("⚖ 計算總分", use_container_width=True)

    # ── B 區 ──
    with col_b:
        with st.form("form_zone_b", border=True):
            st.markdown(f"""
            <div class="score-section-header ssh-b">
                <span class="ssh-title ssh-title-b">B &nbsp;OKR 挑戰結果</span>
                <span class="ssh-badge ssh-badge-b">{int(wb*100)}%</span>
            </div>
            """, unsafe_allow_html=True)
            scores_b = []
            for i, row in enumerate(current_config['excellent']):
                is_warn = '法遵' in row.get('help', '')
                with st.container(border=True):
                    c_lbl, c_val = st.columns([2, 1])
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
                        </div>{help_block}
                        """, unsafe_allow_html=True)
                    with c_val:
                        val = st.number_input(f"B{i}", 0, 100, 80, 5, key=f"vb_{i}", label_visibility="collapsed")
                        scores_b.append(val * row['weight'])
            st.form_submit_button("↑ 在 A 區按計算", use_container_width=True, disabled=True)

    # ── C 區 ──
    with col_c:
        with st.form("form_zone_c", border=True):
            st.markdown(f"""
            <div class="score-section-header ssh-c">
                <span class="ssh-title ssh-title-c">C &nbsp;主管綜合評核</span>
                <span class="ssh-badge ssh-badge-c">{int(wc*100)}%</span>
            </div>
            """, unsafe_allow_html=True)
            st.caption("綜合給分 (1–10)")
            c_mgr_score = st.selectbox("給分", options=range(1, 11), index=7, label_visibility="collapsed")
            st.caption("主管反饋建議（必填）")
            c_mgr_comment = st.text_area("反饋", placeholder="請輸入評價與改善建議...", height=180, label_visibility="collapsed")
            st.form_submit_button("↑ 在 A 區按計算", use_container_width=True, disabled=True)

    # ── 結果面板 ──
    with col_res:
        with st.container(border=True):
            if st.session_state.calculated_score_data:
                res = st.session_state.calculated_score_data
                grade_t, grade_m, grade_c = calculate_dynamic_bonus(res['score'], st.session_state.bonus_rules)
                st.markdown(f"""
                <div class="result-dark-panel">
                    <div class="rdp-label">最終核定總分</div>
                    <div class="rdp-score">{res['score']:.2f}</div>
                    <div>
                        <span class="rdp-grade" style="background:{grade_c}28;color:{grade_c};border:1px solid {grade_c}66;">{grade_t}</span>
                    </div>
                    <hr class="rdp-divider">
                    <div class="rdp-info-row">
                        <span class="rdp-info-label">受評人</span>
                        <span class="rdp-info-val">{res['meta']['name']}</span>
                    </div>
                    <div class="rdp-info-row">
                        <span class="rdp-info-label">部門</span>
                        <span class="rdp-info-val">{res['meta']['dept']}</span>
                    </div>
                    <div class="rdp-info-row">
                        <span class="rdp-info-label">評核月份</span>
                        <span class="rdp-info-val">{res['meta']['date']}</span>
                    </div>
                    <div class="rdp-bonus-box">
                        <div class="rdp-bonus-label">建議核發獎金</div>
                        <div class="rdp-bonus-val">{grade_m} 個月</div>
                        <div class="rdp-bonus-sub">確認後填寫實發金額</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
                base      = st.number_input("本薪基數（元）", 0, 200000, 30000, 1000)
                final_amt = st.number_input("確認實發金額（元）", 0, 500000, int(base * grade_m))
                if st.button("➕ 加入待傳清單", use_container_width=True, type="primary"):
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
            else:
                st.markdown("""
                <div class="result-dark-panel" style="min-height:300px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;">
                    <div style="font-size:32px;opacity:0.25;">⚖</div>
                    <div class="rdp-label" style="text-align:center;">尚未計算</div>
                    <div style="font-size:12px;color:#5A6375;text-align:center;line-height:1.8;">
                        填寫 A、B、C 三區評分<br>點擊 A 區「計算總分」<br>結果將顯示於此
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 計算邏輯
    if submitted_a:
        if not input_name:
            st.error("⚠ 請輸入受評人姓名！")
        else:
            raw_score   = (sum(scores_a) * wa) + (sum(scores_b) * wb) + (c_mgr_score * 10 * wc)
            final_score = max(0.0, min(100.0, raw_score))

            a_details = [f"✓ {row['item']}: {st.session_state[f'va_{i}']}" for i, row in enumerate(current_config['basic'])]
            b_details = [f"✓ {row['item']}: {st.session_state[f'vb_{i}']}" for i, row in enumerate(current_config['excellent'])]
            text_records  = [f"【{row['title']}】\n{st.session_state.get(f't_a_{input_dept}_{i}', row['content'])}" for i, row in enumerate(current_config['text_a'])]
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
            st.toast("✅ 計算完成！")
            st.rerun()


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
            st.markdown('<div class="section-label"><span>↑</span>上傳緩衝區</div>', unsafe_allow_html=True)
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
                                except: old = pd.DataFrame()
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
        st.markdown('<div class="section-label"><span>◈</span>歷史資料檢視</div>', unsafe_allow_html=True)

        if st.session_state.cloud_data_cache is not None and not st.session_state.cloud_data_cache.empty:
            df = st.session_state.cloud_data_cache

            s_cols = st.columns(4)
            with s_cols[0]: st.metric("總評核人數", len(df))
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
                rule_color = "#9AA3B2"
                for r in st.session_state.bonus_rules:
                    if r['grade'] == grade_val:
                        rule_color = r['color']; break
                raw_comment     = str(row.get('主管評語', ''))
                comment_preview = raw_comment[:35] + '…' if len(raw_comment) > 35 else raw_comment
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="history-card">
                        <div class="history-card-header">
                            <span class="history-card-name">👤 {row.get('受評姓名','')}</span>
                            <span class="history-card-dept">{row.get('部門','')}</span>
                        </div>
                        <div>
                            <span class="history-card-score">{score_val}</span>
                            <span style="color:{rule_color};background:{rule_color}20;padding:3px 11px;border-radius:9px;font-size:12px;font-weight:700;margin-left:7px;border:1px solid {rule_color}44;">{grade_val}</span>
                        </div>
                        <div style="font-size:12px;color:var(--text-muted);margin-top:9px;font-weight:500;">
                            主管：{row.get('評分主管','')} &nbsp;|&nbsp; 日期：{row.get('評分日期','')}
                        </div>
                        <div style="font-size:13px;color:var(--text-secondary);margin-top:8px;line-height:1.5;">"{comment_preview}"</div>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("查看詳情"):
                        st.write(row.get('主管評語', '無評語'))
                        bonus_val = row.get('實得獎金', 0)
                        try:    st.caption(f"核定獎金：${int(bonus_val):,}")
                        except: st.caption(f"核定獎金：{bonus_val}")

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

            st.markdown('<div style="font-size:14px;color:#2E7A64;font-weight:800;margin:20px 0 8px;">A 區細項 (KPI 基礎)</div>', unsafe_allow_html=True)
            ed_a = st.data_editor(pd.DataFrame(conf['basic']),     num_rows="dynamic", use_container_width=True, key=f"edit_a_{edit_dept}")
            st.session_state.config_data[edit_dept]['basic'] = ed_a.to_dict('records')

            st.markdown('<div style="font-size:14px;color:#3D5299;font-weight:800;margin:20px 0 8px;">B 區細項 (OKR 挑戰)</div>', unsafe_allow_html=True)
            ed_b2 = st.data_editor(pd.DataFrame(conf['excellent']), num_rows="dynamic", use_container_width=True, key=f"edit_b_{edit_dept}")
            st.session_state.config_data[edit_dept]['excellent'] = ed_b2.to_dict('records')

        with tab3:
            st.caption("自訂顯示在側邊欄的品牌識別，支援上傳圖片或使用 Emoji 圖示。")
            lc = st.session_state.logo_config
            col_lg1, col_lg2 = st.columns(2, gap="large")
            with col_lg1:
                new_company = st.text_input("公司名稱",  value=lc["company_name"])
                new_sysname = st.text_input("系統名稱",  value=lc["system_name"])
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
                    st.markdown(f'<img src="data:image/png;base64,{lc["image_b64"]}" style="width:84px;height:84px;object-fit:contain;border-radius:11px;border:1px solid var(--border);margin-top:10px;">', unsafe_allow_html=True)
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
    <p>馬尼通訊 | 數位化管理系統 © 2026</p>
    <p style="font-size:11px;font-weight:600;margin-top:4px;">系統版本 v42.0 - Light Morandi · New Layout Edition</p>
</div>
""", unsafe_allow_html=True)
