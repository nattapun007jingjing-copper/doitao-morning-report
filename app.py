import streamlit as st
import datetime
import os
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# เชื่อมต่อ Google Sheets
from google.oauth2.service_account import Credentials
import gspread

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="แบบบันทึกรายงานเวรเช้า", layout="centered")

# --- ฟังก์ชันบันทึก Sheets ---
def save_to_sheets(date_str, teacher_str, day_str, detail_str):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open("database_morning_report")
        worksheet = sh.get_worksheet(0)
        worksheet.append_row([date_str, teacher_str, day_str, detail_str])
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึกลง Sheets: {e}")
        return False

# --- ส่วนหน้าจอหลัก ---
st.title("โรงเรียนดอยเต่าวิทยาคม")
st.subheader("📝 แบบบันทึกรายงานเวรเช้า (ระบบออนไลน์)")

teacher_list = ["-- เลือกชื่อครูผู้รายงาน --", "ครูชลธิดา", "ครูศิวิไล", "ครูวีระพงศ์", "ครูขนิญฐา", "ครูนงคราญ"]
selected_teacher = st.selectbox("ชื่อครูผู้รายงานเวร", teacher_list)
selected_day = st.selectbox("เวรประจำวัน", ["-- เลือกวันประจำวัน --", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์"])
report_date = st.date_input("วันที่บันทึกรายงาน", datetime.date.today())
report_detail = st.text_area("รายงานเวร", height=200)

# ส่วนอัปโหลดรูปภาพ
st.markdown("### 📸 ภาพประกอบ")
uploaded_files = st.file_uploader("เลือกรูปภาพเพื่อแสดงในรายงาน", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.markdown("#### 🖼️ ภาพที่อัปโหลดปัจจุบัน")
    img_cols = st.columns(3)
    for index, file in enumerate(uploaded_files):
        with img_cols[index % 3]:
            st.image(file, use_container_width=True)

# ปุ่มประมวลผล
if st.button("⚙️ ประมวลผลและส่งข้อมูลเข้าฐานข้อมูล", type="primary", use_container_width=True):
    if selected_teacher == "-- เลือกชื่อครูผู้รายงาน --" or selected_day == "-- เลือกวันประจำวัน --" or not report_detail:
        st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วนก่อนกดบันทึก")
    else:
        # บันทึกข้อมูล
        success = save_to_sheets(report_date.strftime('%d/%m/%Y'), selected_teacher, selected_day, report_detail)
        
        if success:
            st.success("🎉 บันทึกข้อมูลลงฐานข้อมูลส่วนกลางเรียบร้อย!")
            st.balloons()
