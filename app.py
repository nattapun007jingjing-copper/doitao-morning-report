import streamlit as st
import datetime
import os
from PIL import Image
from io import BytesIO

# เรียกใช้ Library สำหรับสร้างไฟล์ PDF และจัดการฟอนต์ภาษาไทย
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="แบบบันทึกรายงานเวรเช้า - โรงเรียนดอยเต่าวิทยาคม", layout="centered")

# ฟังก์ชันสำหรับลงทะเบียนฟอนต์ภาษาไทย
def setup_thai_font():
    try:
        pdfmetrics.registerFont(TTFont('THSarabunNew', 'C:\\Windows\\Fonts\\THSarabunNew.ttf'))
        return 'THSarabunNew'
    except:
        try:
            pdfmetrics.registerFont(TTFont('Tahoma', 'C:\\Windows\\Fonts\\tahoma.ttf'))
            return 'Tahoma'
        except:
            return 'Helvetica'

# ฟังก์ชันสร้างไฟล์ PDF ในหน่วยความจำ (รองรับระบบออนไลน์)
def export_to_pdf_bytes(date_str, day_str, teacher_str, detail_str, image_files):
    font_name = setup_thai_font()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName=font_name, fontSize=20, leading=24, alignment=1, textColor=colors.HexColor('#990000'))
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName=font_name, fontSize=16, leading=20, alignment=1)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName=font_name, fontSize=14, leading=18, alignment=0)
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName=font_name, fontSize=14, leading=18, bold=True)
    
    if os.path.exists("logo.jpg"):
        story.append(RLImage("logo.jpg", width=70, height=70))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph("รายงานผลการปฏิบัติหน้าที่เวรประจำวันเช้า", title_style))
    story.append(Paragraph("โรงเรียนดอยเต่าวิทยาคม", subtitle_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(f"<b>วันที่บันทึกรายงาน:</b> {date_str} &nbsp;&nbsp;|&nbsp;&nbsp; <b>เวรประจำวัน:</b> วัน{day_str}", body_style))
    story.append(Paragraph(f"<b>ครูผู้รายงานเวร:</b> {teacher_str}", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<font color='#cccccc'>________________________________________________________________________________</font>", body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>รายละเอียดการปฏิบัติหน้าที่:</b>", bold_style))
    story.append(Spacer(1, 5))
    formatted_detail = detail_str.replace('\n', '<br/>')
    story.append(Paragraph(formatted_detail, body_style))
    story.append(Spacer(1, 15))
    
    if image_files:
        story.append(Paragraph("<b>ภาพประกอบการปฏิบัติหน้าที่:</b>", bold_style))
        story.append(Spacer(1, 10))
        for idx, img_file in enumerate(image_files):
            try:
                temp_img_path = f"temp_online_img_{idx}.jpg"
                img = Image.open(img_file)
                img.convert('RGB').save(temp_img_path, quality=50)
                story.append(RLImage(temp_img_path, width=220, height=150))
                story.append(Spacer(1, 10))
            except:
                pass
                
    story.append(Spacer(1, 30))
    sign_text = f"<br/><br/>ลงชื่อ........................................................ผู้รายงาน<br/>({teacher_str})"
    story.append(Paragraph(sign_text, ParagraphStyle('SignStyle', parent=body_style, alignment=2)))
    
    doc.build(story)
    
    if image_files:
        for idx in range(len(image_files)):
            if os.path.exists(f"temp_online_img_{idx}.jpg"):
                os.remove(f"temp_online_img_{idx}.jpg")
                
    buffer.seek(0)
    return buffer

# --- หน้าตาโปรแกรมหลัก ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.jpg"):
        st.image(Image.open("logo.jpg"), width=120)
    else:
        st.warning("⚠️ ไม่พบไฟล์ logo.jpg")

with col_title:
    st.title("โรงเรียนดอยเต่าวิทยาคม")
    st.subheader("📝 แบบบันทึกรายงานเวรเช้า (ระบบออนไลน์)")

st.markdown("---")

st.markdown("### 👤 ข้อมูลทั่วไป")
col1, col2 = st.columns(2)

with col1:
    teacher_list = ["-- เลือกชื่อครูผู้รายงาน --", "ครูชลธิดา", "ครูศิวิไล", "ครูวีระพงศ์", "ครูขนิญฐา", "ครูนงคราญ"]
    selected_teacher = st.selectbox("ชื่อครูผู้รายงานเวร", teacher_list)

with col2:
    day_list = ["-- เลือกวันประจำวัน --", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์"]
    selected_day = st.selectbox("เวรประจำวัน", day_list)

report_date = st.date_input("วันที่บันทึกรายงาน", datetime.date.today())

st.markdown("### 📋 รายละเอียดการปฏิบัติหน้าที่")
report_detail = st.text_area("รายงานเวร (บรรยายรายละเอียดการปฏิบัติหน้าที่)", height=200, placeholder="ระบุเหตุการณ์ พฤติกรรมนักเรียน หรือสิ่งที่พบเจอ...")

st.markdown("### 📸 ภาพประกอบ")
uploaded_files = st.file_uploader("เลือกรูปภาพเพื่อแสดงในรายงาน", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.markdown("#### 🖼️ ภาพที่อัปโหลดปัจจุบัน")
    img_cols = st.columns(3)
    for index, file in enumerate(uploaded_files):
        with img_cols[index % 3]:
            st.image(Image.open(file), use_container_width=True)

st.markdown("---")

# ส่วนของการกดประมวลผลข้อมูลและดาวน์โหลด
if st.button("⚙️ ประมวลผลและสร้างไฟล์ PDF รายงาน", type="primary", use_container_width=True):
    if selected_teacher == "-- เลือกชื่อครูผู้รายงาน --" or selected_day == "-- เลือกวันประจำวัน --" or not report_detail:
        st.error("❌ กรุณากรอกข้อมูลและเลือกตัวเลือกให้ครบถ้วนก่อน")
    else:
        # คำนวณชื่อไฟล์
        year_be = report_date.year + 543
        date_str = report_date.strftime(f'%d_%m_{year_be}')
        pdf_filename = f"รายงานเวรเช้า_{date_str}.pdf"
        
        # สร้าง PDF เก็บใน Memory
        pdf_data = export_to_pdf_bytes(
            date_str=report_date.strftime(f'%d/%m/{year_be}'),
            day_str=selected_day,
            teacher_str=selected_teacher,
            detail_str=report_detail,
            image_files=uploaded_files
        )
        
        st.success("🎉 ประมวลผลรายงานสำเร็จ! คุณครูสามารถกดดาวน์โหลดไฟล์ PDF ได้ที่ปุ่มด้านล่างนี้ครับ")
        
        # ปุ่มดาวน์โหลดที่จะเด้งขึ้นมาให้คุณครูกดเซฟลงเครื่องคอมหรือมือถือของตัวเอง
        st.download_button(
            label="📥 คลิกที่นี่เพื่อดาวน์โหลดไฟล์ PDF ลงเครื่องของคุณ",
            data=pdf_data,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True
        )