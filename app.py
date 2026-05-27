import streamlit as st
import datetime
import gspread
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
        # บันทึก 5 คอลัมน์: วันที่, ชื่อครู, วัน, รายละเอียด, ลิงก์ PDF
        worksheet.append_row([date_str, teacher_str, day_str, detail_str, pdf_link])
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

# ส่วนรับลิงก์ไฟล์ PDF (คุณครูสามารถอัปโหลดไฟล์ลง Drive แล้วก๊อปปี้ลิงก์มาวางได้เลยครับ)
pdf_link = st.text_input("วางลิงก์ไฟล์ PDF (ถ้ามี):", placeholder="https://drive.google.com/...")

# ปุ่มประมวลผล
if st.button("⚙️ ประมวลผลและส่งข้อมูลเข้าฐานข้อมูล", type="primary", use_container_width=True):
    if selected_teacher == "-- เลือกชื่อครูผู้รายงาน --" or selected_day == "-- เลือกวันประจำวัน --" or not report_detail:
        st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วนก่อนกดบันทึก")
    else:
        # บันทึกข้อมูล
        success = save_to_sheets(report_date.strftime('%d/%m/%Y'), selected_teacher, selected_day, report_detail, pdf_link)
        
        if success:
            st.success("🎉 บันทึกข้อมูลลงฐานข้อมูลส่วนกลางเรียบร้อย!")
            st.balloons()
