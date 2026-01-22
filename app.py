import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import sys
from datetime import datetime
import ctypes

# --- 資源路徑函式 ---
def resource_path(relative_path):
    """ 取得資源的絕對路徑 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 資料預設值 ---
DEFAULT_ECOMMERCE_A = [
    ("商品上架效率", "1.新品通知上架\n2.平台上架"),
    ("訂單處理正確率", "1.每月錯誤率≦3%"),
    ("聊聊處理時效", "1.平均處理時間 ≦24hr\n2.回覆正確性≦90%"),
    ("成效追蹤與分析", ""),
    ("促銷活動配合度", "1.上檔準時率、促銷活動回報率")
]
DEFAULT_ECOMMERCE_B = [
    ("跨部門協作", ""),
    ("學習與改善能力", "1.曝光成長、轉換率提升率（月成長）"),
    ("環境", "")
]

DEFAULT_MEDIA_A = [
    ("貼文/短影音產出數", "1.文章 12 篇/月，短影音 12 支/月"),
    ("內容其明確性與目的性", "1. 成品內容有其目標，例如:資費優惠營造留言詢問目的、功能介紹引發商品購買意圖。"),
    ("成效追蹤與分析", "每月統計，準時繳交與內容完整性"),
    ("互動率（留言/分享/點讚）", "")
]
DEFAULT_MEDIA_B = [
    ("創意與學習性", "自主學習：有參與行銷/數據/剪輯相關課程、紀錄可查\n解決內容卡關問題能力：是否有提出並執行改善提案\n接受反饋與優化行為：接受主管/團隊建議後之行動與調整"),
    ("跨部門協作", "主動與設計/行銷配合：有效溝通設計素材、廣告文案需求\n協助他人處理急件或突發任務：是否主動支援他人專案困難\n回覆訊息與開會表現：清晰回應、準備充分、具建設性"),
    ("環境", "")
]

DEFAULT_EDITOR_A = [
    ("設計完成時效", "1. 任務完成時間。\n2. "),
    ("創意與排版多樣性", "1. 提供選擇性及目標性的成品"),
    ("成效追蹤與分析", "1. 平台後台數據整理分析"),
    ("互動率（留言/分享/點讚）", "")
]
DEFAULT_EDITOR_B = [
    ("創意與學習性", "新工具/新風格的主動學習\n設計提案的創新度\n使用者體驗導向的優化思維"),
    ("跨部門協作", "提供替代方案或設計建議的積極性\n與電商、行銷的專案協調效率"),
    ("環境", "")
]

DEFAULT_CONFIG = {
    "電商": {
        "section_weights": [0.50, 0.30, 0.20],
        "basic_fields": ["訂單處理正確率", "上架準確率", "活動提案數", "平台廣告效益"],
        "basic_weights": [0.30, 0.30, 0.20, 0.20], 
        "excellent_fields": ["執行力", "自我學習", "個人優點與貢獻"],
        "excellent_weights": [0.33, 0.33, 0.34], 
        "threshold": 80,
        "text_fields_a": DEFAULT_ECOMMERCE_A,
        "text_fields_b": DEFAULT_ECOMMERCE_B
    },
    "自媒體": {
        "section_weights": [0.50, 0.30, 0.20],
        "basic_fields": ["曝光成長率", "互動率", "導流貢獻", "內容品質"],
        "basic_weights": [0.25, 0.25, 0.25, 0.25], 
        "excellent_fields": ["執行力", "自我學習", "個人優點與貢獻"],
        "excellent_weights": [0.33, 0.33, 0.34], 
        "threshold": 80,
        "text_fields_a": DEFAULT_MEDIA_A,
        "text_fields_b": DEFAULT_MEDIA_B
    },
    "社群編輯": {
        "section_weights": [0.50, 0.30, 0.20],
        "basic_fields": ["素材完成率", "設計品質", "文案提案", "品牌一致性"],
        "basic_weights": [0.30, 0.30, 0.20, 0.20], 
        "excellent_fields": ["執行力", "自我學習", "個人優點與貢獻"],
        "excellent_weights": [0.33, 0.33, 0.34], 
        "threshold": 85,
        "text_fields_a": DEFAULT_EDITOR_A,
        "text_fields_b": DEFAULT_EDITOR_B
    },
    "通用": {
        "section_weights": [0.50, 0.30, 0.20],
        "basic_fields": ["KPI_1", "KPI_2", "KPI_3", "KPI_4"],
        "basic_weights": [0.25, 0.25, 0.25, 0.25],
        "excellent_fields": ["執行力", "自我學習", "個人優點與貢獻"],
        "excellent_weights": [0.33, 0.33, 0.34],
        "threshold": 80,
        "text_fields_a": [("本月職務重點", "請輸入內容...")],
        "text_fields_b": [("工作品質", "請輸入內容...")]
    }
}

for dept in ["會計", "人資", "行銷"]:
    if dept not in DEFAULT_CONFIG:
        DEFAULT_CONFIG[dept] = DEFAULT_CONFIG["通用"].copy()

JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]

class KPIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("總管理處人員評核系統 v23.0 (精細級距版)")
        self.root.state('zoomed')

        try:
            myappid = 'mycompany.kpi.evaluation.v23'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            icon_path = resource_path("logo.ico")
            self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self.current_config = {}
        for dept, data in DEFAULT_CONFIG.items():
            self.current_config[dept] = {
                "section_weights": list(data["section_weights"]),
                "basic_fields": list(data["basic_fields"]),
                "basic_weights": list(data["basic_weights"]),
                "excellent_fields": list(data["excellent_fields"]),
                "excellent_weights": list(data["excellent_weights"]),
                "threshold": data["threshold"],
                "text_fields_a": [list(item) for item in data["text_fields_a"]],
                "text_fields_b": [list(item) for item in data["text_fields_b"]]
            }
        
        self.batch_queue = []
        self.current_calculated_data = None
        
        # --- UI 佈局 ---
        tk.Label(root, text="總管理處人員評核與獎金試算系統 v23.0", font=("微軟正黑體", 16, "bold"), fg="#1a237e", bg="#E8EAF6").pack(fill="x", pady=0, ipady=10)

        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=6, bg="#CFD8DC")
        self.paned_window.pack(fill="both", expand=True)

        self.panel_left_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.panel_left_frame, width=700, stretch="always") 

        self.panel_middle_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.panel_middle_frame, width=450)

        self.panel_right_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.panel_right_frame, width=350)

        self.init_left_panel()
        self.init_middle_panel()
        self.init_right_panel()

    def bind_mousewheel(self, widget):
        def _on_mousewheel(event):
            widget.yview_scroll(int(-1*(event.delta/120)), "units")
        widget.bind('<Enter>', lambda e: widget.bind_all("<MouseWheel>", _on_mousewheel))
        widget.bind('<Leave>', lambda e: widget.unbind_all("<MouseWheel>"))

    # --- 左欄 ---
    def init_left_panel(self):
        lbl_header = tk.Label(self.panel_left_frame, text="1. 評分與計算", font=("微軟正黑體", 14, "bold"), fg="white", bg="#1565C0", pady=8)
        lbl_header.pack(fill="x")

        canvas = tk.Canvas(self.panel_left_frame, bg="#FAFAFA")
        scrollbar = ttk.Scrollbar(self.panel_left_frame, orient="vertical", command=canvas.yview)
        self.panel_left = tk.Frame(canvas, padx=20, pady=20, bg="#FAFAFA")
        
        self.panel_left.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.panel_left, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.bind_mousewheel(canvas)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. 人員資料
        frame_meta = tk.LabelFrame(self.panel_left, text=" 人員資料 ", padx=15, pady=15, bg="#FAFAFA", font=("微軟正黑體", 12, "bold"), fg="#37474F", relief="groove", bd=2)
        frame_meta.pack(fill="x", pady=(0, 20))
        
        tk.Label(frame_meta, text="👤 姓名:", bg="#FAFAFA", font=("微軟正黑體", 11)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_name = tk.Entry(frame_meta, width=12, font=("微軟正黑體", 11), bg="#ECEFF1", relief="flat"); self.entry_name.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(frame_meta, text="🏢 部門:", bg="#FAFAFA", font=("微軟正黑體", 11)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.dept_combo = ttk.Combobox(frame_meta, values=list(self.current_config.keys()), width=12, font=("微軟正黑體", 11))
        self.dept_combo.grid(row=0, column=3, sticky="w", padx=5)
        self.dept_combo.bind("<<ComboboxSelected>>", self.on_dept_selected)

        tk.Label(frame_meta, text="🎓 職等:", bg="#FAFAFA", font=("微軟正黑體", 11)).grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.combo_level = ttk.Combobox(frame_meta, values=JOB_LEVELS, width=10, font=("微軟正黑體", 11)); self.combo_level.grid(row=0, column=5, sticky="w", padx=5); self.combo_level.set("專員")

        tk.Label(frame_meta, text="👨‍💼 主管:", bg="#FAFAFA", font=("微軟正黑體", 11)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_supervisor = tk.Entry(frame_meta, width=12, font=("微軟正黑體", 11), bg="#ECEFF1", relief="flat"); self.entry_supervisor.grid(row=1, column=1, sticky="w", padx=5)

        tk.Label(frame_meta, text="📅 日期:", bg="#FAFAFA", font=("微軟正黑體", 11)).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_date = tk.Entry(frame_meta, width=12, font=("微軟正黑體", 11), bg="#ECEFF1", relief="flat"); self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d")); self.entry_date.grid(row=1, column=3, sticky="w", padx=5)

        # 2. 評分項目區
        frame_top_split = tk.Frame(self.panel_left, bg="#FAFAFA")
        frame_top_split.pack(fill="x", expand=True)

        self.frame_sec_a = tk.LabelFrame(frame_top_split, text="A. 職務基本標準", font=("微軟正黑體", 14, "bold"), fg="#1565C0", bg="#E3F2FD", padx=10, pady=10, relief="solid", bd=1)
        self.frame_sec_a.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
        self.frame_basic = tk.Frame(self.frame_sec_a, bg="#E3F2FD")
        self.frame_basic.pack(fill="x")
        self.basic_entries = []

        self.frame_sec_b = tk.LabelFrame(frame_top_split, text="B. 卓越主動表現", font=("微軟正黑體", 14, "bold"), fg="#2E7D32", bg="#E8F5E9", padx=10, pady=10, relief="solid", bd=1)
        self.frame_sec_b.pack(side=tk.LEFT, fill="both", expand=True)
        self.frame_excellent = tk.Frame(self.frame_sec_b, bg="#E8F5E9")
        self.frame_excellent.pack(fill="x")
        self.excellent_entries = []

        # C區
        self.frame_sec_c = tk.LabelFrame(self.panel_left, text="C. 主管綜合評核", font=("微軟正黑體", 14, "bold"), fg="#E65100", bg="#FFF3E0", padx=15, pady=15, relief="solid", bd=1)
        self.frame_sec_c.pack(fill="x", pady=(20, 0))
        
        f_mgr = tk.Frame(self.frame_sec_c, bg="#FFF3E0"); f_mgr.pack(fill="x", pady=5)
        tk.Label(f_mgr, text="評分 (1-10):", bg="#FFF3E0", font=("微軟正黑體", 14, "bold")).pack(side=tk.LEFT)
        self.combo_mgr_score = ttk.Combobox(f_mgr, values=[str(i) for i in range(1, 11)], width=5, state="readonly", font=("Arial", 18, "bold"))
        self.combo_mgr_score.current(7); self.combo_mgr_score.pack(side=tk.LEFT, padx=15)
        
        tk.Label(self.frame_sec_c, text="反饋評語:", bg="#FFF3E0", anchor="w", font=("微軟正黑體", 12)).pack(fill="x", pady=(10,0))
        self.text_comment = tk.Text(self.frame_sec_c, height=3, width=30, font=("微軟正黑體", 12), bg="white", relief="flat"); self.text_comment.pack(fill="x", pady=5)

        # 3. 獎金 (級距版)
        frame_bonus_zone = tk.LabelFrame(self.panel_left, text="💰 獎金試算中心 (精細級距)", padx=15, pady=15, bg="#FFF8E1", font=("微軟正黑體", 14, "bold"), fg="#F57F17", relief="solid", bd=1)
        frame_bonus_zone.pack(fill="x", pady=(20, 20))
        
        # 顯示級距說明 (可自訂)
        lbl_info = tk.Label(frame_bonus_zone, text="S(90+):1.5 | A(80+):1.0 | B+(75+):0.8 | B-(70+):0.6 | C(60+):0.5 | D:0", font=("Arial", 9), bg="#FFF8E1", fg="gray")
        lbl_info.pack(anchor="w", pady=(0, 5))

        f_vars = tk.Frame(frame_bonus_zone, bg="#FFF8E1")
        f_vars.pack(fill="x", pady=5)
        tk.Label(f_vars, text="月薪 / 基數:", bg="#FFF8E1", font=("微軟正黑體", 12)).pack(side=tk.LEFT)
        self.entry_max_bonus = tk.Entry(f_vars, width=12, justify="right", font=("Arial", 11)); self.entry_max_bonus.insert(0, "0"); self.entry_max_bonus.pack(side=tk.LEFT, padx=5)
        tk.Label(f_vars, text="額外倍率:", bg="#FFF8E1", font=("微軟正黑體", 12)).pack(side=tk.LEFT, padx=(15,0))
        self.entry_bonus_multiplier = tk.Entry(f_vars, width=5, justify="center", font=("Arial", 11)); self.entry_bonus_multiplier.insert(0, "1.0"); self.entry_bonus_multiplier.pack(side=tk.LEFT, padx=5)

        self.btn_calc = tk.Button(frame_bonus_zone, text="計算總分與獎金 (Enter)", command=self.calculate_score, bg="#FFD600", fg="#333", font=("微軟正黑體", 12, "bold"), pady=5, relief="raised")
        self.btn_calc.pack(fill="x", pady=10)

        f_results = tk.Frame(frame_bonus_zone, bg="#FFF8E1")
        f_results.pack(fill="x")
        self.lbl_score_res = tk.Label(f_results, text="總分: --", font=("微軟正黑體", 16, "bold"), bg="#FFF8E1", fg="#333", width=25, anchor="w")
        self.lbl_score_res.pack(side=tk.LEFT)
        tk.Label(f_results, text="實得 $", font=("微軟正黑體", 16, "bold"), bg="#FFF8E1", fg="#D84315").pack(side=tk.LEFT)
        self.entry_final_bonus = tk.Entry(f_results, width=12, fg="#D84315", font=("Arial", 16, "bold"), justify="right", bd=0, bg="#FFF8E1")
        self.entry_final_bonus.pack(side=tk.LEFT)
        
        self.btn_add_queue = tk.Button(self.panel_left, text="加入匯出清單", command=self.add_to_queue, bg="#4CAF50", fg="white", state="disabled", font=("微軟正黑體", 12, "bold"), pady=8, relief="raised")
        self.btn_add_queue.pack(fill="x", pady=5)

    # --- 中欄 ---
    def init_middle_panel(self):
        lbl_header = tk.Label(self.panel_middle_frame, text="2. 每月職務目標 (A/B區)", font=("微軟正黑體", 14, "bold"), fg="white", bg="#4527A0", pady=8)
        lbl_header.pack(fill="x")

        canvas = tk.Canvas(self.panel_middle_frame, bg="white")
        scrollbar = ttk.Scrollbar(self.panel_middle_frame, orient="vertical", command=canvas.yview)
        self.panel_middle = tk.Frame(canvas, bg="white", padx=20, pady=20)
        
        self.panel_middle.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.panel_middle, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.bind_mousewheel(canvas)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.lbl_mid_a = tk.Label(self.panel_middle, text="A. 職務內容與目標", font=("微軟正黑體", 14, "bold"), fg="white", bg="#5E35B1", padx=10, pady=5, anchor="w")
        self.lbl_mid_a.pack(fill="x", pady=(0,10))
        self.frame_text_a_container = tk.Frame(self.panel_middle, bg="white")
        self.frame_text_a_container.pack(fill="x", pady=(0, 20))
        self.text_widgets_a = []

        self.lbl_mid_b = tk.Label(self.panel_middle, text="B. 內在品質與工作環境", font=("微軟正黑體", 14, "bold"), fg="white", bg="#00695C", padx=10, pady=5, anchor="w")
        self.lbl_mid_b.pack(fill="x", pady=(0,10))
        self.frame_text_b_container = tk.Frame(self.panel_middle, bg="white")
        self.frame_text_b_container.pack(fill="x", pady=(0, 20))
        self.text_widgets_b = []

    # --- 右欄 ---
    def init_right_panel(self):
        lbl_header = tk.Label(self.panel_right_frame, text="3. 設定與匯出", font=("微軟正黑體", 14, "bold"), fg="white", bg="#455A64", pady=8)
        lbl_header.pack(fill="x")

        self.panel_right = tk.Frame(self.panel_right_frame, bg="#ECEFF1", padx=10, pady=10)
        self.panel_right.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self.panel_right)
        self.notebook.pack(fill="both", expand=True)

        self.tab_fields = tk.Frame(self.notebook, bg="#ECEFF1")
        self.notebook.add(self.tab_fields, text="評分設定")

        self.tab_texts = tk.Frame(self.notebook, bg="#ECEFF1")
        self.notebook.add(self.tab_texts, text="職務目標設定")

        self.tab_list = tk.Frame(self.notebook, bg="#ECEFF1")
        self.notebook.add(self.tab_list, text="待匯出清單")

        self.setup_config_tab()
        self.setup_text_config_tab()
        self.setup_list_tab()

    # --- 邏輯 ---
    def on_dept_selected(self, event):
        self.update_left_panel_fields()
        self.update_middle_panel_fields()
        self.load_config_to_tabs()

    def update_left_panel_fields(self):
        for w in self.frame_basic.winfo_children(): w.destroy()
        for w in self.frame_excellent.winfo_children(): w.destroy()
        self.basic_entries = []
        self.excellent_entries = []

        dept = self.dept_combo.get()
        config = self.current_config.get(dept)
        if not config: return

        w_a, w_b, w_c = config["section_weights"]
        self.frame_sec_a.config(text=f"A. 職務基本標準 ({int(w_a*100)}%)")
        self.frame_sec_b.config(text=f"B. 卓越主動表現 ({int(w_b*100)}%)")
        self.frame_sec_c.config(text=f"C. 主管綜合評核 ({int(w_c*100)}%)")

        for i, (f, w) in enumerate(zip(config["basic_fields"], config["basic_weights"])):
            fr = tk.Frame(self.frame_basic, bg="#E3F2FD"); fr.pack(fill="x", pady=5)
            tk.Label(fr, text=f, width=15, anchor="w", font=("微軟正黑體", 12), bg="#E3F2FD").pack(side=tk.LEFT)
            ent = tk.Entry(fr, width=4, font=("Arial", 18, "bold"), justify='center'); ent.pack(side=tk.RIGHT)
            ent.bind("<Return>", lambda e, idx=i: self.focus_next_basic(idx))
            self.basic_entries.append(ent)

        for i, (f, w) in enumerate(zip(config["excellent_fields"], config["excellent_weights"])):
            fr = tk.Frame(self.frame_excellent, bg="#E8F5E9"); fr.pack(fill="x", pady=5)
            tk.Label(fr, text=f, width=15, anchor="w", font=("微軟正黑體", 12), bg="#E8F5E9").pack(side=tk.LEFT)
            ent = tk.Entry(fr, width=4, font=("Arial", 18, "bold"), justify='center'); ent.pack(side=tk.RIGHT)
            ent.bind("<Return>", lambda e, idx=i: self.focus_next_excellent(idx))
            self.excellent_entries.append(ent)

    def focus_next_basic(self, idx):
        if idx + 1 < len(self.basic_entries):
            self.basic_entries[idx+1].focus_set()
        elif self.excellent_entries:
            self.excellent_entries[0].focus_set()

    def focus_next_excellent(self, idx):
        if idx + 1 < len(self.excellent_entries):
            self.excellent_entries[idx+1].focus_set()
        else:
            self.calculate_score()

    def update_middle_panel_fields(self):
        for w in self.frame_text_a_container.winfo_children(): w.destroy()
        for w in self.frame_text_b_container.winfo_children(): w.destroy()
        self.text_widgets_a = []
        self.text_widgets_b = []

        dept = self.dept_combo.get()
        config = self.current_config.get(dept)
        if not config: return

        for name, default_text in config["text_fields_a"]:
            f = tk.Frame(self.frame_text_a_container, bg="white", pady=5)
            f.pack(fill="x")
            tk.Label(f, text=f"● {name}", font=("微軟正黑體", 14, "bold"), bg="white", fg="#4527A0").pack(anchor="w")
            txt = tk.Text(f, height=3, width=50, bg="#F3E5F5", font=("微軟正黑體", 14))
            txt.insert("1.0", default_text)
            txt.pack(fill="x", pady=2)
            self.text_widgets_a.append((name, txt))

        for name, default_text in config["text_fields_b"]:
            f = tk.Frame(self.frame_text_b_container, bg="white", pady=5)
            f.pack(fill="x")
            tk.Label(f, text=f"● {name}", font=("微軟正黑體", 14, "bold"), bg="white", fg="#00695C").pack(anchor="w")
            txt = tk.Text(f, height=3, width=50, bg="#E0F2F1", font=("微軟正黑體", 14))
            txt.insert("1.0", default_text)
            txt.pack(fill="x", pady=2)
            self.text_widgets_b.append((name, txt))

    def setup_config_tab(self):
        self.frame_conf_content = tk.Frame(self.tab_fields, bg="#ECEFF1")
        self.frame_conf_content.pack(fill="both", expand=True, padx=5, pady=5)
        self.config_row_entries = []
        btn_update = tk.Button(self.tab_fields, text="更新評分設定", command=self.apply_config, bg="#FFCC80")
        btn_update.pack(fill="x", pady=10)

    def setup_text_config_tab(self):
        self.frame_text_conf_content = tk.Frame(self.tab_texts, bg="#ECEFF1")
        self.frame_text_conf_content.pack(fill="both", expand=True, padx=5, pady=5)
        self.text_config_entries = []
        btn_update = tk.Button(self.tab_texts, text="更新預設職務目標", command=self.apply_text_config, bg="#FFCC80")
        btn_update.pack(fill="x", pady=10)

    def load_config_to_tabs(self):
        for w in self.frame_conf_content.winfo_children(): w.destroy()
        self.config_row_entries = []
        dept = self.dept_combo.get()
        config = self.current_config.get(dept)
        if not config: return
        
        tk.Label(self.frame_conf_content, text="A. 職務基本標準 (項目/權重)", bg="#E3F2FD").pack(fill="x")
        for f, w in zip(config["basic_fields"], config["basic_weights"]): self.create_conf_row(f, w, "A")
        tk.Button(self.frame_conf_content, text="+ 新增", command=lambda: self.create_conf_row("新項目", 0.1, "A")).pack()
        
        tk.Label(self.frame_conf_content, text="B. 卓越主動表現 (項目/權重)", bg="#E8F5E9").pack(fill="x", pady=(10,0))
        for f, w in zip(config["excellent_fields"], config["excellent_weights"]): self.create_conf_row(f, w, "B")
        tk.Button(self.frame_conf_content, text="+ 新增", command=lambda: self.create_conf_row("新項目", 0.1, "B")).pack()

        for w in self.frame_text_conf_content.winfo_children(): w.destroy()
        self.text_config_entries = []
        
        tk.Label(self.frame_text_conf_content, text="A. 職務內容與目標 (標題/預設內容)", bg="#D1C4E9").pack(fill="x")
        for name, content in config["text_fields_a"]: self.create_text_conf_row(name, content, "TA")
        tk.Button(self.frame_text_conf_content, text="+ 新增", command=lambda: self.create_text_conf_row("新欄位", "", "TA")).pack()

        tk.Label(self.frame_text_conf_content, text="B. 內在品質與工作環境 (標題/預設內容)", bg="#B2DFDB").pack(fill="x", pady=(10,0))
        for name, content in config["text_fields_b"]: self.create_text_conf_row(name, content, "TB")
        tk.Button(self.frame_text_conf_content, text="+ 新增", command=lambda: self.create_text_conf_row("新欄位", "", "TB")).pack()

    def create_conf_row(self, name, weight, sec):
        r = tk.Frame(self.frame_conf_content); r.pack(fill="x", pady=1)
        e_n = tk.Entry(r, width=15); e_n.insert(0, name); e_n.pack(side=tk.LEFT)
        e_w = tk.Entry(r, width=5); e_w.insert(0, str(weight)); e_w.pack(side=tk.LEFT)
        tk.Button(r, text="X", command=lambda: r.destroy(), bg="#FFEBEE", width=2).pack(side=tk.LEFT)
        self.config_row_entries.append((e_n, e_w, r, sec))

    def create_text_conf_row(self, name, content, sec):
        r = tk.Frame(self.frame_text_conf_content); r.pack(fill="x", pady=2)
        e_n = tk.Entry(r, width=15); e_n.insert(0, name); e_n.pack(side=tk.LEFT, anchor="n")
        t_c = tk.Text(r, height=2, width=30); t_c.insert("1.0", content); t_c.pack(side=tk.LEFT)
        tk.Button(r, text="X", command=lambda: r.destroy(), bg="#FFEBEE", width=2).pack(side=tk.LEFT, anchor="n")
        self.text_config_entries.append((e_n, t_c, r, sec))

    def apply_config(self):
        dept = self.dept_combo.get()
        new_a_f, new_a_w, new_b_f, new_b_w = [], [], [], []
        try:
            for en, ew, r, sec in self.config_row_entries:
                if r.winfo_exists():
                    if sec == "A": new_a_f.append(en.get()); new_a_w.append(float(ew.get()))
                    else: new_b_f.append(en.get()); new_b_w.append(float(ew.get()))
            self.current_config[dept]["basic_fields"] = new_a_f
            self.current_config[dept]["basic_weights"] = new_a_w
            self.current_config[dept]["excellent_fields"] = new_b_f
            self.current_config[dept]["excellent_weights"] = new_b_w
            self.update_left_panel_fields()
            messagebox.showinfo("成功", "評分項目已更新")
        except: messagebox.showerror("錯誤", "數值格式錯誤")

    def apply_text_config(self):
        dept = self.dept_combo.get()
        ta, tb = [], []
        for en, tc, r, sec in self.text_config_entries:
            if r.winfo_exists():
                item = (en.get(), tc.get("1.0", tk.END).strip())
                if sec == "TA": ta.append(item)
                else: tb.append(item)
        self.current_config[dept]["text_fields_a"] = ta
        self.current_config[dept]["text_fields_b"] = tb
        self.update_middle_panel_fields()
        messagebox.showinfo("成功", "職務目標預設值已更新")

    def setup_list_tab(self):
        self.tree = ttk.Treeview(self.tab_list, columns=("Name", "Total", "Bonus"), show='headings', height=15)
        self.tree.heading("Name", text="姓名"); self.tree.heading("Total", text="總分"); self.tree.heading("Bonus", text="獎金")
        self.tree.column("Name", width=80); self.tree.column("Total", width=60); self.tree.column("Bonus", width=80)
        self.tree.pack(fill="both", expand=True)
        tk.Button(self.tab_list, text="匯出 CSV", command=self.export_batch, bg="#4CAF50", fg="white").pack(fill="x", pady=5)
        tk.Button(self.tab_list, text="清除", command=lambda: self.tree.delete(*self.tree.get_children()) or self.batch_queue.clear()).pack(fill="x")

    def calculate_score(self):
        dept = self.dept_combo.get()
        if not dept: return
        config = self.current_config[dept]
        
        try:
            w_a, w_b, w_c = config["section_weights"]
            sc_a = sum(float(e.get() or 0)*w for e, w in zip(self.basic_entries, config["basic_weights"])) * w_a
            sc_b = sum(float(e.get() or 0)*w for e, w in zip(self.excellent_entries, config["excellent_weights"])) * w_b
            sc_c = (int(self.combo_mgr_score.get()) * 10) * w_c
            total = sc_a + sc_b + sc_c
            
            # --- 級距計算 ---
            # 獲取基數 (月薪)
            try:
                base_salary = float(self.entry_max_bonus.get())
            except:
                base_salary = 0
            
            try:
                bonus_multi = float(self.entry_bonus_multiplier.get())
            except:
                bonus_multi = 1.0

            # 判斷級距
            bonus_months = 0
            grade_name = ""
            
            if total >= 90:
                bonus_months = 1.5
                grade_name = "S (90-100)"
            elif total >= 80:
                bonus_months = 1.0
                grade_name = "A (80-89)"
            elif total >= 75:
                bonus_months = 0.8 # B+
                grade_name = "B+ (75-79)"
            elif total >= 70:
                bonus_months = 0.6 # B-
                grade_name = "B- (70-74)"
            elif total >= 60:
                bonus_months = 0.5
                grade_name = "C (60-69)"
            else:
                bonus_months = 0
                grade_name = "D (<60)"

            # 計算最終金額
            final_bonus = base_salary * bonus_months * bonus_multi

            self.lbl_score_res.config(text=f"總分: {total:.2f} [{grade_name}]")
            self.entry_final_bonus.delete(0, tk.END); self.entry_final_bonus.insert(0, str(int(final_bonus)))
            self.btn_add_queue.config(state="normal")
            
            self.current_calculated_data = {
                "評分日期": self.entry_date.get(),
                "評分主管": self.entry_supervisor.get(),
                "受評姓名": self.entry_name.get(),
                "職等": self.combo_level.get(),
                "部門": dept,
                "總分": f"{total:.2f}",
                "評等": grade_name, # 新增欄位
                "核定月數": str(bonus_months), # 新增欄位
                "主管評語": self.text_comment.get("1.0", tk.END).strip()
            }
            for name, txt in self.text_widgets_a:
                self.current_calculated_data[f"目標_{name}"] = txt.get("1.0", tk.END).strip()
            for name, txt in self.text_widgets_b:
                self.current_calculated_data[f"目標_{name}"] = txt.get("1.0", tk.END).strip()

        except Exception as e:
            messagebox.showerror("錯誤", str(e))

    def add_to_queue(self):
        if not self.current_calculated_data: return
        self.current_calculated_data["實得獎金"] = self.entry_final_bonus.get()
        self.batch_queue.append(self.current_calculated_data)
        self.tree.insert("", "end", values=(self.current_calculated_data["受評姓名"], self.current_calculated_data["總分"], self.current_calculated_data["實得獎金"]))
        self.btn_add_queue.config(state="disabled")

    def export_batch(self):
        if not self.batch_queue: return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"績效評核_{datetime.now().strftime('%Y%m%d')}.csv")
        if not filepath: return
        try:
            keys = set()
            for d in self.batch_queue: keys.update(d.keys())
            priority = ["評分日期","評分主管","受評姓名","職等","部門","總分","評等","核定月數","實得獎金","主管評語"]
            others = sorted([k for k in keys if k not in priority])
            header = priority + others
            
            with open(filepath, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                writer.writerows(self.batch_queue)
            messagebox.showinfo("成功", "匯出完成")
            self.batch_queue = []
            self.tree.delete(*self.tree.get_children())
        except Exception as e:
            messagebox.showerror("失敗", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = KPIApp(root)
    root.mainloop()
