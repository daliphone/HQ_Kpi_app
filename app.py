import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- 1. 頁面設定 (必須在第一行) ---
st.set_page_config(
    page_title="總管理處人員評核系統 (Web版)",
    page_icon="📊",
    layout="wide", # 開啟寬螢幕模式
    initial_sidebar_state="expanded"
)

# --- 2. 資料預設值 (與 v14.0 保持一致) ---
DEFAULT_DATA = {
    "電商": {
        "weights": [0.50, 0.30, 0.20],
        "basic": [("訂單處理正確率", 0.30), ("上架準確率", 0.30), ("活動提案數", 0.20), ("平台廣告效益", 0.20)],
        "excellent": [("執行力", 0.33), ("自我學習", 0.33), ("個人優點與貢獻", 0.34)],
        "threshold": 80,
        "text_a": [
            ("商品上架效率", "1.新品通知上架\n2.平台上架"),
            ("訂單處理正確率", "1.每月錯誤率≦3%"),
            ("聊聊處理時效", "1.平均處理時間 ≦24hr\n2.回覆正確性≦90%"),
            ("成效追蹤與分析", ""),
            ("促銷活動配合度", "1.上檔準時率、促銷活動回報率")
        ],
        "text_b": [
            ("跨部門協作", ""),
            ("學習與改善能力", "1.曝光成長、轉換率提升率（月成長）"),
            ("環境", "")
        ]
    },
    "自媒體": {
        "weights": [0.50, 0.30, 0.20],
        "basic": [("曝光成長率", 0.25), ("互動率", 0.25), ("導流貢獻", 0.25), ("內容品質", 0.25)],
        "excellent": [("執行力", 0.33), ("自我學習", 0.33), ("個人優點與貢獻", 0.34)],
        "threshold": 80,
        "text_a": [
            ("貼文/短影音產出數", "1.文章 12 篇/月，短影音 12 支/月"),
            ("內容其明確性與目的性", "1. 成品內容有其目標..."),
            ("成效追蹤與分析", "每月統計，準時繳交與內容完整性"),
            ("互動率（留言/分享/點讚）", "")
        ],
        "text_b": [
            ("創意與學習性", "自主學習..."),
            ("跨部門協作", "主動與設計/行銷配合..."),
            ("環境", "")
        ]
    },
    "社群編輯": {
        "weights": [0.50, 0.30, 0.20],
        "basic": [("素材完成率", 0.30), ("設計品質", 0.30), ("文案提案", 0.20), ("品牌一致性", 0.20)],
        "excellent": [("執行力", 0.33), ("自我學習", 0.33), ("個人優點與貢獻", 0.34)],
        "threshold": 85,
        "text_a": [
            ("設計完成時效", "1. 任務完成時間..."),
            ("創意與排版多樣性", "1. 提供選擇性及目標性的成品"),
            ("成效追蹤與分析", "1. 平台後台數據整理分析"),
            ("互動率", "")
        ],
        "text_b": [
            ("創意與學習性", "新工具/新風格的主動學習..."),
            ("跨部門協作", "提供替代方案..."),
            ("環境", "")
        ]
    },
    "通用": {
        "weights": [0.50, 0.30, 0.20],
        "basic": [("KPI_1", 0.25), ("KPI_2", 0.25), ("KPI_3", 0.25), ("KPI_4", 0.25)],
        "excellent": [("執行力", 0.33), ("自我學習", 0.33), ("個人優點與貢獻", 0.34)],
        "threshold": 80,
        "text_a": [("本月職務重點", "請輸入內容...")],
        "text_b": [("工作品質", "請輸入內容...")]
    }
}

# 補齊其他部門
for d in ["會計", "人資", "行銷"]:
    if d not in DEFAULT_DATA:
        DEFAULT_DATA[d] = DEFAULT_DATA["通用"]

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]

# --- 3. 初始化 Session State (類似全域變數，用於儲存清單) ---
if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = []
if 'current_dept' not in st.session_state:
    st.session_state.current_dept = "電商"

# --- 4. CSS 美化 (模擬之前的配色) ---
st.markdown("""
<style>
    .big-font { font-size:18px !important; font-weight: bold; }
    .header-a { background-color: #E3F2FD; padding: 10px; border-radius: 5px; color: #1565C0; font-weight: bold; margin-bottom: 10px; }
    .header-b { background-color: #E8F5E9; padding: 10px; border-radius: 5px; color: #2E7D32; font-weight: bold; margin-bottom: 10px; }
    .header-c { background-color: #FFF3E0; padding: 10px; border-radius: 5px; color: #E65100; font-weight: bold; margin-bottom: 10px; }
    .header-mid-a { background-color: #5E35B1; padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 10px; }
    .header-mid-b { background-color: #00695C; padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 10px; }
    .bonus-box { background-color: #FFF8E1; padding: 15px; border-radius: 10px; border: 1px solid #FFD54F; }
    .result-box { background-color: #FFEBEE; padding: 10px; border-radius: 5px; color: #C62828; font-size: 20px; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 5. 主標題 ---
st.title("📊 總管理處人員評核系統 v19 (Web版)")

# --- 6. 版面佈局 (三欄式) ---
# 左欄(評分) : 中欄(目標) : 右欄(設定)
col_left, col_mid, col_right = st.columns([1.2, 1, 0.8], gap="medium")

# ==========================================
# 左欄：評分與計算
# ==========================================
with col_left:
    st.markdown("### 1. 評分與計算")
    
    # 1.1 人員資料 Form
    with st.expander("👤 人員資料", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            input_supervisor = st.text_input("主管", value="")
            input_name = st.text_input("姓名", value="")
            # 部門選擇 (連動)
            input_dept = st.selectbox("部門", options=list(DEFAULT_DATA.keys()), index=0)
        with c2:
            input_date = st.date_input("日期", value=datetime.now())
            input_level = st.selectbox("職等", options=JOB_LEVELS, index=1)
    
    # 取得目前部門設定
    config = DEFAULT_DATA[input_dept]
    wa, wb, wc = config['weights']

    # 1.2 評分表單
    # 使用 Form 避免每輸入一個字就重新整理頁面
    with st.form("score_form"):
        # A區
        st.markdown(f'<div class="header-a">A. 職務基本標準 ({int(wa*100)}%)</div>', unsafe_allow_html=True)
        scores_a = []
        cols_a = st.columns(2) # 雙排顯示
        for i, (item, weight) in enumerate(config['basic']):
            with cols_a[i % 2]:
                val = st.number_input(f"{item} ({int(weight*100)}%)", min_value=0, max_value=100, value=80, key=f"a_{i}")
                scores_a.append(val * weight)

        # B區
        st.markdown(f'<div class="header-b">B. 卓越主動表現 ({int(wb*100)}%)</div>', unsafe_allow_html=True)
        scores_b = []
        cols_b = st.columns(2)
        for i, (item, weight) in enumerate(config['excellent']):
            with cols_b[i % 2]:
                val = st.number_input(f"{item} ({int(weight*100)}%)", min_value=0, max_value=100, value=80, key=f"b_{i}")
                scores_b.append(val * weight)

        # C區
        st.markdown(f'<div class="header-c">C. 主管綜合評核 ({int(wc*100)}%)</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            mgr_score = st.selectbox("評分 (1-10)", options=range(1, 11), index=7)
        with col_c2:
            mgr_comment = st.text_area("反饋評語", height=38) # 高度配合 selectbox

        st.markdown("---")
        
        # 獎金試算區
        st.markdown('<div class="bonus-box">💰 <b>獎金試算</b></div>', unsafe_allow_html=True)
        bc1, bc2 = st.columns(2)
        with bc1:
            bonus_base = st.number_input("基數 (Max)", value=0, step=1000)
        with bc2:
            bonus_multi = st.number_input("倍率", value=1.0, step=0.1)
        
        bonus_formula = st.text_input("公式", value="base * (score / 100) * multiplier", disabled=True)

        # 提交按鈕
        submitted = st.form_submit_button("開始計算 (Calculate)", use_container_width=True, type="primary")

    # 計算邏輯 (Form 提交後執行)
    if submitted:
        total_a = sum(scores_a)
        total_b = sum(scores_b)
        total_c = mgr_score * 10 
        final_score = (total_a * wa) + (total_b * wb) + (total_c * wc)
        
        # 獎金計算
        try:
            base = bonus_base
            score = final_score
            multiplier = bonus_multi
            final_bonus = eval(bonus_formula)
        except:
            final_bonus = 0

        # 顯示結果
        st.markdown(f'<div class="result-box">總分：{final_score:.2f}</div>', unsafe_allow_html=True)
        
        # 儲存計算結果到 Session State 以便稍後加入清單
        st.session_state.temp_result = {
            "name": input_name,
            "dept": input_dept,
            "level": input_level,
            "supervisor": input_supervisor,
            "date": str(input_date),
            "score": f"{final_score:.2f}",
            "bonus": int(final_bonus),
            "comment": mgr_comment,
            # 這裡簡單儲存，實務上可儲存更多細節
        }
        st.success(f"計算完成！實得獎金: ${int(final_bonus):,}")

    # 加入清單按鈕 (獨立於 Form 之外)
    if 'temp_result' in st.session_state:
        if st.button("➕ 加入待匯出清單", use_container_width=True):
            # 抓取中欄的文字輸入 (需要透過 key 取得)
            # 注意：Streamlit 的 key 值在 rerun 後可用
            texts = {}
            # 這裡簡化處理，實際要抓取中欄所有 key 比較複雜，
            # 網頁版建議將文字輸入區也放入 form 或 session_state 管理
            
            st.session_state.batch_queue.append(st.session_state.temp_result)
            st.toast(f"已加入：{st.session_state.temp_result['name']}")
            del st.session_state.temp_result # 清除暫存

# ==========================================
# 中欄：職務目標 (文字輸入)
# ==========================================
with col_mid:
    st.markdown("### 2. 每月職務目標")
    
    # 根據左欄選擇的部門，載入對應文字
    current_config = DEFAULT_DATA[input_dept]

    st.markdown('<div class="header-mid-a">A. 職務內容與目標</div>', unsafe_allow_html=True)
    for title, default_val in current_config['text_a']:
        st.text_area(f"● {title}", value=default_val, height=100, key=f"txt_a_{title}")

    st.markdown('<div class="header-mid-b">B. 內在品質與工作環境</div>', unsafe_allow_html=True)
    for title, default_val in current_config['text_b']:
        st.text_area(f"● {title}", value=default_val, height=100, key=f"txt_b_{title}")

# ==========================================
# 右欄：設定與匯出
# ==========================================
with col_right:
    st.markdown("### 3. 待匯出清單")
    
    if len(st.session_state.batch_queue) > 0:
        df = pd.DataFrame(st.session_state.batch_queue)
        st.dataframe(df, hide_index=True)
        
        # 匯出 CSV
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📥 下載 CSV 報表",
            data=csv_buffer,
            file_name=f"績效評核_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
        if st.button("🗑️ 清空清單", use_container_width=True):
            st.session_state.batch_queue = []
            st.rerun()
    else:
        st.info("目前清單為空")

    with st.expander("⚙️ 參數設定 (檢視)"):
        st.write("各區權重:", config['weights'])
        st.write("及格標準:", config['threshold'])
        st.caption("網頁版暫不支援線上修改設定結構，請聯絡管理員修改程式碼。")