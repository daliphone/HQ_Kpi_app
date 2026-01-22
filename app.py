import streamlit as st
import pandas as pd
from datetime import datetime
import io

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
    /* 區塊標題 */
    .header-a { background-color: #E3F2FD; padding: 10px; border-radius: 5px; color: #1565C0; font-weight: bold; margin-bottom: 5px; border: 1px solid #BBDEFB; }
    .header-b { background-color: #E8F5E9; padding: 10px; border-radius: 5px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; border: 1px solid #C8E6C9; }
    .header-c { background-color: #FFF3E0; padding: 10px; border-radius: 5px; color: #E65100; font-weight: bold; margin-bottom: 5px; border: 1px solid #FFE0B2; }
    .header-mid-a { background-color: #673AB7; padding: 8px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
    .header-mid-b { background-color: #00897B; padding: 8px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
    
    /* 獎金區塊 */
    .bonus-box { background-color: #FFF8E1; padding: 15px; border-radius: 10px; border: 2px solid #FBC02D; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    /* 分數結果 */
    .result-box { background-color: #FAFAFA; padding: 10px; border-radius: 5px; color: #333; font-size: 22px; font-weight: bold; text-align: center; border: 1px solid #ddd; margin-top: 10px; }
    .grade-badge { font-size: 20px; font-weight: bold; padding: 5px 15px; border-radius: 20px; color: white; display: inline-block; margin: 10px 0;}
    
    /* Footer */
    .footer { text-align: center; color: #888; font-size: 12px; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化資料 ---
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
    # 定義通用模板 (修正資料結構為 dict，解決 TypeError)
    GENERAL_TEMPLATE = {
        "section_weights": [0.50, 0.30, 0.20],
        "basic": [
            {"item": "KPI_1", "weight": 0.25},
            {"item": "KPI_2", "weight": 0.25},
            {"item": "KPI_3", "weight": 0.25},
            {"item": "KPI_4", "weight": 0.25}
        ],
        "excellent": [
            {"item": "執行力", "weight": 0.33},
            {"item": "自我學習", "weight": 0.33},
            {"item": "個人優點與貢獻", "weight": 0.34}
        ],
        "threshold": 80,
        "text_a": [{"title": "本月職務重點", "content": "請輸入內容..."}], # 修正為 dict
        "text_b": [{"title": "工作品質", "content": "請輸入內容..."}]      # 修正為 dict
    }

    st.session_state.config_data = {
        "電商": {
            "section_weights": [0.50, 0.30, 0.20],
            "basic": [
                {"item": "訂單處理正確率", "weight": 0.30},
                {"item": "上架準確率", "weight": 0.30},
                {"item": "活動提案數", "weight": 0.20},
                {"item": "平台廣告效益", "weight": 0.20}
            ],
            "excellent": [
                {"item": "執行力", "weight": 0.33},
                {"item": "自我學習", "weight": 0.33},
                {"item": "個人優點與貢獻", "weight": 0.34}
            ],
            "threshold": 80,
            "text_a": [
                {"title": "商品上架效率", "content": "1.新品通知上架\n2.平台上架"},
                {"title": "訂單處理正確率", "content": "1.每月錯誤率≦3%"},
                {"title": "聊聊處理時效", "content": "1.平均處理時間 ≦24hr\n2.回覆正確性≦90%"},
                {"title": "成效追蹤與分析", "content": ""},
                {"title": "促銷活動配合度", "content": "1.上檔準時率、促銷活動回報率"}
            ],
            "text_b": [
                {"title": "跨部門協作", "content": ""},
                {"title": "學習與改善能力", "content": "1.曝光成長、轉換率提升率（月成長）"},
                {"title": "環境", "content": ""}
            ]
        },
        "自媒體": {
            "section_weights": [0.50, 0.30, 0.20],
            "basic": [
                {"item": "曝光成長率", "weight": 0.25},
                {"item": "互動率", "weight": 0.25},
                {"item": "導流貢獻", "weight": 0.25},
                {"item": "內容品質", "weight": 0.25}
            ],
            "excellent": [
                {"item": "執行力", "weight": 0.33},
                {"item": "自我學習", "weight": 0.33},
                {"item": "個人優點與貢獻", "weight": 0.34}
            ],
            "threshold": 80,
            "text_a": [
                {"title": "貼文/短影音產出數", "content": "1.文章 12 篇/月，短影音 12 支/月"},
                {"title": "內容其明確性與目的性", "content": "1. 成品內容有其目標..."},
                {"title": "成效追蹤與分析", "content": "每月統計，準時繳交與內容完整性"},
                {"title": "互動率（留言/分享/點讚）", "content": ""}
            ],
            "text_b": [
                {"title": "創意與學習性", "content": "自主學習..."},
                {"title": "跨部門協作", "content": "主動與設計/行銷配合..."},
                {"title": "環境", "content": ""}
            ]
        },
        "社群編輯": {
            "section_weights": [0.50, 0.30, 0.20],
            "basic": [
                {"item": "素材完成率", "weight": 0.30},
                {"item": "設計品質", "weight": 0.30},
                {"item": "文案提案", "weight": 0.20},
                {"item": "品牌一致性", "weight": 0.20}
            ],
            "excellent": [
                {"item": "執行力", "weight": 0.33},
                {"item": "自我學習", "weight": 0.33},
                {"item": "個人優點與貢獻", "weight": 0.34}
            ],
            "threshold": 85,
            "text_a": [
                {"title": "設計完成時效", "content": "1. 任務完成時間..."},
                {"title": "創意與排版多樣性", "content": "1. 提供選擇性及目標性的成品"},
                {"title": "成效追蹤與分析", "content": "1. 平台後台數據整理分析"},
                {"title": "互動率", "content": ""}
            ],
            "text_b": [
                {"title": "創意與學習性", "content": "新工具/新風格的主動學習..."},
                {"title": "跨部門協作", "content": "提供替代方案..."},
                {"title": "環境", "content": ""}
            ]
        }
    }
    # 自動套用通用模板給其他部門 (不顯示 "通用" 選項)
    for d in ["會計", "人資", "行銷"]:
        st.session_state.config_data[d] = GENERAL_TEMPLATE

if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []

if 'calculated_score_data' not in st.session_state:
    st.session_state.calculated_score_data = None

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST = list(st.session_state.config_data.keys())

# --- 4. 核心邏輯 ---
def calculate_dynamic_bonus(score, rules_data):
    sorted_rules = sorted(rules_data, key=lambda x: x['min_score'], reverse=True)
    for rule in sorted_rules:
        if score >= rule['min_score']:
            return rule['grade'], rule['months'], rule['color']
    return "N/A", 0.0, "#000000"

# --- 5. 主標題 ---
st.title("📊 總管理處人員評核系統")

# --- 6. 版面佈局 ---
col_left, col_mid, col_right = st.columns([0.8, 1.5, 0.7], gap="medium")

# ==========================================
# 左欄：1. 人員資料 & 2. 每月職務目標
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
    
    # 取得 Config
    current_config = st.session_state.config_data[input_dept]
    
    st.markdown("### 2. 職務目標參考")
    
    with st.expander("📝 每月職務目標 (點擊展開)", expanded=False):
        st.markdown('<div class="header-mid-a">A. 職務內容與目標</div>', unsafe_allow_html=True)
        for row in current_config['text_a']:
            st.text_area(f"● {row['title']}", value=row['content'], height=80, key=f"txt_a_{row['title']}")

        st.markdown('<div class="header-mid-b">B. 內在品質與工作環境</div>', unsafe_allow_html=True)
        for row in current_config['text_b']:
            st.text_area(f"● {row['title']}", value=row['content'], height=80, key=f"txt_b_{row['title']}")

# ==========================================
# 中欄：3. 評分內容
# ==========================================
with col_mid:
    st.markdown("### 3. 評分內容")
    
    wa, wb, wc = current_config['section_weights']

    with st.form("score_form"):
        # A區
        st.markdown(f'<div class="header-a">A. 職務基本標準 (權重 {int(wa*100)}%)</div>', unsafe_allow_html=True)
        scores_a = []
        cols_a = st.columns(2)
        for i, row in enumerate(current_config['basic']):
            with cols_a[i % 2]:
                val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", min_value=0, max_value=100, value=80, step=5, key=f"a_{i}")
                scores_a.append(val * row['weight'])

        # B區
        st.markdown(f'<div class="header-b">B. 卓越主動表現 (權重 {int(wb*100)}%)</div>', unsafe_allow_html=True)
        scores_b = []
        cols_b = st.columns(2)
        for i, row in enumerate(current_config['excellent']):
            with cols_b[i % 2]:
                val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", min_value=0, max_value=100, value=80, step=5, key=f"b_{i}")
                scores_b.append(val * row['weight'])

        # C區
        st.markdown(f'<div class="header-c">C. 主管綜合評核 (權重 {int(wc*100)}%)</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            mgr_score = st.selectbox("評分 (1-10)", options=range(1, 11), index=7)
        with col_c2:
            mgr_comment = st.text_area("反饋評語", height=38, placeholder="請輸入評語...")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📊 計算總分", use_container_width=True, type="primary")

    # 計算邏輯
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
        st.success(f"計算完成！總分：{final_score:.2f} (請參考右側獎金試算)")

# ==========================================
# 右欄：4. 獎金試算 & 5. 設定匯出
# ==========================================
with col_right:
    # --- 獎金區 ---
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
            
            final_bonus = bonus_base * grade_months * bonus_multi
            
            if bonus_base > 0:
                st.info(f"💵 計算結果：${int(final_bonus):,}")
            else:
                st.caption("請輸入月薪")

            st.markdown("---")
            final_confirm_bonus = st.number_input("最終實發", value=int(final_bonus), step=100, key="calc_final")
            
            if st.button("➕ 加入待匯出清單", type="secondary", use_container_width=True):
                meta = st.session_state.calculated_score_data["meta"]
                text_data = {}
                try:
                    for row in current_config['text_a']:
                        k = f"txt_a_{row['title']}"
                        if k in st.session_state: text_data[f"A_{row['title']}"] = st.session_state[k]
                    for row in current_config['text_b']:
                        k = f"txt_b_{row['title']}"
                        if k in st.session_state: text_data[f"B_{row['title']}"] = st.session_state[k]
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

    # --- 設定與匯出 ---
    st.markdown("### 5. 設定與匯出")
    
    tab1, tab2 = st.tabs(["⚙️ 參數設定", "📥 匯出清單"])

    with tab1:
        st.caption("修改後請按 Enter 套用")
        
        with st.expander("年終獎金級距設定", expanded=False):
            st.caption("設定分數區間與對應月數")
            df_bonus = pd.DataFrame(st.session_state.bonus_rules)
            edited_bonus_rules = st.data_editor(
                df_bonus, 
                num_rows="dynamic",
                column_config={
                    "grade": st.column_config.TextColumn("等級名稱", required=True),
                    "min_score": st.column_config.NumberColumn("最低分", min_value=0, max_value=100),
                    "months": st.column_config.NumberColumn("月數", step=0.1),
                    "color": st.column_config.TextColumn("顏色(Hex)", help="#FF0000")
                },
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
            
            st.caption("A區細項")
            df_b = pd.DataFrame(edit_config['basic'])
            ed_b = st.data_editor(df_b, num_rows="dynamic", key="ed_b")
            st.session_state.config_data[edit_dept]['basic'] = ed_b.to_dict('records')
            
            st.caption("B區細項")
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
            st.download_button("📥 下載 CSV", data=csv, file_name=f"KPI_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="primary")
            if st.button("🗑️ 清空"):
                st.session_state.batch_queue = []
                st.rerun()
        else:
            st.info("尚無資料")

# --- 7. 系統資訊 (Footer) ---
with st.expander("ℹ️ 系統資訊 (System Info)", expanded=False):
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 13px;">
        <p><b>版本歷程</b></p>
        <ul style="text-align: left; display: inline-block;">
            <li>v26.1: 修復通用部門設定 Bug，優化資料結構。</li>
            <li>v26.0: 版面重心調整，職務目標移至左欄，評分置中。</li>
            <li>v25.1: 修復舊版 Streamlit 相容性問題。</li>
        </ul>
        <br><br>
        <p>© 2026 馬尼通訊總管理處考核系統</p>
    </div>
    """, unsafe_allow_html=True)
