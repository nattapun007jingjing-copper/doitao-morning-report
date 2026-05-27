import streamlit as st
import datetime
import gspread
import os
from google.oauth2.service_account import Credentials

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="แบบบันทึกรายงานเวรเช้า", layout="centered")

# --- ฟังก์ชันบันทึก Sheets ---
def save_to_sheets(date_str, teacher_str, day_str, detail_str, pdf_link):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sh = client.open("database_morning_report")
        worksheet = sh.get_worksheet(0)
        # บันทึกข้อมูล 5 คอลัมน์
        worksheet.append_row([date_str, teacher_str, day_str, detail_str, pdf_link])
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึกลง Sheets: {e}")
        return False

# --- ส่วนหน้าจอหลัก ---
# แก้ไขชื่อไฟล์เป็น logo.jpg ตามที่ปรากฏใน GitHub ของคุณครูครับ
if os.path.exists("logo.jpg"):
    st.image("logo.jpg", width=150)

st.title("โรงเรียนดอยเต่าวิทยาคม")
st.subheader("📝 แบบบันทึกรายงานเวรเช้า (ระบบออนไลน์)")

# ฟอร์มกรอกข้อมูล
teacher_list = ["-- เลือกชื่อครูผู้รายงาน --", "ครูชลธิดา", "ครูศิวิไล", "ครูวีระพงศ์", "ครูขนิญฐา", "ครูนงคราญ"]
selected_teacher = st.selectbox("ชื่อครูผู้รายงานเวร", teacher_list)
selected_day = st.selectbox("เวรประจำวัน", ["-- เลือกวันประจำวัน --", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์"])
report_date = st.date_input("วันที่บันทึกรายงาน", datetime.date.today())
report_detail = st.text_area("รายงานเวร", height=200)

# ระบบอัปโหลดรูปภาพ
st.markdown("### 📸 ภาพประกอบ")
uploaded_files = st.file_uploader("เลือกรูปภาพเพื่อแสดงในรายงาน (ดูหน้าเว็บเท่านั้น)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    img_cols = st.columns(3)
    for index, file in enumerate(uploaded_files):
        with img_cols[index % 3]:
            st.image(file, use_container_width=True)

# ช่องใส่ลิงก์ PDF
pdf_link = st.text_input("วางลิงก์ไฟล์ PDF (อัปโหลดจาก Drive แล้วนำลิงก์มาวางที่นี่):", placeholder="https://drive.google.com/...")

# ปุ่มประมวลผล
if st.button("⚙️ ประมวลผลและส่งข้อมูลเข้าฐานข้อมูล", type="primary", use_container_width=True):
    if selected_teacher == "-- เลือกชื่อครูผู้รายงาน --" or selected_day == "-- เลือกวันประจำวัน --" or not report_detail:
        st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วนก่อนกดบันทึก")
    else:
        success = save_to_sheets(report_date.strftime('%d/%m/%Y'), selected_teacher, selected_day, report_detail, pdf_link)
        if success:
            st.success("🎉 บันทึกข้อมูลลงฐานข้อมูลส่วนกลางเรียบร้อย!")
            st.balloons()
