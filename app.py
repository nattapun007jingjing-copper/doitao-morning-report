import streamlit as st
import datetime
import gspread
import os
from google.oauth2.service_account import Credentials

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="แบบบันทึกรายงานเวรเช้า", layout="centered")

# --- ฟังก์ชันบันทึกข้อมูล ---
def save_to_sheets(date_str, teacher_str, day_str, detail_str):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open("database_morning_report")
        worksheet = sh.get_worksheet(0)
        # บันทึกข้อมูล 4 คอลัมน์ (คอลัมน์ที่ 5 คือลิงก์ PDF ที่ Apps Script จะเติมให้)
        worksheet.append_row([date_str, teacher_str, day_str, detail_str])
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
        return False

# --- หน้าจอหลัก ---
if os.path.exists("logo.jpg"):
    st.image("logo.jpg", width=150)

st.title("โรงเรียนดอยเต่าวิทยาคม")
st.subheader("📝 ระบบบันทึกรายงานเวรเช้า")

# ฟอร์มกรอกข้อมูล
teacher_list = ["-- เลือกชื่อครูผู้รายงาน --", "ครูชลธิดา", "ครูศิวิไล", "ครูวีระพงศ์", "ครูขนิญฐา", "ครูนงคราญ"]
selected_teacher = st.selectbox("ชื่อครูผู้รายงานเวร", teacher_list)
selected_day = st.selectbox("เวรประจำวัน", ["-- เลือกวันประจำวัน --", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์"])
report_date = st.date_input("วันที่บันทึกรายงาน", datetime.date.today())
report_detail = st.text_area("รายงานเวร", height=200)

# ระบบอัปโหลดรูปภาพ (ที่หายไป)
st.markdown("### 📸 ภาพประกอบ")
uploaded_files = st.file_uploader("เลือกรูปภาพเพื่อแสดงในรายงาน (ดูหน้าเว็บเท่านั้น)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    img_cols = st.columns(3)
    for index, file in enumerate(uploaded_files):
        with img_cols[index % 3]:
            st.image(file, use_container_width=True)

# ปุ่มประมวลผล
if st.button("⚙️ ประมวลผลและส่งข้อมูลเข้าฐานข้อมูล", type="primary", use_container_width=True):
    if selected_teacher == "-- เลือกชื่อครูผู้รายงาน --" or selected_day == "-- เลือกวันประจำวัน --" or not report_detail:
        st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
    else:
        if save_to_sheets(report_date.strftime('%d/%m/%Y'), selected_teacher, selected_day, report_detail):
            st.success("🎉 บันทึกข้อมูลเรียบร้อย! ระบบกำลังสร้าง PDF ให้ใน Google Drive ครับ")
            st.balloons()
