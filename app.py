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

# --- 2. 不飽和美學 UI 優化 CSS ---
st.markdown("""
<style>
    /* 全域字體與柔和背景 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans TC', sans-serif; }
    .stApp { background-color: #F4F6F8; } /* 極淡的灰藍背景 */

    /* 消除預設頂部空白與隱藏預設元件 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { 
        padding-top: 1.5rem !important; 
        padding-bottom: 2rem !important; 
        max-width: 96%;
    }
    
    /* 側邊欄美化 (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #ECEFF1 !important; /* 柔和灰底 */
        border-right: 1px solid #CFD8DC;
    }
    [data-testid="stSidebar"] hr {
        margin-top: 10px;
        margin-bottom: 20px;
        border-color: #B0BEC5;
    }

    /* 頂部導航列 (取代原本很粗的漸層) */
    .top-nav {
        background-color: #FFFFFF;
        padding: 16px 24px;
        border-radius: 12px;
        border-left: 6px solid #7986CB; /* 莫蘭迪紫藍 */
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        display: flex;
        align-items: center;
    }
    .top-nav h2 { 
        margin: 0; 
        color: #455A64; /* 深灰藍 */
        font-size: 22px; 
        font-weight: 700; 
    }
    
    /* 區塊標題設計 (簡約底線風) */
    .section-header {
        font-size: 16px;
        font-weight: 700;
        color: #546E7A;
        border-bottom: 2px solid #CFD8DC;
        padding-bottom: 8px;
        margin: 15px 0 15px 0;
    }

    /* 評分區專用 (降飽和的柔和色標) */
    .header-a { background-color: #F1F8E9; color: #558B2F; padding: 10px 15px; border-radius: 8px; font-weight: 600; font-size: 14px; border: 1px solid #DCEDC8; margin-bottom: 12px;}
    .header-b { background-color: #E8EAF6; color: #3F51B5; padding: 10px 15px; border-radius: 8px; font-weight: 600; font-size: 14px; border: 1px solid #C5CAE9; margin-bottom: 12px;}
    .header-c { background-color: #FFF3E0; color: #E65100; padding: 10px 15px; border-radius: 8px; font-weight: 600; font-size: 14px; border: 1px solid #FFE0B2; margin-bottom: 12px;}
    
    /* 小標題 */
    .header-mid-a, .header-mid-b { 
        color: #607D8B; 
        font-weight: 700; 
        font-size: 14px; 
        margin-bottom: 8px;
    }
    
    /* 獎金看板 (輕量化) */
    .bonus-display {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #E0E0E0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    .final-score { font-size: 42px; font-weight: 800; color: #455A64; margin: 0; line-height: 1.2;}
    .final-grade { font-size: 18px; font-weight: 700; color: white; padding: 6px 18px; border-radius: 20px; display: inline-block; margin: 8px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}

    /* 歷史紀錄格狀卡片 */
    .history-grid-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        height: 100%;
        transition: all 0.2s ease-in-out;
    }
    .history-grid-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.06);
        border-color: #90A4AE;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心功能：動態獎金計算 ---
def calculate_dynamic_bonus(score, rules_data):
    sorted_rules = sorted(rules_data, key=lambda x: x['min_score'], reverse=True)
    for rule in sorted_rules:
        if score >= rule['min_score']:
            return rule['grade'], rule['months'], rule['color']
    return "N/A", 0.0, "#000000"

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
    # 顏色全面降飽和，更具專業感
    st.session_state.bonus_rules = [
        {"grade": "S (特優)", "min_score": 90, "months": 1.5, "color": "#E57373"}, # 柔和紅
        {"grade": "A (優良)", "min_score": 80, "months": 1.0, "color": "#7986CB"}, # 柔和藍紫
        {"grade": "B+ (甲上)", "min_score": 75, "months": 0.8, "color": "#81C784"}, # 柔和綠
        {"grade": "B- (甲)", "min_score": 70, "months": 0.6, "color": "#AED581"}, # 淺草綠
        {"grade": "C (待改善)", "min_score": 60, "months": 0.5, "color": "#FFB74D"}, # 柔和橘
        {"grade": "D (不合格)", "min_score": 0, "months": 0.0, "color": "#90A4AE"}, # 藍灰
    ]

if 'config_data' not in st.session_state:
    ECOMMERCE_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "訂單處理正確率", "weight": 0.30, "help": "【法遵紅線】不可扣底薪。\n100分: 0%錯誤; 85分: <0.5%"},
            {"item": "客服聊聊響應", "weight": 0.30, "help": "【法遵紅線】僅限上班時間計入。"},
            {"item": "商城活動參與", "weight": 0.20, "help": "主動提報與執行力。"},
            {"item": "上架與庫存準確", "weight": 0.20, "help": "【法遵紅線】標錯價屬重大疏失。"}
        ],
        "excellent": [
            {"item": "KR1: 滯銷品去化", "weight": 0.33, "help": ""},
            {"item": "KR2: 價盤監控", "weight": 0.33, "help": ""},
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
            {"item": "官網SEO文章撰寫", "weight": 0.30, "help": "【法遵紅線】抄襲涉及著作權法。"},
            {"item": "社群互動維護", "weight": 0.20, "help": "【法遵紅線】禁止下班要求回覆。"},
            {"item": "導流貢獻(ROAS)", "weight": 0.20, "help": "100分: >50筆詢單"}
        ],
        "excellent": [
            {"item": "KR1: 爆款影片", "weight": 0.33, "help": ""},
            {"item": "KR2: 關鍵字排名", "weight": 0.33, "help": ""},
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
            {"item": "版權與品牌規範", "weight": 0.20, "help": "【法遵紅線】盜版致侵權負賠償責任。"},
            {"item": "點擊率(CTR)", "weight": 0.20, "help": "100分: 高於平均20%"}
        ],
        "excellent": [
            {"item": "KR1: A/B Test提案", "weight": 0.33, "help": ""},
            {"item": "KR2: AI工具應用", "weight": 0.33, "help": ""},
            {"item": "KR3: 視覺優化", "weight": 0.34, "help": ""}
        ],
        "threshold": 85,
        "text_a": [{"title": "O (目標): 視覺傳達精準化", "content": "1. 提升素材點擊率"}],
        "text_b": [{"title": "O (目標): 品牌視覺升級", "content": "導入新工具提升質感"}]
    }

    GENERAL_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "作業準確度", "weight": 0.25, "help": "【法遵紅線】導致政府罰款連動績效。"},
            {"item": "電商撥款對帳", "weight": 0.35, "help": "防舞弊核心。100分: 完全一致"},
            {"item": "專案/發薪時效", "weight": 0.20, "help": "【法遵紅線】遲發薪水具勞檢風險。"},
            {"item": "跨部門協作", "weight": 0.20, "help": "90分: 產出SOP無投訴"}
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
        "電商專員": ECOMMERCE_TEMPLATE,
        "自媒體/行銷": MEDIA_TEMPLATE,
        "社群編輯/美編": DESIGN_TEMPLATE,
        "會計/行政": GENERAL_TEMPLATE,
    }

if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []

if 'calculated_score_data' not in st.session_state:
    st.session_state.calculated_score_data = None

if 'cloud_data_cache' not in st.session_state:
    st.session_state.cloud_data_cache = None

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST = list(st.session_state.config_data.keys())

# ==========================================
# 側邊欄導航 (Sidebar Navigation)
# ==========================================
with st.sidebar:
    # 重新設計側邊欄 LOGO 區塊，更簡約現代
    st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <div style='font-size: 48px; line-height: 1;'>💠</div>
        <h3 style='color: #37474F; margin: 10px 0 5px 0; font-weight: 700; letter-spacing: 1px;'>馬尼通訊</h3>
        <p style='color: #78909C; font-size: 12px; margin: 0;'>數位化績效管理中樞</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    menu = st.radio(
        "導覽選單",
        ["📝 新增評核", "📋 雲端紀錄", "⚙️ 參數設定"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.spacer = st.container()
    with st.spacer:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.session_state.batch_queue:
            st.info(f"📥 待上傳紀錄：{len(st.session_state.batch_queue)} 筆")

# ==========================================
# 頁面 1：新增人員評核
# ==========================================
if menu == "📝 新增評核":
    st.markdown('<div class="top-nav"><h2>新增人員評核</h2></div>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1.2, 2], gap="large")
    
    with col_l:
        st.markdown('<div class="section-header">1. 基本資料</div>', unsafe_allow_html=True)
        # 取消邊框，改用純白卡片
        with st.container():
            st.markdown('<div style="background:white; padding:20px; border-radius:12px; border:1px solid #E0E0E0;">', unsafe_allow_html=True)
            input_name = st.text_input("👤 受評人姓名", placeholder="輸入姓名...")
            input_supervisor = st.text_input("👨‍💼 評分主管", placeholder="直屬主管姓名...")
            input_dept = st.selectbox("🏢 所屬部門", options=DEPT_LIST)
            input_level = st.selectbox("⭐ 職稱職等", options=JOB_LEVELS)
            input_date = st.date_input("📅 評核月份", value=datetime.now())
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">2. 職務目標</div>', unsafe_allow_html=True)
        current_config = st.session_state.config_data[input_dept]
        with st.container():
            st.markdown('<div style="background:white; padding:20px; border-radius:12px; border:1px solid #E0E0E0;">', unsafe_allow_html=True)
            st.markdown('<div class="header-mid-a">A. 基礎目標 (KPI)</div>', unsafe_allow_html=True)
            for i, row in enumerate(current_config['text_a']):
                st.text_area(f"● {row['title']}", value=row['content'], height=80, key=f"t_a_{input_dept}_{i}", on_change=update_target_content, args=(input_dept, 'text_a', i, f"t_a_{input_dept}_{i}"))
            
            st.markdown('<div class="header-mid-b" style="margin-top: 15px;">B. 挑戰目標 (OKR)</div>', unsafe_allow_html=True)
            for i, row in enumerate(current_config['text_b']):
                st.text_area(f"● {row['title']}", value=row['content'], height=80, key=f"t_b_{input_dept}_{i}", on_change=update_target_content, args=(input_dept, 'text_b', i, f"t_b_{input_dept}_{i}"))
            st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-header">3. 績效評分維度</div>', unsafe_allow_html=True)
        wa, wb, wc = current_config['section_weights']
        
        # 移除 form 的預設醜邊框，改用純淨背景
        with st.form("score_form_v33", border=False):
            st.markdown('<div style="background:white; padding:25px; border-radius:12px; border:1px solid #E0E0E0; margin-bottom: 20px;">', unsafe_allow_html=True)
            
            # A 區
            st.markdown(f'<div class="header-a">A. 職務基本標準 (KPI) - 權重 {int(wa*100)}%</div>', unsafe_allow_html=True)
            scores_a = []
            c1, c2 = st.columns(2)
            for i, row in enumerate(current_config['basic']):
                with (c1 if i % 2 == 0 else c2):
                    val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", -100, 100, 80, 5, help=row.get('help',''), key=f"va_{i}")
                    scores_a.append(val * row['weight'])
            
            st.markdown("<hr style='margin: 20px 0; border-color: #ECEFF1;'>", unsafe_allow_html=True)
            
            # B 區
            st.markdown(f'<div class="header-b">B. OKR 關鍵結果 (挑戰) - 權重 {int(wb*100)}%</div>', unsafe_allow_html=True)
            scores_b = []
            c3, c4 = st.columns(2)
            for i, row in enumerate(current_config['excellent']):
                with (c3 if i % 2 == 0 else c4):
                    val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", 0, 100, 80, 5, key=f"vb_{i}")
                    scores_b.append(val * row['weight'])
            
            st.markdown("<hr style='margin: 20px 0; border-color: #ECEFF1;'>", unsafe_allow_html=True)
            
            # C 區
            st.markdown(f'<div class="header-c">C. 主管綜合評核 - 權重 {int(wc*100)}%</div>', unsafe_allow_html=True)
            c_mgr_score = st.slider("綜合給分 (1-10)", 1, 10, 8)
            c_mgr_comment = st.text_area("主管反饋建議 (必填)", placeholder="請輸入評價與建議...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("⚖️ 執行計算並鎖定分數", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not input_name: 
                st.error("⚠️ 請輸入受評人姓名！")
            else:
                final_score = (sum(scores_a) * wa) + (sum(scores_b) * wb) + (c_mgr_score * 10 * wc)
                
                # 紀錄細節字串
                a_details = [f"✓ {row['item']}: {st.session_state[f'va_{i}']}" for i, row in enumerate(current_config['basic'])]
                b_details = [f"✓ {row['item']}: {st.session_state[f'vb_{i}']}" for i, row in enumerate(current_config['excellent'])]
                text_records = [f"【{row['title']}】\n{st.session_state.get(f't_a_{input_dept}_{i}', row['content'])}" for i, row in enumerate(current_config['text_a'])]
                text_records += [f"【{row['title']}】\n{st.session_state.get(f't_b_{input_dept}_{i}', row['content'])}" for i, row in enumerate(current_config['text_b'])]

                st.session_state.calculated_score_data = {
                    "score": final_score,
                    "meta": {
                        "name": input_name, "dept": input_dept, "supervisor": input_supervisor, 
                        "date": str(input_date), "level": input_level, "comment": c_mgr_comment,
                        "a_detail_str": "\n".join(a_details), "b_detail_str": "\n".join(b_details), "text_record_str": "\n\n".join(text_records)
                    }
                }
                # 使用 toast 代替大面積的 success，保持畫面乾淨
                st.toast("✅ 計算成功！請確認下方結果。")

        # 獎金試算浮動區
        if st.session_state.calculated_score_data:
            st.markdown('<div class="section-header">4. 核定結果與上傳</div>', unsafe_allow_html=True)
            res = st.session_state.calculated_score_data
            grade_t, grade_m, grade_c = calculate_dynamic_bonus(res['score'], st.session_state.bonus_rules)
            
            with st.container():
                col_res1, col_res2 = st.columns([1, 1])
                with col_res1:
                    st.markdown(f"""
                    <div class="bonus-display" style="height: 100%;">
                        <p style="color: #90A4AE; font-weight: 600; margin-bottom: 5px;">最終核定總分</p>
                        <h1 class="final-score">{res['score']:.2f}</h1>
                        <div class="final-grade" style="background-color: {grade_c};">{grade_t}</div>
                        <p style="color: #607D8B; font-size: 14px;">建議核發獎金：{grade_m} 個月</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_res2:
                    st.markdown('<div class="bonus-display" style="text-align: left; height: 100%;">', unsafe_allow_html=True)
                    base = st.number_input("本薪基數", 0, 200000, 30000, 1000)
                    final_amt = st.number_input("確認實發金額", 0, 500000, int(base * grade_m))
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("➕ 加入待傳清單", use_container_width=True):
                        meta = res['meta']
                        full_data = {
                            "評分日期": meta["date"], "評分主管": meta["supervisor"], "受評姓名": meta["name"],
                            "部門": meta["dept"], "職等": meta["level"], "總分": f"{res['score']:.2f}", "評等": grade_t, 
                            "實得獎金": final_amt, "主管評語": meta["comment"],
                            "A區_基礎評分明細": meta["a_detail_str"], "B區_挑戰評分明細": meta["b_detail_str"], "OKR_目標設定與內容": meta["text_record_str"]
                        }
                        st.session_state.batch_queue.append(full_data)
                        st.toast(f"✅ 已暫存 {meta['name']} 的紀錄")
                    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 頁面 2：雲端評核紀錄 (Dashboard 版)
# ==========================================
elif menu == "📋 雲端紀錄":
    st.markdown('<div class="top-nav"><h2>雲端評核紀錄資料庫</h2></div>', unsafe_allow_html=True)
    
    col_ctrl1, col_ctrl2 = st.columns([1, 4])
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
            else: st.error(tp)

    # 待傳區區塊化
    if st.session_state.batch_queue:
        st.markdown('<div class="section-header">上傳緩衝區</div>', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.batch_queue)[['受評姓名', '部門', '總分', '評等']])
        col_up1, col_up2, col_up3 = st.columns([1,1,2])
        with col_up1:
            if st.button("🚀 正式上傳", use_container_width=True, type="primary"):
                conn, tp = get_gsheets_connection()
                if conn:
                    with st.spinner("安全寫入中..."):
                        try:
                            try:
                                old = conn.read(worksheet="評核紀錄")
                                if isinstance(old, pd.DataFrame):
                                    old = old.dropna(how='all')
                                else:
                                    old = pd.DataFrame()
                            except:
                                old = pd.DataFrame()
                                
                            new = pd.concat([old, pd.DataFrame(st.session_state.batch_queue)], ignore_index=True)
                            conn.update(worksheet="評核紀錄", data=new)
                            st.session_state.batch_queue = []
                            st.session_state.cloud_data_cache = new
                            st.success("寫入成功！")
                            st.balloons()
                        except Exception as e:
                            st.error(f"寫入錯誤: {e}")
                else: st.error(tp)
        with col_up2:
            if st.button("🗑️ 清空暫存", use_container_width=True):
                st.session_state.batch_queue = []
                st.rerun()
    
    st.markdown('<div class="section-header">歷史資料檢視</div>', unsafe_allow_html=True)
    
    if st.session_state.cloud_data_cache is not None and not st.session_state.cloud_data_cache.empty:
        df = st.session_state.cloud_data_cache
        
        # 篩選列
        m_list = ["全部"] + list(df['評分日期'].astype(str).str[:7].unique())
        c_filt1, c_filt2 = st.columns([1, 3])
        with c_filt1:
            s_m = st.selectbox("過濾月份", m_list, label_visibility="collapsed")
        
        if s_m != "全部": df = df[df['評分日期'].astype(str).str.startswith(s_m)]
        st.caption(f"顯示 {len(df)} 筆資料")
        
        # 使用 Grid 佈局呈現卡片
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                st.markdown(f"""
                <div class="history-grid-card">
                    <div style="display:flex; justify-content:space-between; align-items: center;">
                        <span style="font-weight:700; color:#455A64; font-size:16px;">👤 {row.get('受評姓名', '')}</span>
                        <span style="background:#ECEFF1; color:#546E7A; padding:2px 8px; border-radius:10px; font-size:11px;">{row.get('部門', '')}</span>
                    </div>
                    <div style="margin: 10px 0;">
                        <span style="font-size:24px; font-weight:700; color:#607D8B;">{row.get('總分', '')}</span>
                        <span style="font-size:13px; font-weight:600; color:#90A4AE; margin-left:8px;">{row.get('評等', '')}</span>
                    </div>
                    <p style="font-size:11px; color:#90A4AE; margin:0;">主管：{row.get('評分主管', '')} | 日期：{row.get('評分日期', '')}</p>
                    <hr style="margin: 10px 0; border-color: #ECEFF1;">
                    <p style="font-size:12px; color:#546E7A; line-height:1.4;">"{str(row.get('主管評語', ''))[:35]}..."</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("查看詳情"):
                    st.write(row.get('主管評語', '無評語'))
                    st.caption(f"核定獎金：${row.get('實得獎金', 0):,}")
                    
    elif st.session_state.cloud_data_cache is not None and st.session_state.cloud_data_cache.empty:
        st.info("雲端資料庫目前為空。")
    else:
        st.info("請點擊左上方按鈕同步雲端紀錄。")

# ==========================================
# 頁面 3：參數設定
# ==========================================
elif menu == "⚙️ 參數設定":
    st.markdown('<div class="top-nav"><h2>系統參數維護</h2></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div style="background:white; padding:25px; border-radius:12px; border:1px solid #E0E0E0;">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["💰 獎金級距與顏色", "📋 部門考核項目"])
        
        with tab1:
            st.caption("您可以修改顏色代碼(Hex)來改變等級的顯示色彩。建議使用柔和色系。")
            df_b = pd.DataFrame(st.session_state.bonus_rules)
            ed_b = st.data_editor(df_b, num_rows="dynamic", use_container_width=True)
            st.session_state.bonus_rules = ed_b.to_dict('records')
            
        with tab2:
            edit_dept = st.selectbox("選擇要修改的部門", options=DEPT_LIST)
            conf = st.session_state.config_data[edit_dept]
            st.write(f"當前 {edit_dept} 權重配置 (A / B / C)：{conf['section_weights']}")
            st.caption("A區細項 (KPI 基礎)")
            ed_a = st.data_editor(pd.DataFrame(conf['basic']), num_rows="dynamic", use_container_width=True)
            st.session_state.config_data[edit_dept]['basic'] = ed_a.to_dict('records')
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 儲存並套用設定", type="primary"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
