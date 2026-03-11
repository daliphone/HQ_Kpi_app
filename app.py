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
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 終極 UI 優化 CSS ---
st.markdown("""
<style>
    /* 全域字體與背景 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans TC', sans-serif; background-color: #F0F2F5; }

    /* 隱藏預設元件 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 頂部導航模擬 */
    .top-nav {
        background: linear-gradient(90deg, #1A237E 0%, #1A73E8 100%);
        padding: 20px;
        border-radius: 0px 0px 15px 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
    }

    /* 現代化卡片容器 */
    .st-emotion-cache-12w0qpk { border-radius: 12px; } 
    
    .main-card {
        background-color: white;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
        border: 1px solid #E8EAED;
        margin-bottom: 25px;
    }
    
    /* 區塊標題設計 */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1A237E;
        border-left: 6px solid #1A73E8;
        padding-left: 15px;
        margin: 25px 0 15px 0;
    }

    /* 評分區專用 */
    .score-zone {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #DEE2E6;
        margin-bottom: 15px;
    }
    
    /* 獎金看板 */
    .bonus-display {
        background: #F8F9FA;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        border: 2px solid #E8EAED;
    }
    .final-score { font-size: 48px; font-weight: 800; color: #1A73E8; margin: 0; }
    .final-grade { font-size: 24px; font-weight: 700; color: white; background: #D93025; padding: 5px 20px; border-radius: 20px; display: inline-block; margin: 10px 0; }

    /* 歷史紀錄格狀卡片 */
    .history-grid-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        height: 100%;
        transition: all 0.3s ease;
    }
    .history-grid-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.08);
        border-color: #1A73E8;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心功能：動態獎金計算 (修復：補回此核心函式) ---
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

# --- 4. 初始化資料 (修復：補回完整範本) ---
if 'bonus_rules' not in st.session_state:
    st.session_state.bonus_rules = [
        {"grade": "S (特優)", "min_score": 90, "months": 1.5, "color": "#D93025"},
        {"grade": "A (優良)", "min_score": 80, "months": 1.0, "color": "#1A73E8"},
        {"grade": "B+ (甲上)", "min_score": 75, "months": 0.8, "color": "#188038"},
        {"grade": "B- (甲)", "min_score": 70, "months": 0.6, "color": "#34A853"},
        {"grade": "C (待改善)", "min_score": 60, "months": 0.5, "color": "#F9AB00"},
        {"grade": "D (不合格)", "min_score": 0, "months": 0.0, "color": "#5F6368"},
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
    # 使用 Markdown Emoji 取代外部圖片網址，確保 LOGO 永遠穩定顯示
    st.markdown("<div style='text-align: center; font-size: 65px; margin-bottom: -20px;'>💎</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #1A237E; text-align: center;'>馬尼通訊</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #5F6368; font-size: 13px; margin-top: -10px;'>數位化績效管理系統 v33.1</p>", unsafe_allow_html=True)
    st.divider()
    
    menu = st.radio(
        "系統選單",
        ["📝 新增人員評核", "📋 雲端評核紀錄", "⚙️ 系統參數設定"],
        index=0
    )
    
    st.spacer = st.container()
    with st.spacer:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.session_state.batch_queue:
            st.warning(f"🛒 待上傳紀錄：{len(st.session_state.batch_queue)} 筆")

# ==========================================
# 頁面 1：新增人員評核
# ==========================================
if menu == "📝 新增人員評核":
    st.markdown('<div class="top-nav"><h1>📝 新增人員評核表單</h1></div>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1.2, 2], gap="large")
    
    with col_l:
        st.markdown('<div class="section-header">1. 受評人基本資料</div>', unsafe_allow_html=True)
        with st.container(border=True):
            input_name = st.text_input("受評人姓名", placeholder="請輸入姓名...")
            input_supervisor = st.text_input("評分主管", placeholder="直屬主管姓名...")
            input_dept = st.selectbox("所屬部門", options=DEPT_LIST)
            input_level = st.selectbox("職稱職等", options=JOB_LEVELS)
            input_date = st.date_input("評核月份", value=datetime.now())
        
        st.markdown('<div class="section-header">2. 職務目標 (O)</div>', unsafe_allow_html=True)
        current_config = st.session_state.config_data[input_dept]
        with st.expander("📝 編輯本月目標與內容", expanded=True):
            for i, row in enumerate(current_config['text_a']):
                st.text_area(f"● {row['title']}", value=row['content'], height=100, key=f"t_a_{input_dept}_{i}", on_change=update_target_content, args=(input_dept, 'text_a', i, f"t_a_{input_dept}_{i}"))
            for i, row in enumerate(current_config['text_b']):
                st.text_area(f"● {row['title']}", value=row['content'], height=100, key=f"t_b_{input_dept}_{i}", on_change=update_target_content, args=(input_dept, 'text_b', i, f"t_b_{input_dept}_{i}"))

    with col_r:
        st.markdown('<div class="section-header">3. 績效評分維度</div>', unsafe_allow_html=True)
        wa, wb, wc = current_config['section_weights']
        
        with st.form("score_form_v33"):
            # A 區
            st.markdown(f"**🟢 A. 職務基本標準 (KPI) - 權重 {int(wa*100)}%**")
            scores_a = []
            c1, c2 = st.columns(2)
            for i, row in enumerate(current_config['basic']):
                with (c1 if i % 2 == 0 else c2):
                    val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", -100, 100, 80, 5, help=row.get('help',''), key=f"va_{i}")
                    scores_a.append(val * row['weight'])
            
            st.divider()
            # B 區
            st.markdown(f"**🟣 B. OKR 關鍵結果 (挑戰) - 權重 {int(wb*100)}%**")
            scores_b = []
            c3, c4 = st.columns(2)
            for i, row in enumerate(current_config['excellent']):
                with (c3 if i % 2 == 0 else c4):
                    val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", 0, 100, 80, 5, key=f"vb_{i}")
                    scores_b.append(val * row['weight'])
            
            st.divider()
            # C 區
            st.markdown(f"**🟠 C. 主管綜合評核 - 權重 {int(wc*100)}%**")
            c_mgr_score = st.slider("綜合給分 (1-10)", 1, 10, 8)
            c_mgr_comment = st.text_area("主管反饋建議 (必填)", placeholder="請輸入評價與建議...")
            
            submitted = st.form_submit_button("⚖️ 執行計算並鎖定分數", use_container_width=True, type="primary")

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
                st.success("✅ 計算成功！請於下方確認獎金並加入待傳清單。")

        # 獎金試算浮動區
        if st.session_state.calculated_score_data:
            st.markdown('<div class="section-header">4. 獎金試算與確認</div>', unsafe_allow_html=True)
            res = st.session_state.calculated_score_data
            grade_t, grade_m, grade_c = calculate_dynamic_bonus(res['score'], st.session_state.bonus_rules)
            
            with st.container():
                st.markdown(f"""
                <div class="bonus-display">
                    <p style="color: #5F6368; font-weight: 600;">最終核定總分</p>
                    <h1 class="final-score">{res['score']:.2f}</h1>
                    <div class="final-grade" style="background-color: {grade_c};">{grade_t}</div>
                    <p>建議核發獎金：{grade_m} 個月</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_b1, col_b2 = st.columns(2)
                base = col_b1.number_input("月薪基數", 0, 200000, 30000, 1000)
                final_amt = col_b2.number_input("最終實發金額", 0, 500000, int(base * grade_m))
                
                if st.button("➕ 加入待上傳清單", use_container_width=True, type="secondary"):
                    meta = res['meta']
                    full_data = {
                        "評分日期": meta["date"], "評分主管": meta["supervisor"], "受評姓名": meta["name"],
                        "部門": meta["dept"], "職等": meta["level"], "總分": f"{res['score']:.2f}", "評等": grade_t, 
                        "實得獎金": final_amt, "主管評語": meta["comment"],
                        "A區_基礎評分明細": meta["a_detail_str"], "B區_挑戰評分明細": meta["b_detail_str"], "OKR_目標設定與內容": meta["text_record_str"]
                    }
                    st.session_state.batch_queue.append(full_data)
                    st.toast(f"✅ 已暫存 {meta['name']} 的紀錄")

# ==========================================
# 頁面 2：雲端評核紀錄 (Dashboard 版)
# ==========================================
elif menu == "📋 雲端評核紀錄":
    st.markdown('<div class="top-nav"><h1>📋 雲端評核紀錄管理中心</h1></div>', unsafe_allow_html=True)
    
    col_ctrl1, col_ctrl2 = st.columns([1, 4])
    with col_ctrl1:
        if st.button("🔄 同步最新雲端資料", use_container_width=True, type="primary"):
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
        with st.expander(f"📥 待上傳緩衝區 ({len(st.session_state.batch_queue)} 筆)", expanded=True):
            st.table(pd.DataFrame(st.session_state.batch_queue)[['受評姓名', '部門', '總分', '評等']])
            if st.button("🚀 正式批次同步至 Google Sheets", use_container_width=True):
                conn, tp = get_gsheets_connection()
                if conn:
                    with st.spinner("寫入中..."):
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
                            st.success("雲端寫入成功！")
                            st.balloons()
                        except Exception as e:
                            st.error(f"寫入錯誤: {e}")
                else: st.error(tp)
    
    st.divider()
    
    # 歷史紀錄 Dashboard
    if st.session_state.cloud_data_cache is not None and not st.session_state.cloud_data_cache.empty:
        df = st.session_state.cloud_data_cache
        st.markdown(f"### 歷史數據概覽 (共 {len(df)} 筆)")
        
        # 篩選列
        m_list = ["全部"] + list(df['評分日期'].astype(str).str[:7].unique())
        s_m = st.selectbox("📅 過濾月份", m_list)
        if s_m != "全部": df = df[df['評分日期'].astype(str).str.startswith(s_m)]
        
        # 使用 Grid 佈局呈現卡片
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                st.markdown(f"""
                <div class="history-grid-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-weight:700; color:#1A237E; font-size:18px;">👤 {row.get('受評姓名', '')}</span>
                        <span style="background:#E8F0FE; color:#1A73E8; padding:2px 8px; border-radius:10px; font-size:12px;">{row.get('部門', '')}</span>
                    </div>
                    <div style="margin: 15px 0;">
                        <span style="font-size:28px; font-weight:800; color:#1A73E8;">{row.get('總分', '')}</span>
                        <span style="font-size:14px; font-weight:600; color:#D93025; margin-left:10px;">({row.get('評等', '')})</span>
                    </div>
                    <p style="font-size:12px; color:#666; margin:0;">主管：{row.get('評分主管', '')}</p>
                    <p style="font-size:12px; color:#666; margin:0;">日期：{row.get('評分日期', '')}</p>
                    <hr style="margin: 10px 0;">
                    <p style="font-size:13px; color:#333; line-height:1.4;">"{str(row.get('主管評語', ''))[:40]}..."</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("🔍 詳情"):
                    st.write(row.get('主管評語', '無評語'))
                    st.caption(f"核定獎金：${row.get('實得獎金', 0):,}")
                    
    elif st.session_state.cloud_data_cache is not None and st.session_state.cloud_data_cache.empty:
        st.info("雲端資料庫目前為空，請新增評核並上傳。")
    else:
        st.info("請點擊左上方按鈕同步雲端紀錄。")

# ==========================================
# 頁面 3：參數設定
# ==========================================
elif menu == "⚙️ 系統參數設定":
    st.markdown('<div class="top-nav"><h1>⚙️ 系統參數設定</h1></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["💰 獎金級距", "📋 部門項目"])
        
        with tab1:
            df_b = pd.DataFrame(st.session_state.bonus_rules)
            ed_b = st.data_editor(df_b, num_rows="dynamic", use_container_width=True)
            st.session_state.bonus_rules = ed_b.to_dict('records')
            
        with tab2:
            edit_dept = st.selectbox("修改部門", options=DEPT_LIST)
            conf = st.session_state.config_data[edit_dept]
            st.write(f"當前 {edit_dept} 權重：{conf['section_weights']}")
            st.caption("A區細項 (KPI)")
            ed_a = st.data_editor(pd.DataFrame(conf['basic']), num_rows="dynamic", use_container_width=True)
            st.session_state.config_data[edit_dept]['basic'] = ed_a.to_dict('records')
            
        if st.button("💾 儲存並套用所有設定"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. Footer ---
st.markdown("""
<div class="footer">
    <p>馬尼行動通訊總管理處 | 數位化管理系統 © 2026</p>
    <p style="font-size:10px;">系統版本 v33.1 - 核心修復與模組化導航</p>
</div>
""", unsafe_allow_html=True)
