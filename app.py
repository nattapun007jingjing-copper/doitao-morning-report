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

# ส่วนเชื่อมต่อ Google Sheets
from google.oauth2.service_account import Credentials
import gspread

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="แบบบันทึกรายงานเวรเช้า", layout="centered")

# --- ฟังก์ชันเชื่อมต่อ Google Sheets ---
def save_to_sheets(date_str, teacher_str, day_str, detail_str):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        # ตรวจสอบชื่อไฟล์ให้ตรงกับใน Google Drive
        sh = client.open("database_morning_report")
        worksheet = sh.get_worksheet(0)
        worksheet.append_row([date_str, teacher_str, day_str, detail_str])
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึกลง Sheets: {e}")
        return False

# --- ฟังก์ชันสร้างฟอนต์และ PDF (เหมือนเดิมของคุณครู) ---
def setup_thai_font():
    try:
        # สำหรับบน Streamlit Cloud ให้ใช้ฟอนต์ที่โหลดมาในโฟลเดอร์โปรเจกต์
        pdfmetrics.registerFont(TTFont('THSarabunNew', 'THSarabunNew.ttf'))
        return 'THSarabunNew'
    except:
        return 'Helvetica'

def export_to_pdf_bytes(date_str, day_str, teacher_str, detail_str, image_files):
    font_name = setup_thai_font()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName=font_name, fontSize=20, leading=24, alignment=1, textColor=colors.HexColor('#990000'))
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName=font_name, fontSize=14, leading=18, alignment=0)
    
    story.append(Paragraph("รายงานผลการปฏิบัติหน้าที่เวรประจำวันเช้า", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"<b>วันที่:</b> {date_str}  <b>เวรวัน:</b> {day_str}", body_style))
    story.append(Paragraph(f"<b>ครูผู้รายงาน:</b> {teacher_str}", body_style))
    story.append(Paragraph(f"<b>รายละเอียด:</b> {detail_str}", body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- ส่วนหน้าจอหลัก ---
st.title("โรงเรียนดอยเต่าวิทยาคม")
st.subheader("📝 แบบบันทึกรายงานเวรเช้า (ระบบออนไลน์)")

teacher_list = ["-- เลือกชื่อครูผู้รายงาน --", "ครูชลธิดา", "ครูศิวิไล", "ครูวีระพงศ์", "ครูขนิญฐา", "ครูนงคราญ"]
selected_teacher = st.selectbox("ชื่อครูผู้รายงานเวร", teacher_list)
selected_day = st.selectbox("เวรประจำวัน", ["-- เลือกวันประจำวัน --", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์"])
report_date = st.date_input("วันที่บันทึกรายงาน", datetime.date.today())
report_detail = st.text_area("รายงานเวร", height=200)

if st.button("⚙️ ประมวลผลและส่งข้อมูลเข้าฐานข้อมูล", type="primary", use_container_width=True):
    if selected_teacher == "-- เลือกชื่อครูผู้รายงาน --" or selected_day == "-- เลือกวันประจำวัน --" or not report_detail:
        st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
    else:
        # 1. บันทึกลง Google Sheets
        success = save_to_sheets(report_date.strftime('%d/%m/%Y'), selected_teacher, selected_day, report_detail)
        
        # 2. สร้าง PDF (เก็บใน Memory)
        pdf_data = export_to_pdf_bytes(report_date.strftime('%d/%m/%Y'), selected_day, selected_teacher, report_detail, [])
        
        if success:
            st.success("🎉 บันทึกข้อมูลลงฐานข้อมูลส่วนกลางเรียบร้อย!")
            st.download_button("📥 ดาวน์โหลดไฟล์ PDF", data=pdf_data, file_name=f"report_{selected_teacher}.pdf", mime="application/pdf")
