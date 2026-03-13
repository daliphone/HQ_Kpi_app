import customtkinter as ctk
from datetime import datetime

# --- 1. 莫蘭迪設計系統 (Morandi Design System) ---
class MorandiTheme:
    BG_BASE = "#EAECEE"         # 溫和的淺灰背景
    BG_SURFACE = "#F8F9FA"      # 卡片表面顏色 (略白)
    TEXT_PRIMARY = "#343A40"    # 深灰文字 (非純黑)
    TEXT_MUTED = "#868E96"      # 輔助說明文字
    
    # 莫蘭迪主色調
    ACCENT_BLUE = "#8395A7"     # 莫蘭迪灰藍 (主按鈕、A區)
    ACCENT_BLUE_HOVER = "#6A7B8C"
    ACCENT_TEAL = "#8BA3A0"     # 莫蘭迪灰綠 (B區)
    ACCENT_ROSE = "#B5989B"     # 莫蘭迪灰粉 (歷史、特優)
    
    CORNER_RADIUS = 12          # 統一圓角大小
    PADDING_L = 24              # 大留白
    PADDING_M = 16              # 中留白

# --- 2. 系統核心資料 ---
JOB_LEVELS = ["助理", "專員", "資深專員", "組長", "副理", "經理", "總監"]
DEPT_LIST  = ["電商專員", "自媒體/行銷", "社群編輯/美編", "會計/行政"]

CONFIG_DATA = {
    "section_weights": [0.50, 0.30, 0.20],
    "basic": [
        {"item": "訂單處理正確率", "weight": 0.30},
        {"item": "客服聊聊響應", "weight": 0.30},
        {"item": "商城活動參與", "weight": 0.20},
        {"item": "上架與庫存準確", "weight": 0.20}
    ]
}

# --- 3. 桌面端 GUI 類別 ---
class ManiAssessmentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 視窗基礎設定
        self.title("馬尼通訊 | 總管理處考核系統 (Pro Max 預覽版)")
        self.geometry("1100x800")
        self.configure(fg_color=MorandiTheme.BG_BASE)
        ctk.set_appearance_mode("Light") # 強制亮色莫蘭迪模式

        # 網格佈局設定
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        """建構左側導航欄"""
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=MorandiTheme.BG_SURFACE, corner_radius=0, width=240)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) 

        # Logo 區塊
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="💠 馬尼通訊", 
            font=("Microsoft JhengHei", 24, "bold"), text_color=MorandiTheme.TEXT_PRIMARY
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 5), sticky="w")
        
        self.sub_logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="數位化管理系統", 
            font=("Microsoft JhengHei", 12), text_color=MorandiTheme.TEXT_MUTED
        )
        self.sub_logo_label.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="w")

        # 導航按鈕
        btn_kwargs = {
            "font": ("Microsoft JhengHei", 15, "bold"),
            "fg_color": "transparent", "text_color": MorandiTheme.TEXT_PRIMARY,
            "hover_color": "#E9ECEF", "corner_radius": MorandiTheme.CORNER_RADIUS,
            "anchor": "w", "height": 45
        }

        self.btn_new = ctk.CTkButton(self.sidebar_frame, text="  📝 新增評核", command=self.show_new_assessment, **btn_kwargs)
        self.btn_new.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_history = ctk.CTkButton(self.sidebar_frame, text="  📋 雲端紀錄", command=self.show_placeholder, **btn_kwargs)
        self.btn_history.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # 預設選中第一個
        self.btn_new.configure(fg_color=MorandiTheme.ACCENT_BLUE, text_color="white", hover_color=MorandiTheme.ACCENT_BLUE_HOVER)

    def _build_main_area(self):
        """建構右側滾動主視窗"""
        self.main_scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scrollable.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_scrollable.grid_columnconfigure(0, weight=1)
        self.main_scrollable.grid_columnconfigure(1, weight=1)
        
        self.show_new_assessment()

    def clear_main_area(self):
        for widget in self.main_scrollable.winfo_children():
            widget.destroy()

    def show_placeholder(self):
        self.clear_main_area()
        self.btn_new.configure(fg_color="transparent", text_color=MorandiTheme.TEXT_PRIMARY)
        self.btn_history.configure(fg_color=MorandiTheme.ACCENT_BLUE, text_color="white")
        
        lbl = ctk.CTkLabel(self.main_scrollable, text="📋 雲端紀錄與設定頁面建置中...", font=("Microsoft JhengHei", 20, "bold"), text_color=MorandiTheme.TEXT_PRIMARY)
        lbl.grid(row=0, column=0, pady=50)

    def show_new_assessment(self):
        self.clear_main_area()
        self.btn_history.configure(fg_color="transparent", text_color=MorandiTheme.TEXT_PRIMARY)
        self.btn_new.configure(fg_color=MorandiTheme.ACCENT_BLUE, text_color="white")

        # 頁面標題
        title_lbl = ctk.CTkLabel(self.main_scrollable, text="新增人員評核", font=("Microsoft JhengHei", 28, "bold"), text_color=MorandiTheme.TEXT_PRIMARY)
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        sub_title = ctk.CTkLabel(self.main_scrollable, text="填寫基本資料與各維度評分，完成後執行計算。", font=("Microsoft JhengHei", 14), text_color=MorandiTheme.TEXT_MUTED)
        sub_title.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 20))

        # --- 1. 基本資料卡片 (左側) ---
        info_frame = ctk.CTkFrame(self.main_scrollable, fg_color=MorandiTheme.BG_SURFACE, corner_radius=MorandiTheme.CORNER_RADIUS)
        info_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text="1. 基本資料", font=("Microsoft JhengHei", 18, "bold"), text_color=MorandiTheme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 10))
        
        form_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
        form_grid.pack(fill="x", padx=20, pady=(0, 20))
        form_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_grid, text="受評人姓名", font=("Microsoft JhengHei", 14), text_color=MorandiTheme.TEXT_PRIMARY).grid(row=0, column=0, sticky="w", pady=10, padx=(0, 15))
        self.ent_name = ctk.CTkEntry(form_grid, font=("Microsoft JhengHei", 14), height=40, border_color="#DDE1EE")
        self.ent_name.grid(row=0, column=1, sticky="ew", pady=10)

        ctk.CTkLabel(form_grid, text="所屬部門", font=("Microsoft JhengHei", 14), text_color=MorandiTheme.TEXT_PRIMARY).grid(row=1, column=0, sticky="w", pady=10, padx=(0, 15))
        self.cb_dept = ctk.CTkComboBox(form_grid, values=DEPT_LIST, font=("Microsoft JhengHei", 14), height=40, border_color="#DDE1EE", button_color=MorandiTheme.ACCENT_BLUE)
        self.cb_dept.grid(row=1, column=1, sticky="ew", pady=10)

        # --- 2. 評分卡片 (右側) ---
        score_frame = ctk.CTkFrame(self.main_scrollable, fg_color=MorandiTheme.BG_SURFACE, corner_radius=MorandiTheme.CORNER_RADIUS)
        score_frame.grid(row=2, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(score_frame, text="2. 績效評分維度", font=("Microsoft JhengHei", 18, "bold"), text_color=MorandiTheme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(score_frame, text="▸ A. 職務基本標準 (KPI)", font=("Microsoft JhengHei", 16, "bold"), text_color=MorandiTheme.ACCENT_BLUE).pack(anchor="w", padx=20, pady=5)
        
        self.score_entries = []
        for item in CONFIG_DATA["basic"]:
            item_frame = ctk.CTkFrame(score_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=20, pady=8)
            
            lbl_title = ctk.CTkLabel(item_frame, text=f"{item['item']} ({int(item['weight']*100)}%)", font=("Microsoft JhengHei", 14), text_color=MorandiTheme.TEXT_PRIMARY)
            lbl_title.pack(side="left")
            
            ent_score = ctk.CTkEntry(item_frame, width=70, font=("Microsoft JhengHei", 14), justify="center", border_color="#DDE1EE")
            ent_score.insert(0, "80")
            ent_score.pack(side="right")
            self.score_entries.append((ent_score, item['weight']))

        ctk.CTkLabel(score_frame, text="▸ C. 主管綜合評核 (20%)", font=("Microsoft JhengHei", 16, "bold"), text_color=MorandiTheme.ACCENT_ROSE).pack(anchor="w", padx=20, pady=(25, 5))
        self.ent_manager = ctk.CTkEntry(score_frame, placeholder_text="輸入 1~10 分", font=("Microsoft JhengHei", 14), height=40, border_color="#DDE1EE")
        self.ent_manager.pack(fill="x", padx=20, pady=10)

        # 計算按鈕
        calc_btn = ctk.CTkButton(
            score_frame, text="⚖ 執行計算並鎖定分數", 
            command=self.calculate_score,
            font=("Microsoft JhengHei", 16, "bold"), height=50,
            fg_color=MorandiTheme.ACCENT_BLUE, hover_color=MorandiTheme.ACCENT_BLUE_HOVER, corner_radius=MorandiTheme.CORNER_RADIUS
        )
        calc_btn.pack(fill="x", padx=20, pady=(30, 15))

        self.result_lbl = ctk.CTkLabel(score_frame, text="最終總分：--", font=("Arial", 28, "bold"), text_color=MorandiTheme.TEXT_PRIMARY)
        self.result_lbl.pack(pady=10)

    def calculate_score(self):
        """處理計分邏輯 (完整防呆版)"""
        try:
            total_a = 0
            for ent, weight in self.score_entries:
                val = ent.get().strip()
                score = float(val) if val else 0.0
                total_a += score * weight
            
            mgr_val = self.ent_manager.get().strip()
            mgr_score = float(mgr_val) * 10 * 0.20 if mgr_val else 0.0
            
            final_score = total_a + mgr_score
            self.result_lbl.configure(text=f"最終總分：{final_score:.2f}", text_color=MorandiTheme.ACCENT_TEAL)
            
        except ValueError:
            self.result_lbl.configure(text="⚠ 請輸入有效數字！", text_color=MorandiTheme.ACCENT_ROSE)

if __name__ == "__main__":
    app = ManiAssessmentApp()
    app.mainloop()
