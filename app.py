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
    page_title="總管理處人員評核系統",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS 美化 ---
st.markdown("""
<style>
    .header-a { background-color: #E3F2FD; padding: 10px; border-radius: 5px; color: #1565C0; font-weight: bold; margin-bottom: 5px; border: 1px solid #BBDEFB; }
    .header-b { background-color: #F3E5F5; padding: 10px; border-radius: 5px; color: #6A1B9A; font-weight: bold; margin-bottom: 5px; border: 1px solid #E1BEE7; }
    .header-c { background-color: #FFF3E0; padding: 10px; border-radius: 5px; color: #E65100; font-weight: bold; margin-bottom: 5px; border: 1px solid #FFE0B2; }
    .header-mid-a { background-color: #673AB7; padding: 8px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
    .header-mid-b { background-color: #00897B; padding: 8px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
    .bonus-box { background-color: #FFF8E1; padding: 15px; border-radius: 10px; border: 2px solid #FBC02D; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .result-box { background-color: #FAFAFA; padding: 10px; border-radius: 5px; color: #333; font-size: 22px; font-weight: bold; text-align: center; border: 1px solid #ddd; margin-top: 10px; }
    .grade-badge { font-size: 20px; font-weight: bold; padding: 5px 15px; border-radius: 20px; color: white; display: inline-block; margin: 10px 0;}
    .footer { text-align: center; color: #888; font-size: 12px; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    .history-card { background-color: white; padding: 15px; border-radius: 8px; border-left: 5px solid #1976D2; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

# --- 3. 核心功能：即時存檔回調函數 ---
def update_target_content(dept, section, idx, key):
    new_value = st.session_state[key]
    st.session_state.config_data[dept][section][idx]['content'] = new_value

# --- 4. 初始化資料 ---
if 'bonus_rules' not in st.session_state:
    st.session_state.bonus_rules = [
        {"grade": "S (特優)", "min_score": 90, "months": 1.5, "color": "#D32F2F"},
        {"grade": "A (優良)", "min_score": 80, "months": 1.0, "color": "#1976D2"},
        {"grade": "B+ (甲上)", "min_score": 75, "months": 0.8, "color": "#2E7D32"},
        {"grade": "B- (甲)", "min_score": 70, "months": 0.6, "color": "#388E3C"},
        {"grade": "C (待改善)", "min_score": 60, "months": 0.5, "color": "#FBC02D"},
        {"grade": "D (不合格)", "min_score": 0, "months": 0.0, "color": "#616161"},
    ]

if 'config_data' not in st.session_state:
    ECOMMERCE_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "訂單處理正確率", "weight": 0.30, "help": "【法遵紅線】發錯貨造成的運費損失，不可直接從底薪扣除。\n100分: 0%錯誤\n85分: <0.5%\n60分以下: >1.5%(需檢討SOP)"},
            {"item": "客服聊聊響應", "weight": 0.30, "help": "【法遵紅線】僅限上班時間，嚴禁下班待命防範加班費爭議。\n100分: >95%且<30分\n85分: >90%且<1小時\n60分以下: <85%"},
            {"item": "商城活動參與", "weight": 0.20, "help": "100分: 每月成功提報2檔+大促機制\n85分: 提報1檔\n60分: 僅被動配合"},
            {"item": "上架與庫存準確", "weight": 0.20, "help": "【法遵紅線】一票否決：標錯價(價差>10%)、庫存負數導致超賣補償，當月績效全額取消。"}
        ],
        "excellent": [
            {"item": "KR1: 滯銷品去化", "weight": 0.33, "help": ""},
            {"item": "KR2: 競業價格監控", "weight": 0.33, "help": ""},
            {"item": "KR3: 客單價提升", "weight": 0.34, "help": ""}
        ],
        "threshold": 80,
        "text_a": [
            {"title": "O (目標): 維持優選賣家資格", "content": "1. 確保出貨零失誤\n2. 聊聊回應率維持 95% 以上"},
            {"title": "訂單正確率標準", "content": "100分: 0% 錯誤\n85分: < 0.5% 錯誤\n60分: > 1.5% 錯誤"},
            {"title": "聊聊響應標準", "content": "100分: >95%且<30分\n85分: >90%且<1小時\n60分: <85%"}
        ],
        "text_b": [
            {"title": "O (目標): 提升賣場獲利結構", "content": "1. 降低庫存週轉天數\n2. 提高組合商品銷售比重"},
            {"title": "KR 關鍵結果", "content": "1. 成功去化 3 款滯銷 >90天商品\n2. 提出 2 次競業破盤價分析報告"}
        ]
    }

    MEDIA_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "短影音產出成效", "weight": 0.30, "help": "【法遵紅線】勞務vs結果：12支影片是「勞務」，觀看數是「結果」。不可因結果未達扣底薪。\n100分: 12支+觀看破萬\n85分: 準時12支\n60分以下: <10支"},
            {"item": "官網SEO文章撰寫", "weight": 0.30, "help": "【法遵紅線】原創性要求：複製貼上涉及著作權法，若導致被告列重大疏失。\n100分: 4篇且上首頁\n85分: 4篇且符SEO結構\n60分: 抄襲/未產出"},
            {"item": "社群互動維護", "weight": 0.20, "help": "【法遵紅線】禁止24H待命：嚴禁要求員工下班回訊息。\n90分: 上班時間內回覆<2小時\n60分: 累積逾24小時未回"},
            {"item": "導流貢獻(ROAS)", "weight": 0.20, "help": "【法遵預警】若公司未給予廣告預算或素材，不可因成效不佳懲處。\n100分: >50筆詢單\n85分: >30筆\n60分: 無效益"}
        ],
        "excellent": [
            {"item": "KR1: 爆款影片", "weight": 0.33, "help": ""},
            {"item": "KR2: 關鍵字排名", "weight": 0.33, "help": ""},
            {"item": "KR3: 時事跟風速度", "weight": 0.34, "help": ""}
        ],
        "threshold": 80,
        "text_a": [
            {"title": "O (目標): 建立流量護城河", "content": "1. 穩定產出高品質內容\n2. 經營官網長尾流量"},
            {"title": "短影音標準", "content": "100分: 12支 + 觀看破萬\n85分: 12支準時完成\n60分: 數量未達標"},
            {"title": "SEO文章標準", "content": "100分: 4篇 + 關鍵字上首頁\n85分: 4篇 + 符合SEO結構\n60分: 未產出"}
        ],
        "text_b": [
            {"title": "O (目標): 擴大品牌心佔率", "content": "讓馬尼成為台南 3C 資訊首選"},
            {"title": "KR 關鍵結果", "content": "1. 打造 1 支互動率 >5% 的影片\n2. 3C 重大新聞發生後 4 小時內產出內容"}
        ]
    }

    DESIGN_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "素材完成時效", "weight": 0.30, "help": "【法遵紅線】延遲若導致補助取消，須留存「具體損害證明」。\n100分: 提前1天完成\n85分: 準時\n0分: 開天窗"},
            {"item": "設計修改次數", "weight": 0.30, "help": "【法遵預警】須區分「主管改主意」與「美編做錯」。\n100分: 一次過稿\n85分: 修改2次內\n60分以下: 修改>5次"},
            {"item": "版權與品牌規範", "weight": 0.20, "help": "【法遵紅線】所有素材/字體均有合法授權。\n100分: 完全合規\n-100分(重大疏失): 盜版致侵權警告，負賠償責任。"},
            {"item": "點擊率(CTR)", "weight": 0.20, "help": "屬激勵性質，不可作為懲戒依據。\n100分: 高於平均20%\n80分: 持平"}
        ],
        "excellent": [
            {"item": "KR1: A/B Test提案", "weight": 0.33, "help": ""},
            {"item": "KR2: AI工具應用", "weight": 0.33, "help": ""},
            {"item": "KR3: 視覺優化", "weight": 0.34, "help": ""}
        ],
        "threshold": 85,
        "text_a": [
            {"title": "O (目標): 視覺傳達精準化", "content": "1. 提升素材點擊率\n2. 減少溝通修改成本"},
            {"title": "時效標準", "content": "100分: 提前1天完稿\n85分: 準時完稿\n0分: 開天窗"},
            {"title": "修改標準", "content": "100分: 一次過稿\n85分: 修改2次內\n60分: 修改>5次"}
        ],
        "text_b": [
            {"title": "O (目標): 品牌視覺升級", "content": "導入新工具提升質感與效率"},
            {"title": "KR 關鍵結果", "content": "1. 主動提出 2 款不同風格封面圖測試 CTR\n2. 導入 AI 去背/生成工具縮短工時"}
        ]
    }

    GENERAL_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "作業準確度", "weight": 0.25, "help": "【法遵紅線】罰鍰連動：導致政府罰款(漏保/滯納金)連動績效，留存罰單副本。\n100分: 零誤差"},
            {"item": "電商撥款對帳", "weight": 0.35, "help": "【法遵紅線】防舞弊核心：發生帳務不符且隱匿不報，為勞基法12條直接解雇事由。\n100分: IMEI/訂單/撥款完全一致"},
            {"item": "專案/發薪時效", "weight": 0.20, "help": "【法遵紅線】遲發薪水具集體勞檢風險。\n100分: 5號前完成\n60分: 逾期未報備"},
            {"item": "跨部門協作", "weight": 0.20, "help": "將「態度」量化為「產出物」。\n90分: 產出SOP無投訴\n60分: 溝通傲慢"}
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

# v31.0: 暫存雲端抓下來的歷史資料
if 'cloud_data_cache' not in st.session_state:
    st.session_state.cloud_data_cache = None

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST = list(st.session_state.config_data.keys())

# --- 5. 核心邏輯：動態獎金計算 ---
def calculate_dynamic_bonus(score, rules_data):
    sorted_rules = sorted(rules_data, key=lambda x: x['min_score'], reverse=True)
    for rule in sorted_rules:
        if score >= rule['min_score']:
            return rule['grade'], rule['months'], rule['color']
    return "N/A", 0.0, "#000000"

# --- 共用連線函式 ---
def get_gsheets_connection():
    spreadsheet_url = None
    json_str = None
    
    if st.secrets.get("connections") and st.secrets["connections"].get("gsheets"):
        spreadsheet_url = st.secrets["connections"]["gsheets"].get("spreadsheet")
    if st.secrets.get("gcp_service_account_json"):
        json_str = st.secrets.get("gcp_service_account_json")
        
    is_legacy_format = False
    if not json_str and st.secrets.get("connections") and st.secrets["connections"].get("gsheets") and "client_email" in st.secrets["connections"]["gsheets"]:
        is_legacy_format = True
    
    if not spreadsheet_url or (not json_str and not is_legacy_format):
        return None, "找不到金鑰設定或網址。"
    
    temp_key_path = "/tmp/gsheets_key.json"
    os.makedirs("/tmp", exist_ok=True)
    
    try:
        if is_legacy_format:
            legacy_secrets = dict(st.secrets["connections"]["gsheets"])
            legacy_secrets.pop("spreadsheet", None) 
            with open(temp_key_path, "w") as f:
                json.dump(legacy_secrets, f)
        else:
            key_dict = json.loads(json_str)
            with open(temp_key_path, "w") as f:
                json.dump(key_dict, f)
                
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_key_path
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn, temp_key_path
    except Exception as e:
        return None, str(e)

# --- 6. 主標題 ---
st.title("📊 總管理處人員評核系統 (v31.0)")

# --- 7. 版面佈局 ---
col_left, col_mid, col_right = st.columns([0.8, 1.5, 0.7], gap="medium")

# ==========================================
# 左欄：1. 人員資料 & 2. 每月職務目標 (O: Objectives)
# ==========================================
with col_left:
    st.markdown("### 1. 人員資料")
    with st.container(border=True):
        input_name = st.text_input("姓名", value="")
        input_supervisor = st.text_input("主管", value="")
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            input_dept = st.selectbox("部門", options=DEPT_LIST, index=0)
        with c_l2:
            input_level = st.selectbox("職等", options=JOB_LEVELS, index=1)
        input_date = st.date_input("日期", value=datetime.now())
    
    current_config = st.session_state.config_data[input_dept]
    
    st.markdown("### 2. 職務目標 (Objectives)")
    with st.expander("📝 設定本月 O 與 KR 標準 (自動存檔)", expanded=False):
        st.markdown('<div class="header-mid-a">A. 基礎目標 (KPI/Maintenance)</div>', unsafe_allow_html=True)
        for i, row in enumerate(current_config['text_a']):
            unique_key = f"target_a_{input_dept}_{i}"
            st.text_area(f"● {row['title']}", value=row['content'], height=80, key=unique_key, on_change=update_target_content, args=(input_dept, 'text_a', i, unique_key))

        st.markdown('<div class="header-mid-b">B. 挑戰目標 (OKR/Growth)</div>', unsafe_allow_html=True)
        for i, row in enumerate(current_config['text_b']):
            unique_key = f"target_b_{input_dept}_{i}"
            st.text_area(f"● {row['title']}", value=row['content'], height=80, key=unique_key, on_change=update_target_content, args=(input_dept, 'text_b', i, unique_key))

# ==========================================
# 中欄：3. 評分內容 (內建法遵 Tooltip)
# ==========================================
with col_mid:
    st.markdown("### 3. 評分內容")
    wa, wb, wc = current_config['section_weights']

    with st.form("score_form"):
        st.markdown(f'<div class="header-a">A. 職務基本標準 (權重 {int(wa*100)}%) - KPI</div>', unsafe_allow_html=True)
        scores_a = []
        cols_a = st.columns(2)
        for i, row in enumerate(current_config['basic']):
            with cols_a[i % 2]:
                help_text = row.get("help", "")
                val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", min_value=-100, max_value=100, value=80, step=5, key=f"a_{i}", help=help_text)
                scores_a.append(val * row['weight'])

        st.markdown(f'<div class="header-b">B. OKR 關鍵結果 (權重 {int(wb*100)}%) - 挑戰</div>', unsafe_allow_html=True)
        scores_b = []
        cols_b = st.columns(2)
        for i, row in enumerate(current_config['excellent']):
            with cols_b[i % 2]:
                help_text = row.get("help", "")
                val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", min_value=0, max_value=100, value=80, step=5, key=f"b_{i}", help=help_text)
                scores_b.append(val * row['weight'])

        st.markdown(f'<div class="header-c">C. 主管綜合評核 (權重 {int(wc*100)}%)</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            mgr_score = st.selectbox("評分 (1-10)", options=range(1, 11), index=7)
        with col_c2:
            mgr_comment = st.text_area("反饋評語", height=38, placeholder="分數低於60分需詳述原因...")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📊 計算總分", use_container_width=True, type="primary")

    if submitted:
        total_a = sum(scores_a)
        total_b = sum(scores_b)
        total_c = mgr_score * 10 
        final_score = (total_a * wa) + (total_b * wb) + (total_c * wc)
        
        a_details = []
        for i, row in enumerate(current_config['basic']):
            a_details.append(f"✓ {row['item']}: {st.session_state[f'a_{i}']}")
        
        b_details = []
        for i, row in enumerate(current_config['excellent']):
            b_details.append(f"✓ {row['item']}: {st.session_state[f'b_{i}']}")
            
        text_records = []
        for i, row in enumerate(current_config['text_a']):
            text_records.append(f"【{row['title']}】\n{st.session_state.get(f'target_a_{input_dept}_{i}', row['content'])}")
        for i, row in enumerate(current_config['text_b']):
            text_records.append(f"【{row['title']}】\n{st.session_state.get(f'target_b_{input_dept}_{i}', row['content'])}")
        
        st.session_state.calculated_score_data = {
            "score": final_score,
            "meta": {
                "name": input_name, "dept": input_dept, "supervisor": input_supervisor,
                "date": str(input_date), "level": input_level, "comment": mgr_comment,
                "a_detail_str": "\n".join(a_details),
                "b_detail_str": "\n".join(b_details),
                "text_record_str": "\n\n".join(text_records)
            }
        }
        
        if final_score < 60:
            st.error(f"⚠️ 警告：總分 {final_score:.2f} 低於及格線，請務必安排面談並留存輔導紀錄 (PIP)。")
        else:
            st.success(f"計算完成！總分：{final_score:.2f}")

# ==========================================
# 右欄：4. 獎金試算 & 5. 設定匯出 & 儀表板
# ==========================================
with col_right:
    st.markdown("### 4. 獎金試算 & 系統功能")
    
    # 將所有右側功能收納進 Tab 中，讓介面更清爽
    tab_calc, tab_db, tab_settings = st.tabs(["💰 試算與暫存", "📊 歷史儀表板", "⚙️ 設定"])

    # --- Tab 1: 試算與上傳 ---
    with tab_calc:
        if st.session_state.calculated_score_data:
            current_score = st.session_state.calculated_score_data["score"]
            meta_name = st.session_state.calculated_score_data["meta"]["name"]
            
            st.markdown(f'<div class="result-box">總分：{current_score:.2f}</div>', unsafe_allow_html=True)
            grade_text, grade_months, grade_color = calculate_dynamic_bonus(current_score, st.session_state.bonus_rules)
            
            st.markdown(f"""
            <div style="text-align: center;">
                <span class="grade-badge" style="background-color: {grade_color};">{grade_text}</span>
                <span style="font-size: 18px; font-weight: bold; color: #555;">{grade_months} 個月</span>
            </div>
            """, unsafe_allow_html=True)
            st.divider()
            
            c_b1, c_b2 = st.columns([2, 1])
            with c_b1:
                bonus_base = st.number_input("月薪 (Base)", value=0, step=1000, key="calc_base")
            with c_b2:
                bonus_multi = st.number_input("倍率", value=1.0, step=0.1, key="calc_multi")
            
            final_bonus = max(0, bonus_base * grade_months * bonus_multi)
            
            if bonus_base > 0:
                st.info(f"💵 核定獎金：${int(final_bonus):,}")
                
            final_confirm_bonus = st.number_input("最終實發", value=int(final_bonus), step=100, key="calc_final")
            
            if st.button("➕ 加入待匯出清單", type="secondary", use_container_width=True):
                meta = st.session_state.calculated_score_data["meta"]
                full_data = {
                    "評分日期": meta["date"], 
                    "評分主管": meta["supervisor"], 
                    "受評姓名": meta["name"],
                    "部門": meta["dept"], 
                    "職等": meta["level"], 
                    "總分": f"{current_score:.2f}",
                    "評等": grade_text, 
                    "實得獎金": final_confirm_bonus,
                    "主管評語": meta["comment"],
                    "A區_基礎評分明細": meta["a_detail_str"],
                    "B區_挑戰評分明細": meta["b_detail_str"],
                    "OKR_目標設定與內容": meta["text_record_str"]
                }
                st.session_state.batch_queue.append(full_data)
                st.toast(f"✅ {meta['name']} 已加入清單！")
        else:
            st.info("👈 請先在中欄計算總分")

        if len(st.session_state.batch_queue) > 0:
            st.markdown("---")
            st.markdown("##### 📥 待上傳清單")
            df_export = pd.DataFrame(st.session_state.batch_queue)
            st.dataframe(df_export[['受評姓名', '部門', '總分', '評等']], hide_index=True)
            
            if st.button("🚀 批次上傳至 Google Sheets", type="primary", use_container_width=True):
                if not HAS_GSHEETS:
                    st.error("未安裝套件")
                else:
                    conn, temp_path_or_error = get_gsheets_connection()
                    if conn is None:
                        st.error(temp_path_or_error)
                    else:
                        try:
                            with st.spinner("同步中..."):
                                existing_data = pd.DataFrame()
                                try:
                                    existing_data = conn.read(worksheet="評核紀錄")
                                    if not isinstance(existing_data, pd.DataFrame):
                                        existing_data = pd.DataFrame()
                                    else:
                                        existing_data = existing_data.dropna(how='all') 
                                except Exception: pass 
                                    
                                if existing_data.empty:
                                    updated_data = df_export
                                else:
                                    updated_data = pd.concat([existing_data, df_export], ignore_index=True)
                                    
                                conn.update(worksheet="評核紀錄", data=updated_data)
                            st.success("✅ 上傳成功！")
                            st.session_state.batch_queue = [] # 上傳後清空
                            st.session_state.cloud_data_cache = updated_data # 更新快取
                        except Exception as e:
                            st.error(f"寫入失敗：{e}")
                        finally:
                            if os.path.exists(temp_path_or_error): os.remove(temp_path_or_error)
            
            if st.button("🗑️ 清空清單"):
                st.session_state.batch_queue = []
                st.rerun()

    # --- Tab 2: 歷史紀錄儀表板 (v31 核心功能) ---
    with tab_db:
        st.markdown("##### 雲端資料庫檢視")
        st.caption("從 Google Sheets 讀取並美化呈現，無需直接看醜醜的試算表。")
        
        if st.button("🔄 從雲端載入最新紀錄", use_container_width=True):
            conn, temp_path_or_error = get_gsheets_connection()
            if conn is None:
                st.error(temp_path_or_error)
            else:
                with st.spinner("正在下載資料..."):
                    try:
                        df_cloud = conn.read(worksheet="評核紀錄")
                        df_cloud = df_cloud.dropna(how='all')
                        st.session_state.cloud_data_cache = df_cloud
                        st.success("✅ 載入成功！")
                    except Exception as e:
                        st.error(f"讀取失敗：{e}")
                    finally:
                        if os.path.exists(temp_path_or_error): os.remove(temp_path_or_error)

        if st.session_state.cloud_data_cache is not None and not st.session_state.cloud_data_cache.empty:
            df = st.session_state.cloud_data_cache
            
            # 提供簡單的篩選器
            selected_month = st.selectbox("📅 選擇月份", options=["全部"] + list(df['評分日期'].astype(str).str[:7].unique()))
            
            if selected_month != "全部":
                df = df[df['評分日期'].astype(str).str.startswith(selected_month)]
                
            st.markdown(f"**共找到 {len(df)} 筆紀錄**")
            
            # 將資料轉化為漂亮的卡片
            for idx, row in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="history-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; color:#1565C0;">👤 {row.get('受評姓名', '未知')} ({row.get('部門', '')} - {row.get('職等', '')})</h4>
                            <span style="background-color:#E3F2FD; padding:3px 10px; border-radius:15px; font-weight:bold;">總分: {row.get('總分', '')} ({row.get('評等', '')})</span>
                        </div>
                        <p style="margin:5px 0 0 0; font-size:12px; color:#666;">評分主管：{row.get('評分主管', '')} | 日期：{row.get('評分日期', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("查看詳細各項分數與評語"):
                        st.markdown("**主管評語：**")
                        st.info(row.get('主管評語', '無'))
                        
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            st.markdown("**A區_基礎評分**")
                            st.text(row.get('A區_基礎評分明細', ''))
                        with col_d2:
                            st.markdown("**B區_挑戰評分**")
                            st.text(row.get('B區_挑戰評分明細', ''))
                            
                        st.markdown("**OKR 目標內容**")
                        st.caption(str(row.get('OKR_目標設定與內容', '')).replace('\n', '  \n'))
        else:
            st.info("尚無資料，請先點擊載入按鈕。")

    # --- Tab 3: 設定 ---
    with tab_settings:
        st.caption("修改後請按 Enter 套用")
        with st.expander("部門評分權重 & 項目", expanded=False):
            edit_dept = st.selectbox("選擇部門", options=DEPT_LIST)
            edit_config = st.session_state.config_data[edit_dept]
            c_w1, c_w2, c_w3 = st.columns(3)
            nw_a = c_w1.number_input("A區權重", value=edit_config['section_weights'][0], step=0.05)
            nw_b = c_w2.number_input("B區權重", value=edit_config['section_weights'][1], step=0.05)
            nw_c = c_w3.number_input("C區權重", value=edit_config['section_weights'][2], step=0.05)
            st.session_state.config_data[edit_dept]['section_weights'] = [nw_a, nw_b, nw_c]
            
            st.caption("A區細項 (KPI - 基礎)")
            df_b = pd.DataFrame(edit_config['basic'])
            ed_b = st.data_editor(df_b, num_rows="dynamic", key="ed_b")
            st.session_state.config_data[edit_dept]['basic'] = ed_b.to_dict('records')
            
            st.caption("B區細項 (OKR - 挑戰)")
            df_e = pd.DataFrame(edit_config['excellent'])
            ed_e = st.data_editor(df_e, num_rows="dynamic", key="ed_e")
            st.session_state.config_data[edit_dept]['excellent'] = ed_e.to_dict('records')

        if st.button("🔄 重整套用"):
            st.rerun()

# --- 7. 系統資訊 (Footer) ---
with st.expander("ℹ️ 系統資訊 (System Info)", expanded=False):
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 13px;">
        <p><b>版本歷程</b></p>
        <ul style="text-align: left; display: inline-block;">
            <li>v31.0: 新增「歷史儀表板」功能，在系統內直接美化呈現 Google Sheets 資料。</li>
            <li>v30.1: 兼容新舊版 Google Sheets Secrets 設定格式。</li>
            <li>v30.0: 優化 Google Sheets 匯出格式，將各部門欄位收納對齊，並加入單項給分明細。</li>
        </ul>
        <br>
        <p>© 2026 馬尼通訊總管理處考核系統</p>
    </div>
    """, unsafe_allow_html=True)
