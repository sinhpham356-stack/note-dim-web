import streamlit as st
from PIL import Image, ImageDraw
import io
from pptx import Presentation
from pptx.util import Inches

st.set_page_config(page_title="Note-Dim Web V10", layout="wide")

# Khởi tạo bộ nhớ tạm cho các trang slide
if 'project_slides' not in st.session_state:
    st.session_state.project_slides = []

def create_pdf(images):
    buf = io.BytesIO()
    if images:
        rgb_images = [img.convert('RGB') for img in images]
        rgb_images[0].save(buf, format='PDF', save_all=True, append_images=rgb_images[1:])
    buf.seek(0)
    return buf.getvalue()

def create_pptx(images):
    prs = Presentation()
    for img in images:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        slide.shapes.add_picture(img_io, Inches(0), Inches(0), width=prs.slide_width)
    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.getvalue()

# Giao diện Sidebar quản lý danh sách slide
with st.sidebar:
    st.header("📑 Danh sách Trang (Slide)")
    st.write(f"Đã lưu: **{len(st.session_state.project_slides)}** trang")
    
    if len(st.session_state.project_slides) > 0:
        for i, img in enumerate(st.session_state.project_slides):
            st.image(img, caption=f"Trang {i+1}", use_container_width=True)
            
        st.write("---")
        st.subheader("📥 Xuất Dự Án")
        st.download_button(
            label="📄 Tải xuống file PDF",
            data=create_pdf(st.session_state.project_slides),
            file_name="Du_An_Note_Dim.pdf",
            mime="application/pdf"
        )
        st.download_button(
            label="📊 Tải xuống file PowerPoint",
            data=create_pptx(st.session_state.project_slides),
            file_name="Du_An_Note_Dim.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        if st.button("🗑️ Xóa toàn bộ dự án"):
            st.session_state.project_slides = []
            st.rerun()

st.title("📏 Công cụ Note-Dim (Phiên bản Web ổn định)")
st.markdown("Tải ảnh lên, thêm ghi chú nhanh và gom vào danh sách để xuất file PDF/PPTX hàng loạt.")

uploaded_file = st.file_uploader("📂 Tải ảnh lên", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    st.write("---")
    st.subheader("✍️ Thêm ghi chú văn bản lên ảnh")
    
    col1, col2 = st.columns(2)
    with col1:
        note_text = st.text_input("Nhập nội dung ghi chú/thông số:")
        text_x = st.slider("Vị trí ngang (X theo % ảnh)", 0, 100, 50)
        text_y = st.slider("Vị trí dọc (Y theo % ảnh)", 0, 100, 50)
    with col2:
        font_size = st.slider("Cỡ chữ:", 10, 100, 30)
        # Tạo bản vẽ có chứa chữ người dùng nhập
        edited_image = image.copy()
        draw = ImageDraw.Draw(edited_image)
        if note_text:
            # Tính toán tọa độ thực tế trên ảnh
            real_x = int(image.width * (text_x / 100))
            real_y = int(image.height * (text_y / 100))
            draw.text((real_x, real_y), note_text, fill=(255, 0, 0)) # Chữ màu đỏ nổi bật

    st.write("### 🖼️ Xem trước kết quả")
    st.image(edited_image, use_container_width=True)

    st.write("---")
    if st.button("➕ Thêm trang này vào Dự Án", type="primary"):
        st.session_state.project_slides.append(edited_image)
        st.success(f"Đã thêm vào danh sách! Tổng số trang: {len(st.session_state.project_slides)}")
        st.rerun()
