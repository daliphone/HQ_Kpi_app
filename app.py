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
    /* 區塊標題樣式 */
    .header-a { background-color: #E3F2FD; padding: 10px; border-radius: 5px; color: #1565C0; font-weight: bold; margin-bottom: 5px; border: 1px solid #BBDEFB; }
    .header-b { background-color: #E8F5E9; padding: 10px; border-radius: 5px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; border: 1px solid #C8E6C9; }
    .header-c { background-color: #FFF3E0; padding: 10px; border-radius: 5px; color: #E65100; font-weight: bold; margin-bottom: 5px; border: 1px solid #FFE0B2; }
    
    /* 中欄標題 */
    .header-mid-a { background-color: #5E35B1; padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 5px; }
    .header-mid-b { background-color: #00695C; padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 5px; }
    
    /* 結果顯示 */
    .result-box { background-color: #FAFAFA; padding: 15px; border-radius: 5px; color: #333; font-size: 20px; font-weight: bold; text-align: center; border: 1px solid #ddd; margin-bottom: 10px; }
    .grade-badge { font-size: 18px; font-weight: bold; padding: 5px 12px; border-radius: 15px; color: white; display: inline-block; margin-bottom: 5px;}
    
    /* Footer */
    .footer { text-align: center; color: #888; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化資料 (包含預設獎金級距) ---
if 'bonus_rules' not in st.session_state:
    # 預設級距邏輯 (可被修改)
    st.session_state.bonus_rules = [
        {"grade": "S (特優)", "min_score": 90, "months": 1.5, "color": "#D32F2F"},
        {"grade": "A (優良)", "min_score": 80, "months": 1.0, "color": "#1976D2"},
        {"grade": "B+ (甲上)", "min_score": 75, "months": 0.8, "color": "#2E7D32"},
        {"grade": "B- (甲)", "min_score": 70, "months": 0.6, "color": "#388E3C"},
        {"grade": "C (待改善)", "min_score": 60, "months": 0.5, "color": "#FBC02D"},
        {"grade": "D (不合格)", "min_score": 0, "months": 0.0, "color": "#616161"},
    ]

if 'config_data' not in st.session_state:
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
        },
        "通用": {
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
            "text_a": [("本月職務重點", "請輸入內容...")],
            "text_b": [("工作品質", "請輸入內容...")]
        }
    }

for d in ["會計", "人資", "行銷"]:
    if d not in st.session_state.config_data:
        st.session_state.config_data[d] = st.session_state.config_data["通用"]

if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []

# 用來暫存「已計算但未加入清單」的評分結果
if 'calculated_score_data' not in st.session_state:
    st.session_state.calculated_score_data = None

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST = list(st.session_state.config_data.keys())

# --- 4. 核心邏輯：動態獎金計算 ---
def calculate_dynamic_bonus(score, rules_data):
    """
    根據 rules_data (List of Dict) 動態計算獎金
    """
    # 1. 將規則按分數由高到低排序，確保邏輯正確
    # 假設使用者輸入順序不一，我們必須先排序
    sorted_rules = sorted(rules_data, key=lambda x: x['min_score'], reverse=True)
    
    # 2. 比對分數
    for rule in sorted_rules:
        if score >= rule['min_score']:
            return rule['grade'], rule['months'], rule['color']
    
    # 若低於所有設定 (理論上最後一個應為0分)，回傳預設
    return "N/A", 0.0, "#000000"

# --- 5. 主標題 ---
st.title("📊 總管理處人員評核系統")

# --- 6. 版面佈局 (三欄式) ---
col_left, col_mid, col_right = st.columns([1.2, 1, 0.8], gap="medium")

# ==========================================
# 左欄：評分與計算
# ==========================================
with col_left:
    st.markdown("### 1. 評分與計算")
    
    # 1.1 人員資料 Form
    with st.container(border=True):
        st.markdown("#### 👤 人員資料")
        c1, c2 = st.columns(2)
        with c1:
            input_supervisor = st.text_input("主管", value="")
            input_name = st.text_input("姓名", value="")
            input_dept = st.selectbox("部門", options=DEPT_LIST, index=0)
        with c2:
            input_date = st.date_input("日期", value=datetime.now())
            input_level = st.selectbox("職等", options=JOB_LEVELS, index=1)
    
    current_config = st.session_state.config_data[input_dept]
    wa, wb, wc = current_config['section_weights']

    # 1.2 評分表單
    with st.form("score_form"):
        st.markdown(f'<div class="header-a">A. 職務基本標準 (權重 {int(wa*100)}%)</div>', unsafe_allow_html=True)
        scores_a = []
        cols_a = st.columns(2)
        for i, row in enumerate(current_config['basic']):
            with cols_a[i % 2]:
                val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", min_value=0, max_value=100, value=80, step=5, key=f"a_{i}")
                scores_a.append(val * row['weight'])

        st.markdown(f'<div class="header-b">B. 卓越主動表現 (權重 {int(wb*100)}%)</div>', unsafe_allow_html=True)
        scores_b = []
        cols_b = st.columns(2)
        for i, row in enumerate(current_config['excellent']):
            with cols_b[i % 2]:
                val = st.number_input(f"{row['item']} ({int(row['weight']*100)}%)", min_value=0, max_value=100, value=80, step=5, key=f"b_{i}")
                scores_b.append(val * row['weight'])

        st.markdown(f'<div class="header-c">C. 主管綜合評核 (權重 {int(wc*100)}%)</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            mgr_score = st.selectbox("評分 (1-10)", options=range(1, 11), index=7)
        with col_c2:
            mgr_comment = st.text_area("反饋評語", height=38, placeholder="請輸入評語...")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📊 計算評核總分", use_container_width=True, type="primary")

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

    # 1.4 獨立區塊：年終獎金試算 (UI 更新：移除淡黃色方塊，改用原生 Container)
    st.markdown("<br>", unsafe_allow_html=True) # 間距
    
    # 使用 container 包裹，加上標題
    with st.container(border=True):
        st.markdown("#### 💰 年終獎金試算 (級距制)")
        
        # 顯示簡易規則提示
        rules_hint = " | ".join([f"{r['grade']}: {r['months']}月" for r in sorted(st.session_state.bonus_rules, key=lambda x:x['min_score'], reverse=True)[:4]])
        st.caption(f"目前規則：{rules_hint} ... (詳見設定)")

        if st.session_state.calculated_score_data:
            current_score = st.session_state.calculated_score_data["score"]
            
            # 顯示總分
            st.markdown(f'<div class="result-box">目前總分：{current_score:.2f}</div>', unsafe_allow_html=True)
            
            # 使用動態規則計算
            grade_text, grade_months, grade_color = calculate_dynamic_bonus(current_score, st.session_state.bonus_rules)
            
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.markdown(f"**評定等級**")
                st.markdown(f'<div style="background-color:{grade_color};" class="grade-badge">{grade_text}</div>', unsafe_allow_html=True)
            with c_res2:
                st.metric("建議核定月數", f"{grade_months} 個月")

            st.divider()
            
            # 試算輸入
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                bonus_base = st.number_input("月薪 (Base)", value=0, step=1000, help="輸入員工月薪以計算金額")
            with col_b2:
                bonus_multi = st.number_input("額外倍率", value=1.0, step=0.1, help="特殊加權使用")

            final_bonus = bonus_base * grade_months * bonus_multi
            
            st.info(f"💵 計算結果：${int(final_bonus):,}")
            
            # 確認加入
            st.markdown("##### 確認並存檔")
            final_confirm_bonus = st.number_input("最終實發金額 (可手動修正)", value=int(final_bonus), step=100)
            
            if st.button("➕ 加入待匯出清單", use_container_width=True):
                meta = st.session_state.calculated_score_data["meta"]
                
                text_data = {}
                try:
                    for row in current_config['text_a']:
                        key = f"txt_a_{row['title']}"
                        if key in st.session_state: text_data[f"A_{row['title']}"] = st.session_state[key]
                    for row in current_config['text_b']:
                        key = f"txt_b_{row['title']}"
                        if key in st.session_state: text_data[f"B_{row['title']}"] = st.session_state[key]
                except: pass

                full_data = {
                    "評分日期": meta["date"], "評分主管": meta["supervisor"], "受評姓名": meta["name"],
                    "職等": meta["level"], "部門": meta["dept"], "總分": f"{current_score:.2f}",
                    "評等": grade_text, "核定月數": str(grade_months), "實得獎金": final_confirm_bonus,
                    "主管評語": meta["comment"],
                    **text_data
                }
                
                st.session_state.batch_queue.append(full_data)
                st.toast(f"✅ 已加入 {meta['name']} 的資料！")
                
        else:
            st.warning("👉 請先填寫上方評分並點擊「計算評核總分」")

# ==========================================
# 中欄：職務目標
# ==========================================
with col_mid:
    st.markdown("### 2. 每月職務目標")
    
    st.markdown('<div class="header-mid-a">A. 職務內容與目標</div>', unsafe_allow_html=True)
    for row in current_config['text_a']:
        st.text_area(f"● {row['title']}", value=row['content'], height=100, key=f"txt_a_{row['title']}")

    st.markdown('<div class="header-mid-b">B. 內在品質與工作環境</div>', unsafe_allow_html=True)
    for row in current_config['text_b']:
        st.text_area(f"● {row['title']}", value=row['content'], height=100, key=f"txt_b_{row['title']}")

# ==========================================
# 右欄：參數設定與匯出
# ==========================================
with col_right:
    st.markdown("### 3. 設定與匯出")
    
    tab1, tab2 = st.tabs(["⚙️ 參數設定", "📥 匯出清單"])

    with tab1:
        st.info("💡 修改表格後請按 Enter 套用")
        edit_dept = st.selectbox("選擇要編輯的部門", options=DEPT_LIST)
        edit_config = st.session_state.config_data[edit_dept]

        with st.expander("1. 權重設定 (ABC區)", expanded=False):
            col_w1, col_w2, col_w3 = st.columns(3)
            new_wa = col_w1.number_input("A區權重", value=edit_config['section_weights'][0], step=0.05, key="w_a")
            new_wb = col_w2.number_input("B區權重", value=edit_config['section_weights'][1], step=0.05, key="w_b")
            new_wc = col_w3.number_input("C區權重", value=edit_config['section_weights'][2], step=0.05, key="w_c")
            st.session_state.config_data[edit_dept]['section_weights'] = [new_wa, new_wb, new_wc]

        with st.expander("2. 評分細項設定", expanded=False):
            st.caption("A區：職務基本標準")
            df_basic = pd.DataFrame(edit_config['basic'])
            edited_basic = st.data_editor(df_basic, num_rows="dynamic", key="editor_basic")
            st.session_state.config_data[edit_dept]['basic'] = edited_basic.to_dict('records')

            st.caption("B區：卓越主動表現")
            df_excellent = pd.DataFrame(edit_config['excellent'])
            edited_excellent = st.data_editor(df_excellent, num_rows="dynamic", key="editor_excellent")
            st.session_state.config_data[edit_dept]['excellent'] = edited_excellent.to_dict('records')

        with st.expander("3. 職務目標預設值", expanded=False):
            st.caption("A區文字模板")
            df_text_a = pd.DataFrame(edit_config['text_a'])
            edited_text_a = st.data_editor(df_text_a, num_rows="dynamic", key="editor_text_a")
            st.session_state.config_data[edit_dept]['text_a'] = edited_text_a.to_dict('records')

            st.caption("B區文字模板")
            df_text_b = pd.DataFrame(edit_config['text_b'])
            edited_text_b = st.data_editor(df_text_b, num_rows="dynamic", key="editor_text_b")
            st.session_state.config_data[edit_dept]['text_b'] = edited_text_b.to_dict('records')
        
        # 新增：獎金級距設定
        with st.expander("4. 年終獎金級距設定", expanded=True):
            st.caption("設定分數區間與對應月數 (請按分數高低排列以利閱讀)")
            # 將目前的規則轉為 DF 供編輯
            df_bonus = pd.DataFrame(st.session_state.bonus_rules)
            # 欄位設定：顏色選擇器
            edited_bonus_rules = st.data_editor(
                df_bonus, 
                num_rows="dynamic",
                column_config={
                    "color": st.column_config.ColorPickerColumn("標籤顏色"),
                    "min_score": st.column_config.NumberColumn("最低分數門檻", min_value=0, max_value=100),
                    "months": st.column_config.NumberColumn("核定月數", step=0.1)
                },
                key="editor_bonus"
            )
            # 存回
            st.session_state.bonus_rules = edited_bonus_rules.to_dict('records')

        if st.button("🔄 重整頁面以套用新設定"):
            st.rerun()

    with tab2:
        if len(st.session_state.batch_queue) > 0:
            df_export = pd.DataFrame(st.session_state.batch_queue)
            st.dataframe(df_export, hide_index=True)
            
            csv = df_export.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 下載 CSV 檔案",
                data=csv,
                file_name=f"KPI_Report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
            
            if st.button("🗑️ 清空所有資料", use_container_width=True):
                st.session_state.batch_queue = []
                st.rerun()
        else:
            st.info("📭 目前清單是空的")

# --- 7. 系統資訊 (Footer - 預設閉合) ---
with st.expander("ℹ️ 系統資訊 (System Info)", expanded=False):
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p><b>版本歷程</b></p>
        <ul style="text-align: left; display: inline-block;">
            <li>v24.0: 新增系統資訊區塊、獎金試算區獨立與美化、移除版本標題。</li>
            <li>v23.0: 獎金邏輯升級為精細級距 (B+/B-)。</li>
            <li>v21.0: 網頁版架構重構，支援動態參數設定。</li>
        </ul>
        <br><br>
        <p>© 2026 馬尼通訊總管理處考核系統</p>
    </div>
    """, unsafe_allow_html=True)
