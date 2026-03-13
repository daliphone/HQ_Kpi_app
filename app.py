# --- 2. CSS：Pro Max 莫蘭迪現代設計系統 (Morandi Design System) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700;900&family=DM+Mono:wght@400;500&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    :root {
        /* 莫蘭迪溫和中性背景色 */
        --bg-base:       #F2F4F6;
        --bg-surface:    #FFFFFF;
        --bg-elevated:   #FAFBFC;
        --bg-hover:      #EAECEF;
        --border:        #E1E4E8;
        --border-light:  #EDEFF2;
        
        /* 降低對比度的舒適文字色 */
        --text-primary:  #343A40;
        --text-secondary:#5C6370;
        --text-muted:    #8B949E;
        
        /* 莫蘭迪主色調 (低飽和度，久看不累) */
        --accent-blue:   #7A8B99; /* 灰藍色 */
        --accent-teal:   #829D96; /* 灰綠色 */
        --accent-amber:  #BCA87F; /* 燕麥奶黃 */
        --accent-rose:   #B58B8F; /* 灰粉色 */
        --accent-violet: #8C849E; /* 灰紫色 */
    }

    /* ===== 全域字體與背景 ===== */
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', sans-serif;
        font-size: 16px !important;
        background-color: var(--bg-base) !important;
    }
    .stApp { background-color: var(--bg-base) !important; color: var(--text-primary); }

    /* 保護 Icon 不被覆寫 */
    .material-icons, .st-emotion-cache-1bz1hzt svg, [data-testid="collapsedControl"] svg {
        font-family: 'Material Icons' !important;
    }

    /* 隱藏原生多餘元件 */
    .stDeployButton, [data-testid="stMainMenu"] { display: none !important; }
    [data-testid="stHeader"] { background-color: transparent !important; }

    /* ===== 主容器留白 (增加呼吸空間) ===== */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 92%; /* 讓兩側稍微內縮，聚焦視覺 */
    }

    /* ===== 側邊欄：乾淨、無框線、微陰影 ===== */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: none !important;
        box-shadow: 2px 0 20px rgba(0,0,0,0.03) !important;
    }
    section[data-testid="stSidebar"] hr { border-color: var(--border-light) !important; margin: 16px 0; }
    
    /* ===== 側邊欄 Radio 導航 (柔和 Hover 狀態) ===== */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] { 
        background: transparent !important; gap: 8px !important; padding: 0 16px !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child { 
        display: none !important; 
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:last-child {
        color: var(--text-secondary) !important; font-size: 15px !important; font-weight: 600 !important;
        padding: 14px 20px !important; border-radius: 12px !important;
        transition: all 0.2s ease !important; display: block !important; width: 100% !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover > div:last-child { 
        background: var(--bg-hover) !important; color: var(--text-primary) !important; 
        transform: translateX(4px); /* 滑鼠懸停微動效 */
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"][aria-checked="true"] > div:last-child {
        background: var(--text-primary) !important; color: #FFFFFF !important;
        font-weight: 700 !important; box-shadow: 0 4px 12px rgba(52, 58, 64, 0.15) !important;
    }

    /* ===== Logo 區 ===== */
    .sidebar-logo { padding: 36px 20px 24px; text-align: center; }
    .sidebar-logo-icon { font-size: 42px; line-height: 1; filter: grayscale(20%); opacity: 0.9; }
    .sidebar-logo-title { color: var(--text-primary); font-size: 20px; font-weight: 800; letter-spacing: 2px; margin: 16px 0 4px 0; }
    .sidebar-logo-sub { color: var(--text-muted); font-size: 12px; letter-spacing: 1px; }

    /* ===== 原生容器卡片統一風格 (Pro Max 陰影與圓角) ===== */
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 16px !important;
        padding: 28px !important;
        box-shadow: 0 6px 24px rgba(0,0,0,0.03) !important;
        margin-bottom: 24px !important;
        transition: box-shadow 0.3s ease !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover, [data-testid="stForm"]:hover {
        box-shadow: 0 8px 32px rgba(0,0,0,0.06) !important;
    }

    /* 巢狀容器 (評分項目列) */
    [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--bg-surface) !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        margin-bottom: 12px !important;
        border: 1px solid var(--border) !important;
    }
    [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--accent-blue) !important;
    }

    /* ===== 頁面大標題 (乾淨俐落風格) ===== */
    .page-header-inner {
        display: flex; align-items: center; gap: 20px;
        padding: 0 0 24px 0; margin-bottom: 32px;
        border-bottom: 1px solid var(--border);
    }
    .page-header-icon-wrap {
        width: 56px; height: 56px; flex-shrink: 0;
        background: var(--bg-surface);
        border: 1px solid var(--border); border-radius: 14px;
        display: flex; align-items: center; justify-content: center; font-size: 28px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .page-header-text h2 { margin: 0 0 4px 0; color: var(--text-primary); font-size: 28px; font-weight: 800; letter-spacing: 0.5px; }
    .page-header-text p { margin: 0; color: var(--text-muted); font-size: 15px; }

    /* ===== 步驟標籤 ===== */
    .section-label {
        display: flex; align-items: center; gap: 12px;
        font-size: 18px; font-weight: 800; color: var(--text-primary);
        margin: -10px 0 24px 0; padding-bottom: 16px; border-bottom: 1px dashed var(--border);
    }
    .section-label span {
        display: inline-flex; align-items: center; justify-content: center;
        width: 26px; height: 26px; background: var(--text-primary);
        border-radius: 8px; font-size: 13px; font-weight: 900; color: white; flex-shrink: 0;
    }

    /* ===== 評分區塊標題 (莫蘭迪色塊) ===== */
    .score-section-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 24px; border-radius: 12px; margin: 0 0 20px 0; border: none; }
    .ssh-a { background: rgba(122,139,153,0.12); }
    .ssh-b { background: rgba(130,157,150,0.12); }
    .ssh-c { background: rgba(188,168,127,0.15); }
    .ssh-title { font-weight: 800; font-size: 16px; }
    .ssh-title-a { color: #5B6B78; }
    .ssh-title-b { color: #637A73; }
    .ssh-title-c { color: #9B8762; }
    .ssh-badge { font-size: 13px; font-weight: 800; padding: 6px 16px; border-radius: 20px; font-family: 'DM Mono', monospace; background: #FFFFFF; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .ssh-badge-a { color: #5B6B78; }
    .ssh-badge-b { color: #637A73; }
    .ssh-badge-c { color: #9B8762; }

    /* ===== 評分項目內部文字 ===== */
    .score-title-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
    .score-title { font-weight: 700; font-size: 16px; color: var(--text-primary); }
    .score-weight { font-size: 13px; color: var(--text-secondary); background: var(--bg-hover); padding: 4px 10px; border-radius: 8px; font-family: 'DM Mono', monospace; font-weight: 600; }
    .score-help { font-size: 13px; color: var(--text-muted); line-height: 1.5; font-weight: 500; }
    .score-help-warn { font-size: 13px; color: #AB7575; background: rgba(181,139,143,0.12); padding: 6px 12px; border-radius: 8px; display: inline-block; margin-top: 6px; font-weight: 600; }

    /* ===== 結果看板 ===== */
    .result-panel { background: var(--bg-base); border: 1px dashed var(--border); border-radius: 16px; padding: 40px 24px; text-align: center; height: 100%; transition: all 0.3s ease; }
    .result-panel:hover { background: var(--bg-surface); box-shadow: 0 8px 32px rgba(0,0,0,0.05); border: 1px solid var(--border-light); }
    .result-score-label { font-size: 13px; font-weight: 700; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px; }
    .result-score-value { font-size: 72px; font-weight: 900; color: var(--text-primary); line-height: 1; font-family: 'DM Mono', monospace; margin-bottom: 24px; letter-spacing: -2px;}
    .result-grade-badge { display: inline-block; padding: 8px 24px; border-radius: 24px; font-size: 18px; font-weight: 800; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

    /* ===== Streamlit 輸入元件覆蓋 (流暢互動) ===== */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, [data-testid="stSelectbox"] > div > div, [data-testid="stDateInput"] input { 
        background-color: var(--bg-elevated) !important; 
        border: 1px solid var(--border) !important; 
        border-radius: 10px !important; color: var(--text-primary) !important; 
        font-size: 15px !important; padding: 12px 16px !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, [data-testid="stSelectbox"] > div > div:focus-within { 
        border-color: var(--accent-blue) !important; 
        box-shadow: 0 0 0 4px rgba(122,139,153,0.15) !important; 
        background-color: var(--bg-surface) !important;
    }
    .stTextInput label, .stNumberInput label, .stTextArea label, .stSelectbox label, .stDateInput label { 
        font-size: 14px !important; font-weight: 700 !important; color: var(--text-secondary) !important; margin-bottom: 8px !important;
    }
    
    /* 按鈕樣式 (圓潤、懸停浮起) */
    .stButton > button { 
        background: var(--bg-surface) !important; border: 1px solid var(--border) !important; 
        color: var(--text-secondary) !important; border-radius: 12px !important; 
        font-weight: 700 !important; font-size: 15px !important; padding: 12px 20px !important; 
        transition: all 0.2s ease !important; 
    }
    .stButton > button:hover { 
        background: var(--bg-surface) !important; border-color: var(--accent-blue) !important; 
        color: var(--accent-blue) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        transform: translateY(-2px);
    }
    
    /* 主計算按鈕 (醒目但不刺眼) */
    .stFormSubmitButton > button { 
        background: var(--text-primary) !important; border: none !important; 
        color: white !important; font-size: 16px !important; font-weight: 700 !important; 
        padding: 16px !important; border-radius: 14px !important; 
        box-shadow: 0 8px 20px rgba(52,58,64,0.2) !important; width: 100% !important; margin-top: 20px; 
        transition: all 0.2s ease !important; letter-spacing: 1px;
    }
    .stFormSubmitButton > button:hover {
        background: #1A1D20 !important; transform: translateY(-2px); box-shadow: 0 10px 24px rgba(52,58,64,0.3) !important;
    }
    
    .stCaption, small { font-size: 13px !important; color: var(--text-muted) !important; font-weight: 500 !important;}
    
    .system-footer { text-align: center; padding: 40px 0 20px; color: var(--text-muted); font-size: 13px; margin-top: 40px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)
