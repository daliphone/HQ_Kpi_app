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
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS：Pro Max 莫蘭迪現代設計系統 (Morandi Design System) ---
st.markdown("""
<style>
/* (這裡放我們剛剛那一長串的 CSS 代碼) */
