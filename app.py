import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="總管理處人員評核系統 v21 (Web旗艦版)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed" # 隱藏預設 sidebar 讓畫面更寬
)

# --- 2. CSS 美化 ---
st.markdown("""
<style>
    .header-a { background-color: #E3F2FD; padding: 10px; border-radius: 5px; color: #1565C0; font-weight: bold; margin-bottom: 5px; border: 1px solid #BBDEFB; }
    .header-b { background-color: #E8F5E9; padding: 10px; border-radius: 5px; color: #2E7D32; font-weight: bold; margin-bottom: 5px; border: 1px solid #C8E6C9; }
    .header-c { background-color: #FFF3E0; padding: 10px; border-radius: 5px; color: #E65100; font-weight: bold; margin-bottom: 5px; border: 1px solid #FFE0B2; }
    .header-mid-a { background-color: #5E35B1; padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 5px; }
    .header-mid-b { background-color: #00695C; padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 5px; }
    .bonus-box { background-color: #FFF8E1; padding: 15px; border-radius: 10px; border: 2px solid #F57F17; margin-top: 20px; }
    .result-box { background-color: #FFEBEE; padding: 15px; border-radius: 5px; color: #C62828; font-size: 24px; font-weight: bold; text-align: center; border: 1px solid #FFCDD2; }
    /* 調整 Tab 字體 */
    button[data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化資料 (如果 Session State 是空的，載入預設值) ---
if 'config_data' not in st.session_state:
    # 這裡放原本的 DEFAULT_CONFIG
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

if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []

# --- 4. 輔助變數 ---
JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST = list(st.session_state.config_data.keys())

# --- 5. 主標題 ---
st.title("📊 總管理處人員評核系統 v21.0")

# --- 6. 版面佈局 (三欄式) ---
# 左(1.2) | 中(1.0) | 右(0.8)
col_left, col_mid, col_right = st.columns([1.2, 1, 0.8], gap="medium")

# ==========================================
# 左欄：評分與計算 (主操作區)
# ==========================================
with col_left:
    st.markdown("### 1. 評分與計算")
    
    # 1.1 人員資料 Form (使用 container 讓它看起來像個區塊)
    with st.container(border=True):
        st.markdown("#### 👤 人員資料")
        c1, c2 = st.columns(2)
        with c1:
            input_supervisor = st.text_input("主管", value="")
            input_name = st.text_input("姓名", value="")
            # 部門選擇 (這裡是「使用」哪個部門的設定)
            input_dept = st.selectbox("部門", options=DEPT_LIST, index=0)
        with c2:
            input_date = st.date_input("日期", value=datetime.now())
            input_level = st.selectbox("職等", options=JOB_LEVELS, index=1)
    
    # 取得目前部門的 Config (從 session_state 拿，這樣右邊改了這裡會變)
    current_config = st.session_state.config_data[input_dept]
    wa, wb, wc = current_config['section_weights']

    # 1.2 評分表單
    with st.form("score_form"):
        # A區
        st.markdown(f'<div class="header-a">A. 職務基本標準 (權重 {int(wa*100)}%)</div>', unsafe_allow_html=True)
        scores_a = []
        # 動態生成 A 區輸入框
        cols_a = st.columns(2)
        for i, row in enumerate(current_config['basic']):
            with cols_a[i % 2]:
                val = st.number_input(
                    f"{row['item']} ({int(row['weight']*100)}%)", 
                    min_value=0, max_value=100, value=80, step=5,
                    key=f"a_in_{i}"
                )
                scores_a.append(val * row['weight'])

        # B區
        st.markdown(f'<div class="header-b">B. 卓越主動表現 (權重 {int(wb*100)}%)</div>', unsafe_allow_html=True)
        scores_b = []
        cols_b = st.columns(2)
        for i, row in enumerate(current_config['excellent']):
            with cols_b[i % 2]:
                val = st.number_input(
                    f"{row['item']} ({int(row['weight']*100)}%)", 
                    min_value=0, max_value=100, value=80, step=5,
                    key=f"b_in_{i}"
                )
                scores_b.append(val * row['weight'])

        # C區
        st.markdown(f'<div class="header-c">C. 主管綜合評核 (權重 {int(wc*100)}%)</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            mgr_score = st.selectbox("評分 (1-10)", options=range(1, 11), index=7)
        with col_c2:
            mgr_comment = st.text_area("反饋評語", height=38, placeholder="請輸入評語...")

        # 獎金區 (黃色區塊)
        st.markdown('<div class="bonus-box">', unsafe_allow_html=True)
        st.markdown("#### 💰 獎金試算中心")
        
        # 獎金公式與變數
        col_b_1, col_b_2, col_b_3 = st.columns([2, 1, 1])
        with col_b_1:
            bonus_formula = st.text_input("計算公式", value="base * (score / 100) * multiplier")
        with col_b_2:
            bonus_base = st.number_input("基數 (base)", value=0, step=1000)
        with col_b_3:
            bonus_multi = st.number_input("倍率 (multi)", value=1.0, step=0.1)
        
        st.markdown('</div>', unsafe_allow_html=True) # End bonus-box

        # 提交按鈕
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 計算總分與獎金", use_container_width=True, type="primary")

    # 計算邏輯
    if submitted:
        total_a = sum(scores_a)
        total_b = sum(scores_b)
        total_c = mgr_score * 10 
        final_score = (total_a * wa) + (total_b * wb) + (total_c * wc)
        
        # 獎金計算 (Eval)
        try:
            safe_env = {"base": bonus_base, "score": final_score, "multiplier": bonus_multi}
            final_bonus = eval(bonus_formula, {"__builtins__": None}, safe_env)
        except:
            final_bonus = 0
            st.error("公式錯誤")

        # 顯示結果
        st.markdown(f'<div class="result-box">總分：{final_score:.2f}</div>', unsafe_allow_html=True)
        st.info(f"💵 建議實得獎金：${int(final_bonus):,}")
        
        # 暫存
        st.session_state.temp_result = {
            "name": input_name,
            "dept": input_dept,
            "score": f"{final_score:.2f}",
            "bonus": int(final_bonus),
            "supervisor": input_supervisor,
            "date": str(input_date),
            "level": input_level,
            "comment": mgr_comment
        }

    # 加入清單 (獨立按鈕)
    if 'temp_result' in st.session_state:
        # 讓使用者確認或修改最終獎金
        final_bonus_confirm = st.number_input("確認實發獎金", value=st.session_state.temp_result['bonus'], step=100)
        
        if st.button("➕ 加入待匯出清單", use_container_width=True):
            # 更新獎金
            st.session_state.temp_result['bonus'] = final_bonus_confirm
            
            # 抓取中欄文字 (需遍歷 key)
            # 這裡做一個簡單的抓取，抓取目前設定的欄位
            text_data = {}
            for row in current_config['text_a']:
                key = f"txt_a_{row['title']}"
                if key in st.session_state:
                    text_data[f"A_{row['title']}"] = st.session_state[key]
            
            for row in current_config['text_b']:
                key = f"txt_b_{row['title']}"
                if key in st.session_state:
                    text_data[f"B_{row['title']}"] = st.session_state[key]

            # 合併數據
            full_data = {**st.session_state.temp_result, **text_data}
            st.session_state.batch_queue.append(full_data)
            
            st.success(f"已加入：{st.session_state.temp_result['name']}")
            del st.session_state.temp_result # 清除暫存

# ==========================================
# 中欄：職務目標 (文字輸入)
# ==========================================
with col_mid:
    st.markdown("### 2. 每月職務目標")
    
    # 載入設定中的文字模板
    # 注意：這裡使用 key 是為了讓 Streamlit 記住輸入內容
    # 如果右欄修改了預設值，下次 rerun 時這裡的 label/value 會變
    
    st.markdown('<div class="header-mid-a">A. 職務內容與目標</div>', unsafe_allow_html=True)
    for row in current_config['text_a']:
        st.text_area(f"● {row['title']}", value=row['content'], height=100, key=f"txt_a_{row['title']}")

    st.markdown('<div class="header-mid-b">B. 內在品質與工作環境</div>', unsafe_allow_html=True)
    for row in current_config['text_b']:
        st.text_area(f"● {row['title']}", value=row['content'], height=100, key=f"txt_b_{row['title']}")

# ==========================================
# 右欄：參數設定與匯出 (核心更新)
# ==========================================
with col_right:
    st.markdown("### 3. 設定與匯出")
    
    tab1, tab2 = st.tabs(["⚙️ 參數設定", "📥 匯出清單"])

    # --- Tab 1: 參數設定 (可編輯) ---
    with tab1:
        st.info("💡 修改後請按 Enter 或點擊表格外以套用")
        
        # 1. 選擇要編輯的部門
        edit_dept = st.selectbox("選擇要編輯的部門設定", options=DEPT_LIST)
        edit_config = st.session_state.config_data[edit_dept]

        with st.expander("1. 權重設定 (ABC區)", expanded=True):
            col_w1, col_w2, col_w3 = st.columns(3)
            new_wa = col_w1.number_input("A區權重", value=edit_config['section_weights'][0], step=0.05, key="w_a")
            new_wb = col_w2.number_input("B區權重", value=edit_config['section_weights'][1], step=0.05, key="w_b")
            new_wc = col_w3.number_input("C區權重", value=edit_config['section_weights'][2], step=0.05, key="w_c")
            
            # 即時更新權重
            st.session_state.config_data[edit_dept]['section_weights'] = [new_wa, new_wb, new_wc]

        with st.expander("2. 評分細項 (表格編輯)", expanded=True):
            st.caption("A區：職務基本標準")
            # 轉換為 DataFrame 供編輯
            df_basic = pd.DataFrame(edit_config['basic'])
            edited_basic = st.data_editor(df_basic, num_rows="dynamic", key="editor_basic")
            # 存回 Session State (轉換回 list of dicts)
            st.session_state.config_data[edit_dept]['basic'] = edited_basic.to_dict('records')

            st.caption("B區：卓越主動表現")
            df_excellent = pd.DataFrame(edit_config['excellent'])
            edited_excellent = st.data_editor(df_excellent, num_rows="dynamic", key="editor_excellent")
            st.session_state.config_data[edit_dept]['excellent'] = edited_excellent.to_dict('records')

        with st.expander("3. 職務目標預設值", expanded=False):
            st.caption("A區文字模板 (Title/Content)")
            df_text_a = pd.DataFrame(edit_config['text_a'])
            edited_text_a = st.data_editor(df_text_a, num_rows="dynamic", key="editor_text_a")
            st.session_state.config_data[edit_dept]['text_a'] = edited_text_a.to_dict('records')

            st.caption("B區文字模板")
            df_text_b = pd.DataFrame(edit_config['text_b'])
            edited_text_b = st.data_editor(df_text_b, num_rows="dynamic", key="editor_text_b")
            st.session_state.config_data[edit_dept]['text_b'] = edited_text_b.to_dict('records')
            
        if st.button("🔄 重整頁面以套用新設定"):
            st.rerun()

    # --- Tab 2: 匯出清單 ---
    with tab2:
        if len(st.session_state.batch_queue) > 0:
            df_export = pd.DataFrame(st.session_state.batch_queue)
            st.dataframe(df_export, hide_index=True)
            
            # CSV 轉換
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
