import streamlit as st
import pandas as pd
from datetime import datetime
import io

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

# *** 核心更新：寫入詳細評分標準與「法遵預警 Tooltip」 ***
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
        ],
        "text_b": [
            {"title": "O (目標): 提升賣場獲利結構", "content": "1. 降低庫存週轉天數\n2. 提高組合商品銷售比重"},
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
        "text_a": [{"title": "O (目標): 建立流量護城河", "content": "1. 穩定產出高品質內容\n2. 經營官網長尾流量"}],
        "text_b": [{"title": "O (目標): 擴大品牌心佔率", "content": "讓馬尼成為台南 3C 資訊首選"}]
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
        "text_a": [{"title": "O (目標): 視覺傳達精準化", "content": "1. 提升素材點擊率\n2. 減少溝通修改成本"}],
        "text_b": [{"title": "O (目標): 品牌視覺升級", "content": "導入新工具提升質感與效率"}]
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

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST = list(st.session_state.config_data.keys())

# --- 5. 核心邏輯：動態獎金計算 ---
def calculate_dynamic_bonus(score, rules_data):
    sorted_rules = sorted(rules_data, key=lambda x: x['min_score'], reverse=True)
    for rule in sorted_rules:
        if score >= rule['min_score']:
            return rule['grade'], rule['months'], rule['color']
    return "N/A", 0.0, "#000000"

# --- 6. 主標題 ---
st.title("📊 總管理處人員評核系統 (v29)")

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
                # 加入 help 參數，滑鼠移過去會顯示法遵紅線與標準
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
        
        st.session_state.calculated_score_data = {
            "score": final_score,
            "meta": {
                "name": input_name, "dept": input_dept, "supervisor": input_supervisor,
                "date": str(input_date), "level": input_level, "comment": mgr_comment
            }
        }
        
        # 不適任證據鏈預警
        if final_score < 60:
            st.error(f"⚠️ 警告：總分 {final_score:.2f} 低於及格線，請務必安排面談並留存輔導紀錄 (PIP)。")
        else:
            st.success(f"計算完成！總分：{final_score:.2f}")

# ==========================================
# 右欄：4. 獎金試算 & 5. 設定匯出
# ==========================================
with col_right:
    st.markdown("### 4. 年終獎金試算")
    with st.container(border=True):
        st.markdown("##### 💰 級距制計算機")
        
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
            
            # 薪資計算保險絲：獎金最低為 0，不可倒扣底薪
            final_bonus = max(0, bonus_base * grade_months * bonus_multi)
            
            if bonus_base > 0:
                st.info(f"💵 核定獎金：${int(final_bonus):,}")
            else:
                st.caption("請輸入月薪")

            st.markdown("---")
            final_confirm_bonus = st.number_input("最終實發", value=int(final_bonus), step=100, key="calc_final")
            
            if st.button("➕ 加入待匯出清單", type="secondary", use_container_width=True):
                meta = st.session_state.calculated_score_data["meta"]
                text_data = {}
                try:
                    for i, row in enumerate(current_config['text_a']):
                        k = f"target_a_{input_dept}_{i}"
                        text_data[f"A_{row['title']}"] = st.session_state.get(k, row['content'])
                    for i, row in enumerate(current_config['text_b']):
                        k = f"target_b_{input_dept}_{i}"
                        text_data[f"B_{row['title']}"] = st.session_state.get(k, row['content'])
                except: pass

                full_data = {
                    "評分日期": meta["date"], "評分主管": meta["supervisor"], "受評姓名": meta["name"],
                    "職等": meta["level"], "部門": meta["dept"], "總分": f"{current_score:.2f}",
                    "評等": grade_text, "核定月數": str(grade_months), "實得獎金": final_confirm_bonus,
                    "主管評語": meta["comment"],
                    **text_data
                }
                st.session_state.batch_queue.append(full_data)
                st.toast(f"✅ {meta['name']} 已加入清單！")
        else:
            st.info("👈 請先在中欄計算總分")

    # --- 設定與匯出 (加入 Google Sheets 同步按鈕) ---
    st.markdown("### 5. 設定與匯出")
    tab1, tab2 = st.tabs(["⚙️ 參數設定", "📥 匯出與雲端"])

    with tab1:
        st.caption("修改後請按 Enter 套用")
        with st.expander("年終獎金級距設定", expanded=False):
            df_bonus = pd.DataFrame(st.session_state.bonus_rules)
            edited_bonus_rules = st.data_editor(
                df_bonus, num_rows="dynamic",
                column_config={"grade": st.column_config.TextColumn("等級名稱", required=True), "min_score": st.column_config.NumberColumn("最低分", min_value=0, max_value=100), "months": st.column_config.NumberColumn("月數", step=0.1), "color": st.column_config.TextColumn("顏色(Hex)", help="#FF0000")},
                key="editor_bonus"
            )
            st.session_state.bonus_rules = edited_bonus_rules.to_dict('records')

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

    with tab2:
        if len(st.session_state.batch_queue) > 0:
            df_export = pd.DataFrame(st.session_state.batch_queue)
            st.dataframe(df_export, hide_index=True)
            csv = df_export.to_csv(index=False).encode('utf-8-sig')
            
            # 本機 CSV 下載
            st.download_button("📥 下載 Excel/CSV 檔", data=csv, file_name=f"KPI_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="secondary", use_container_width=True)
            
            # 雲端 Google Sheets 同步
            st.markdown("---")
            st.markdown("##### ☁️ 雲端資料庫 (Google Sheets)")
            if not HAS_GSHEETS:
                st.warning("⚠️ 請先在 `requirements.txt` 加入 `st-gsheets-connection` 才能啟用雲端功能。")
            else:
                if st.button("🚀 批次上傳至 Google Sheets", type="primary", use_container_width=True):
                    try:
                        # 這裡預留實際連線的程式碼
                        # conn = st.connection("gsheets", type=GSheetsConnection)
                        # existing_data = conn.read(worksheet="評核紀錄", usecols=list(range(len(df_export.columns))))
                        # updated_data = pd.concat([existing_data, df_export], ignore_index=True)
                        # conn.update(worksheet="評核紀錄", data=updated_data)
                        st.success("✅ 介面已準備就緒！(待設定 Google 金鑰後即可真實寫入)")
                    except Exception as e:
                        st.error(f"連線失敗，請檢查 Secrets 金鑰設定：{e}")

            st.markdown("---")
            if st.button("🗑️ 清空暫存清單", use_container_width=True):
                st.session_state.batch_queue = []
                st.rerun()
        else:
            st.info("尚無資料加入清單")

# --- 7. 系統資訊 (Footer) ---
with st.expander("ℹ️ 系統資訊 (System Info)", expanded=False):
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 13px;">
        <p><b>版本歷程</b></p>
        <ul style="text-align: left; display: inline-block;">
            <li>v29.0: 內建法遵紅線 Tooltip、準備 Google Sheets 雲端連動。</li>
            <li>v28.0: 導入 OKR 評分架構，內建全職務法遵預設值。</li>
        </ul>
        <br>
        <p>© 2026 馬尼通訊總管理處考核系統</p>
    </div>
    """, unsafe_allow_html=True)
